'''
Name:   Jasper Wong
Date:   11-10-2020
Source: CS 493 W02-W05 HW, Google Cloud Platform docs

'''
from google.cloud import datastore
from flask import Flask, request, render_template
import json
import constants
import boat

app = Flask(__name__)
# register blueprints on application
app.register_blueprint(boat.bp)

client = datastore.Client()

@app.route('/')
def index():
    # return "Please navigate to /boats and /loads to use this API"
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)