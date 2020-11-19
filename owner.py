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

def get_sub_info():
        # get sub info from JWT, owner of boat
    if 'Authorization' in request.headers:
        user_jwt = request.headers['Authorization']
        user_jwt = user_jwt.replace("Bearer ", "")
        req = requests.Request()

        try:
            id_info = id_token.verify_oauth2_token( 
                user_jwt, req, client_info.CLIENT_ID)
            user_sub = id_info['sub']
            return user_sub
        except:
            return "Error: JWT is invalid"
    else:
        return "Error: No Authorization in request header"

def get_sub_valid(sub_info):
    if sub_info == "Error: No Authorization in request header":
        return False
    elif sub_info == "Error: JWT is invalid":
        return False
    else:
        return True

@bp.route('/<owner_id>/boats', methods=['GET'])
def boats_get_delete_patch_put(owner_id):
    if request.method == 'GET':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # bool val if owner_sub is valid or not
        owner_sub_valid = get_sub_valid(owner_sub)

        # query data store for boats
        query = client.query(kind=constants.boats)
        results = list(query.fetch())

        # If no JWT is provided or an invalid JWT is provided,
        # return all public boats that belong to owner and 200 status code
        results_filtered=[]
        # if valid_sub == False:
        if owner_sub_valid == False:
            for e in results:
                e["id"] = str(e.key.id)
                # build self_url from request info and boat entity key id
                self_url = str(request.base_url) + '/' + str(e.key.id)
                # update new_boat json with id and self url
                e.update({"self": self_url})
                # slow method to add all public boats
                if e.get("public") == True and e.get("owner") == owner_id:
                    results_filtered.append(e)
        # elif valid_sub == True:
        elif owner_sub_valid == True and owner_id == owner_sub:
            for e in results:
                e["id"] = str(e.key.id)
                # build self_url from request info and boat entity key id
                self_url = str(request.base_url) + '/' + str(e.key.id)
                # update new_boat json with id and self url
                e.update({"self": self_url})
                # slow method to add to add only owner boats
                if e.get("owner") == owner_id and e.get("public") == True:
                    results_filtered.append(e)
        
        results = results_filtered
        # in python empty list eval to false
        if not results:
            res = make_response({"Error": "This boat owner has no public boats available"})
            res.mimetype = 'application/json'
            res.status_code = 200
            return res
        # setting status code and content-type type with make_response function
        res = make_response(json.dumps(results))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res

    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res
