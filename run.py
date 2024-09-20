from flask import Flask, request, jsonify
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil import parser
from flask_cors import CORS


def to_utc(datetime_str):
    local_dt = parser.parse(datetime_str)
    utc_dt = local_dt - local_dt.utcoffset()
    return utc_dt.replace(tzinfo=None)

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
CORS(app) 
db = client.techstax  # techstax is the database name
events = db.events    # events is the collection name

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers['Content-Type'] == 'application/json':
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')
        event_action = data.get('action')
        print("event_type: ", event_type)
        print("event_action: ", event_action)
        
        if event_type == 'push':
            utc_timestamp = to_utc(data['head_commit']['timestamp'])
            doc = {
                'request_id': data['after'],
                'author': data['head_commit']['author']['name'],
                'action': event_type,
                'from_branch': data['ref'].split('/')[-1],
                'to_branch': data['ref'].split('/')[-1],
                'timestamp': utc_timestamp,
                'status': 'closed'
            }
            events.insert_one(doc)  # Inserting document into MongoDB

        elif event_type == 'pull_request':
            pr_data = data['pull_request']
            utc_timestamp = to_utc(pr_data['created_at'])
            doc = {
                'request_id': pr_data['id'],
                'author': pr_data['user']['login'],
                'action': event_type,
                'from_branch': pr_data['head']['ref'],
                'to_branch': pr_data['base']['ref'],
                'timestamp': utc_timestamp,
                'status': event_action
            }
            events.insert_one(doc)  # Inserting document into MongoDB

        return jsonify({'status': 'success', 'data': data}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid content type'}), 415

@app.route('/events', methods=['GET'])
def get_events():
    # Get the latest timestamp from the query params, default to 0 if not present
    last_fetched = request.args.get('timestamp')
    if last_fetched == "" :
        last_fetched = "1970-01-01T00:00:00.00Z"

    
    # Convert string timestamp to datetime object
    # last_fetched_dt = datetime.strptime(last_fetched, '%Y-%m-%dT%H:%M:%SZ')
    last_fetched_dt = to_utc(last_fetched)
    
    # Fetch new events added after the last_fetched timestamp
    new_events = list(events.find({'timestamp': {'$gt': last_fetched_dt}}, {'_id': False}))
    
    return jsonify(new_events)

@app.route('/', methods=['GET'])
def landing():
    return "Hey buddy, the server is up"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
