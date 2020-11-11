'''
Name:   Jasper Wong
Date:   11-10-2020
Source: CS 493 W02-W05 HW, Google Cloud Platform docs and examples

'''
import json
import flask
from flask import render_template
import requests

# for client info constants
import client_info

app = flask.Flask(__name__)

# when launched to GAE, comment out for local (creates unique user id)
import uuid
app.secret_key = str(uuid.uuid4())

@app.route('/')
def index():
  return render_template('index.html')


# @app.route('/')
# def index():
@app.route('/cred')
def index_cred():
  if 'credentials' not in flask.session:
    # print("1. No credentials, getting it!") # <-----
    return flask.redirect(flask.url_for('oauth'))
  credentials = json.loads(flask.session['credentials'])
  if credentials['expires_in'] <= 0:
    return flask.redirect(flask.url_for('oauth'))
  else:
    # print("8. Back in index after getting access token from POST") # <----
    headers = {'Authorization': 'Bearer {}'.format(credentials['access_token'])}
    req_uri = 'https://people.googleapis.com/v1/people/me?personFields=names'
    # print("9. perform get request and assigning content to r var") # <----- GET REQUEST
    r = requests.get(req_uri, headers=headers)

    res_test = json.loads(r.text) # JSON string to Python dict

    print(res_test["names"][0]["familyName"])
    print(res_test["names"][0]["givenName"].split(' ', 1)[0])
    familyName = res_test["names"][0]["familyName"]
    givenName = res_test["names"][0]["givenName"].split(' ', 1)[0]

    # flask.session["state"] = str(uuid.uuid4()) # comment out when deploying to GCP, only use for testing local
    return render_template('user-info.html', familyName = familyName, givenName = givenName, stateVal = flask.session["state"])


@app.route('/oauth')
def oauth():
  if 'code' not in flask.request.args:
    # print("2. In /oauth, No code in flask request arguments, initial redirect to get code to be able to get access token") # <----
    # print("2-1. Generate random alpha and num for state") # <---
    flask.session['state'] = str(uuid.uuid4()) # gen random string for state track
    print(flask.session['state']) # yes you can just call session object
    auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                '&client_id={}&redirect_uri={}&scope={}&state={}').format(client_info.CLIENT_ID, client_info.REDIRECT_URI, client_info.SCOPE, flask.session['state'])
    # print("3. In /oauth, About to send initial redirect") # <--
    return flask.redirect(auth_uri) # <------- takes me to page to choose account
  else:
    # print("4. Arrived here after account choosen, In /oauth, After initial redirect to get auth code, onward to POST to server to get access token")
    state_info = flask.request.args.get("state")
    # print(type(state_info))
    print(flask.session['state']) # <--- does not work locally, will break. Only works on GCP.
   
    # Ensure that the request is not a forgery and that the user sending, 
    # this connect request is the expected user. source: google doc OpenID Connect
    # comment out when working locally since session does not persist for some reason
    if state_info != flask.session['state']:
      response = make_response(json.dumps('Invalid state parameter.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

    auth_code = flask.request.args.get('code')
    
    data = {'code': auth_code,
            'client_id': client_info.CLIENT_ID,
            'client_secret': client_info.CLIENT_SECRET,
            'redirect_uri': client_info.REDIRECT_URI,
            'grant_type': 'authorization_code'}
    
    # have to comment out r = ... when following oauth 2.0 demo and postman exercise
    # r = ... is POST to get access token. When using log to get the token, invalid_grant error because the token
    # has been used. that is my hypothesis.
    r = requests.post('https://oauth2.googleapis.com/token', data=data) # test <------------ POST portion of demo to get access token
    # print("5. In /oauth, sent post with code authorization to get access token")
    flask.session['credentials'] = r.text
    # print("6. In /oauth, added context of response from post to credentials with sessions")
    print("7. redirecting to / endpoint")
    return flask.redirect(flask.url_for('index_cred'))


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = False
  app.run(host='127.0.0.1', port=8080, debug=True) #change credentials to port 8080
  