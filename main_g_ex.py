import json

import flask
import requests


app = flask.Flask(__name__)

CLIENT_ID = '823710541896-sq5est11004asi1qbu3d5ehc7954hnrq.apps.googleusercontent.com'
# your_client_id = '823710541896-sq5est11004asi1qbu3d5ehc7954hnrq.apps.googleusercontent.com'
CLIENT_SECRET = 'odswOXW_inMxoJnXV_pZxLzp'  # Read from a file or environmental variable in a real app
SCOPE = 'https://www.googleapis.com/auth/drive.metadata.readonly'
# REDIRECT_URI = 'http://127.0.0.1:5000'
# REDIRECT_URI = 'http://127.0.0.1:5000/oauth2callback'
REDIRECT_URI = 'http://127.0.0.1:8080/oauth2callback'
# REDIRECT_URI = 'https://hw06-wongjasp.wl.r.appspot.com/oauth2callback'
# REDIRECT_URI = 'https://hw06-wongjasp.wl.r.appspot.com'

@app.route('/')
def index():
  if 'credentials' not in flask.session:
    return flask.redirect(flask.url_for('oauth2callback'))
  credentials = json.loads(flask.session['credentials'])
  if credentials['expires_in'] <= 0:
    return flask.redirect(flask.url_for('oauth2callback'))
  else:
    headers = {'Authorization': 'Bearer {}'.format(credentials['access_token'])}
    req_uri = 'https://www.googleapis.com/drive/v2/files'
    r = requests.get(req_uri, headers=headers)
    return r.text
    # return render_template('index.html')


@app.route('/oauth2callback')
def oauth2callback():
  if 'code' not in flask.request.args:
    auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                '&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPE)
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    data = {'code': auth_code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'}
    r = requests.post('https://oauth2.googleapis.com/token', data=data)
    flask.session['credentials'] = r.text
    return flask.redirect(flask.url_for('index'))
    # return render_template('index.html')
    # return "Test Test"


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = False
  app.run(host='127.0.0.1', port=8080, debug=True) #change credentials to port 8080
  