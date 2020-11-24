'''
Name:   Jasper Wong
Date:   11-18-2020
Source: Everything from CS 493 and Google Docs
'''

from google.cloud import datastore
from flask import Flask, request, render_template
from requests_oauthlib import OAuth2Session
import json
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests

# files for constants and boat routes by blueprint
import constants
import boat
import owner
import client_info
import load

# # This disables the requirement to use HTTPS so that you can test locally.
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
client = datastore.Client()

# register blueprints on application
app.register_blueprint(boat.bp)
app.register_blueprint(owner.bp)
app.register_blueprint(load.bp)

# These should be copied from an OAuth2 Credential section at
# https://console.cloud.google.com/apis/credentials
# <--Make more secret later!
client_id = r'153129745149-jn0an4tjr2t7nslud3qm51th2e5087ma.apps.googleusercontent.com'
client_secret = r'YgnCx3xxywKGPN7hjPF9Km1A'

# This is the page that you will use to decode and collect the info from
# the Google authentication flow
redirect_uri = 'http://127.0.0.1:8080/oauth' # for local only
# redirect_uri = 'https://hw07-wongjasp.wl.r.appspot.com/oauth'

# These let us get basic info to identify a user and not much else
# they are part of the Google People API
scope = ['https://www.googleapis.com/auth/userinfo.email',
             'https://www.googleapis.com/auth/userinfo.profile', 'openid']
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)

# This link will redirect users to begin the OAuth flow with Google
@app.route('/')
def index():
    authorization_url, state = oauth.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        # access_type and prompt are Google specific extra parameters.
        access_type="offline", prompt="select_account")
    return render_template('index.html', authorization_url = authorization_url)

# This is where users will be redirected back to and where you can collect
# the JWT for use in future requests
@app.route('/oauth')
def oauthroute():
    token = oauth.fetch_token(
        'https://accounts.google.com/o/oauth2/token',
        authorization_response=request.url,
        client_secret=client_secret)
    req = requests.Request()

    id_info = id_token.verify_oauth2_token( 
    token['id_token'], req, client_id)
    
    # print(token['id_token'])
    # print(id_info)

    # return "Your JWT is: %s" % token['id_token']
    return render_template('user-info.html', JWT = token['id_token'], USER_EMAIL = id_info.get('email'), USER_ID = id_info.get('sub'))

# This page demonstrates verifying a JWT. id_info['email'] contains
# the user's email address and can be used to identify them
# this is the code that could prefix any API call that needs to be
# tied to a specific user by checking that the email in the verified
# JWT matches the email associated to the resource being accessed.
@app.route('/verify-jwt') # <-- Postman, params --> key: jwt, value: the is jwt value
def verify():
    req = requests.Request()

    id_info = id_token.verify_oauth2_token( 
    request.args['jwt'], req, client_id)

    return repr(id_info) + "<br><br> the user is: " + id_info['sub']


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)