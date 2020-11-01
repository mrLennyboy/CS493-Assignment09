'''
Name:   Jasper Wong
Date:   10-30-2020`
Source: CS 493 W03 & W02 HW, CS CS 493 W04, Google Cloud Platform docs

'''
from google.cloud import datastore
from flask import Flask, request
import json
import constants
import boat

app = Flask(__name__)
# register blueprints on application
app.register_blueprint(boat.bp)

client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /boats and /loads to use this API"\

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)