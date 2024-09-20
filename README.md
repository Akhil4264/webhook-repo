# Dev Assessment - Webhook Receiver

*******************

## Setup

* Create a new virtual environment

```bash
pip install virtualenv
```

* Create the virtual env

```bash
virtualenv venv
```

* Activate the virtual env

```bash
source venv/bin/activate
```

* Install requirements

```bash
pip install -r requirements.txt
```

* Run the flask application

```bash
python run.py
```

* The endpoint is at:

```bash
POST http://127.0.0.1:5000/webhook/

```
* Install ngrok and tunnel localhost to a https link and add the link in the webhook payload URL


open the index.html in google chrome (or any browser of your choice)

*******************