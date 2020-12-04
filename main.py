'''
Name:   Jasper Wong
Date:   11-18-2020
Source: Everything from CS 493 and Google Docs
'''

from google.cloud import datastore
from flask import Flask, request, render_template, make_response
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
client_id = client_info.CLIENT_ID
client_secret = client_info.CLIENT_SECRET

# This is the page that you will use to decode and collect the info from
# the Google authentication flow
redirect_uri = client_info.REDIRECT_URI

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

    id_info = id_token.verify_oauth2_token(token['id_token'], req, client_id)

    # input validation, check reg user id unique or not. Have to go through datastore entities list, can't use user_id as key check.
    query = client.query(kind=constants.reg_users)
    results = list(query.fetch())
    match_count = 0
    for e in results:
        # if the user id is already assigned to registered user then ignore
        if e["user_id"] == id_info.get('sub'):
            match_count += 1
            break
    if match_count == 0:
        # create datastore entity to add to users endpoint
        new_reg_users = datastore.entity.Entity(key=client.key(constants.reg_users))
        # Update new entity with content data
        new_reg_users.update({"user_email": id_info.get("email"), "user_id": id_info.get('sub')})
        # put new entity to datastore
        client.put(new_reg_users)

    return render_template('user-info.html', JWT = token['id_token'], USER_EMAIL = id_info.get('email'), USER_ID = id_info.get('sub'))

# This page demonstrates verifying a JWT. id_info['email'] contains
# the user's email address and can be used to identify them
# this is the code that could prefix any API call that needs to be
# tied to a specific user by checking that the email in the verified
# JWT matches the email associated to the resource being accessed.
@app.route('/verify-jwt') # <-- Postman, params --> key: jwt, value: the is jwt value, need to be json response <-----
def verify():
    req = requests.Request()

    id_info = id_token.verify_oauth2_token( 
    request.args['jwt'], req, client_id)

    res = make_response(json.dumps(id_info))
    res.mimetype = 'application/json'
    res.status_code = 200
    return res

# # Unprotected Endpoint that returns all users currently "registered" with the app in datastore
@app.route('/users', methods=['GET'])
def registered_user():
    if request.method == 'GET':
        query = client.query(kind=constants.reg_users)
        results = list(query.fetch())
        user_list = []
        for e in results:
            user_list.append(e)
        res = make_response(json.dumps(user_list))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res

    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)