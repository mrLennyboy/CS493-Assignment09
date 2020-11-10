import json

import flask
from flask import render_template
import requests

# for client info constants
import client_info

app = flask.Flask(__name__)

# when launched to GAE, comment out for local
import uuid
app.secret_key = str(uuid.uuid4())

# add state generator

# @app.route('/')
# def index():
#   return render_template('index2.html')

@app.route('/')
def index():
  if 'credentials' not in flask.session:
    print("1. No credentials, getting it!") # <-----
    return flask.redirect(flask.url_for('oauth'))
  credentials = json.loads(flask.session['credentials'])
  if credentials['expires_in'] <= 0:
    return flask.redirect(flask.url_for('oauth'))
  else:
    print("8. Back in index after getting access token from POST") # <----
    headers = {'Authorization': 'Bearer {}'.format(credentials['access_token'])}
    # get credentials since GAE log doesn't show local
    # print("access_token: " + credentials['access_token'])
    req_uri = 'https://people.googleapis.com/v1/people/me?personFields=names'
    print("9. perform get request and assigning content to r var")
    r = requests.get(req_uri, headers=headers)
    # return r.text
    return render_template('index2.html', user_info = r.text)


@app.route('/oauth')
def oauth():
  if 'code' not in flask.request.args:
    print("2. In /oauth, No code in flask request arguments, initial redirect to get code to be able to get access token") # <----
    auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                '&client_id={}&redirect_uri={}&scope={}').format(client_info.CLIENT_ID, client_info.REDIRECT_URI, client_info.SCOPE)
    print("3. In /oauth, About to send initial redirect") # <--
    return flask.redirect(auth_uri)
  else:
    print("4. In /oauth, After initial redirect to get auth code, onward to POST to server to get access token")
    auth_code = flask.request.args.get('code')
    # print("code: " + auth_code)
    # print('client_id: ' + CLIENT_ID)
    # print('client_secret: ' + CLIENT_SECRET)
    # print('redirect_uri: ' + REDIRECT_URI)
    
    data = {'code': auth_code,
            'client_id': client_info.CLIENT_ID,
            'client_secret': client_info.CLIENT_SECRET,
            'redirect_uri': client_info.REDIRECT_URI,
            'grant_type': 'authorization_code'}
    
    # have to comment out r = ... when following oauth 2.0 demo and postman exercise
    # r = ... is POST to get access token. When using log to get the token, invalid_grant error because the token
    # has been used. that is my hypothesis.
    r = requests.post('https://oauth2.googleapis.com/token', data=data) #test
    print("5. In /oauth, sent post with code authorization to get access token")
    flask.session['credentials'] = r.text
    print("6. In /oauth, added context of response from post to credentials with sessions")
    print("7. redirecting to / endpoint")
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = False
  app.run(host='127.0.0.1', port=8080, debug=True) #change credentials to port 8080
  