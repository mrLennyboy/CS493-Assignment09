from google.cloud import datastore
from flask import Flask, request, Blueprint, make_response
import json
import constants
from json2html import *

import requests
from google.oauth2 import id_token

from requests_oauthlib import OAuth2Session
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests

client = datastore.Client()

import client_info

# Python Blueprint template that creates Blueprint named 'boat', 2nd par __name__ the blueprint
# know where it's defined, url_prefix will prepend to all URLs associated with the blueprint.
bp = Blueprint('owner', __name__, url_prefix='/owners')

@bp.route('/<owner_id>/boats', methods=['GET'])
def boats_get_delete_patch_put(boat_id):
    if request.method == 'GET':
        # Postman base accept */*, will send perferred accept of JSON
        # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes:
            boat_key = client.key(constants.boats, int(boat_id))
            boats = client.get(key=boat_key)
            # if boats entity is nonetype return error message and status code
            if boats is None:
                res = make_response(json.dumps(constants.error_miss_bID))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res
                # return (json.dumps(constants.error_miss_bID), 404)

            self_url = str(request.base_url)
            boats.update({"id": str(boats.key.id), "self": self_url})

            # setting status code and content-type type with make_response function
            res = make_response(json.dumps(boats))
            res.mimetype = 'application/json'
            res.status_code = 200
            return res

        # check to see if text/html is listed in Accept header
        elif 'text/html' in request.accept_mimetypes:
            boat_key = client.key(constants.boats, int(boat_id))
            boats = client.get(key=boat_key)
            # if boats entity is nonetype return error message and status code
            if boats is None:
                res = make_response(json.dumps(constants.error_miss_bID))
                res.mimetype = 'text/html'
                res.status_code = 404
                return res
                # return (json.dumps(constants.error_miss_bID), 404)

            self_url = str(request.base_url)
            boats.update({"id": str(boats.key.id), "self": self_url})

            # source w05 lectures setting headers and json2html module
            res = make_response(json2html.convert(json=json.dumps(boats)))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 200
            return res

        else: #else statement for request.accept_mimetype
            # return "This client doesn't accept application/json" leave as text/html
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res
            # return (json.dumps(constants.error_unsupported_accept_type), 406)

    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res