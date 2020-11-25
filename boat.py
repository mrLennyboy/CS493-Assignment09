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

# files for constants and boat routes by blueprint
# import constants
# import boat
# import owner
import client_info

# Python Blueprint template that creates Blueprint named 'boat', 2nd par __name__ the blueprint
# know where it's defined, url_prefix will prepend to all URLs associated with the blueprint.
bp = Blueprint('boat', __name__, url_prefix='/boats')

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

# def sub_return_status(sub_info): # <--figure out why not working
#     if sub_info == "Error: No Authorization in request header":
#         res = make_response({"Error": "No Authorization in request header"})
#         res.mimetype = 'application/json'
#         res.status_code = 401
#         return res
#     elif sub_info == "Error: JWT is invalid":
#         res = make_response({"Error": "JWT is invalid"})
#         res.mimetype = 'application/json'
#         res.status_code = 401
#         return res
#     else:
#         pass


@bp.route('', methods=['POST','GET'])
def boats_post_get():
    if request.method == 'POST':
        # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes:
            # check if request is json
            if not request.is_json:
                # return simple status code for unsupported media type (want JSON)
                res = make_response(json.dumps(constants.error_unsupported_media_type))
                res.mimetype = 'application/json'
                res.status_code = 415
                return res

            # get request json
            content = request.get_json()

            #owner of the boat, value of sub property in the JWT
            owner_sub = get_sub_info()

            #rush job error check for getting owner sub info
            # sub_return_status(owner_sub) # <--figure out later if I have time, return not kicking out
            if owner_sub == "Error: No Authorization in request header":
                res = make_response({"Error": "No Authorization in request header"})
                res.mimetype = 'application/json'
                res.status_code = 401
                return res
            elif owner_sub == "Error: JWT is invalid":
                res = make_response({"Error": "JWT is invalid"})
                res.mimetype = 'application/json'
                res.status_code = 401
                return res

            # print("The sub is: " + owner_sub)

            # using comparison operator for key value check, True if all keys present
            if not (content.keys()) >= constants.check_keys:
                res = make_response(json.dumps(constants.error_miss_attribute))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # start of input validation
            # check boat name length and value type
            if type(content["name"]) != str: 
                res = make_response(json.dumps(constants.error_boat_name_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
 
            if len(content["name"]) > 33:
                res = make_response(json.dumps(constants.error_boat_name_length))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # boat name passes earlier type and length then check if all alpha or space
            # if string not all alpha or space then return error
            if not all(letter.isalpha() or letter.isspace() for letter in content["name"]):
                res = make_response(json.dumps(constants.error_boat_name_invalid))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # check boat type data type and length
            if type(content["type"]) != str: 
                res = make_response(json.dumps(constants.error_boat_type_str))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            if len(content["type"]) > 33:
                res = make_response(json.dumps(constants.error_boat_type_length))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # boat type passes earlier type and length then check if all alpha or space
            # if string not all alpha or space then return error
            if not all(letter.isalpha() or letter.isspace() for letter in content["type"]):
                res = make_response(json.dumps(constants.error_boat_type_invalid))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # check length data type and have int value below 10,000ft, largest ship around 1,500 ft
            if type(content["length"]) != int:
                res = make_response(json.dumps(constants.error_boat_length_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            if content["length"] > 10000 or content["length"] < 0:
                res = make_response(json.dumps(constants.error_boat_length_limit))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # input validation, check boat name if unique or not <-----
            query = client.query(kind=constants.boats)
            results = list(query.fetch())
            print(results)
            # if results: # if list is empty then false
            for e in results:
                # if the boat name is already assigned to a boat then return 403 and error
                if e["name"] == content["name"]:
                    res = make_response(json.dumps(constants.error_boat_name_exists))
                    res.mimetype = 'application/json'
                    res.status_code = 403
                    return res

            # create datastore entity
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))

            # Update new entity with content data
            new_boat.update({"name": content["name"], "type": content["type"],
            "length": content["length"], "public": content["public"],
            "owner": owner_sub})
            # put new entity to datastore
            client.put(new_boat)
            
            # build self_url from request info and new new_boat entity key id
            self_url = str(request.base_url) + '/' + str(new_boat.key.id)
            # update new_boat json with id and self url
            new_boat.update({"id": str(new_boat.key.id), "self": self_url})
            # setting status code and content-type type with make_response function
            res = make_response(json.dumps(new_boat))
            res.mimetype = 'application/json'
            res.status_code = 201
            return res

        else: #else statement for request.accept_mimetype text/html type
            # return "This client doesn't accept application/json" as text/html
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res


    elif request.method == 'GET':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # bool val if owner_sub is valid or not
        owner_sub_valid = get_sub_valid(owner_sub)

        # print("The sub is: " + owner_sub)
        # query data store for boats
        query = client.query(kind=constants.boats)
        results = list(query.fetch())

        # If no JWT is provided or an invalid JWT is provided,
        # return all public boats and 200 status code
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
                if e.get("public") == True:
                    results_filtered.append(e)
        # elif valid_sub == True:
        elif owner_sub_valid == True:
            for e in results:
                e["id"] = str(e.key.id)
                # build self_url from request info and boat entity key id
                self_url = str(request.base_url) + '/' + str(e.key.id)
                # update new_boat json with id and self url
                e.update({"self": self_url})
                # slow method to add to add only owner boats
                if e.get("owner") == owner_sub:
                    results_filtered.append(e)
        
        results = results_filtered
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

@bp.route('/<boat_id>', methods=['DELETE'])
def boats_delete(boat_id):
    if request.method =='DELETE':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # rush job error check for getting owner sub info
        # sub_return_status(owner_sub) # <--figure out later if I have time, return not kicking out
        if owner_sub == "Error: No Authorization in request header":
            res = make_response({"Error": "No Authorization in request header"})
            res.mimetype = 'application/json'
            res.status_code = 401
            return res
        elif owner_sub == "Error: JWT is invalid":
            res = make_response({"Error": "JWT is invalid"})
            res.mimetype = 'application/json'
            res.status_code = 401
            return res

        # rush job error check v2 for route spec. <-- not necessary
        owner_sub_valid = get_sub_valid(owner_sub)

        boat_key = client.key(constants.boats, int(boat_id))
        # get boat entity with the key requested
        boats = client.get(key=boat_key)

        # if boat entity is nonetype (id doesn't exist) return error message and status code
        if boats is None:
            res = make_response(json.dumps({"Error": "Boat with this id does not exist"}))
            res.mimetype = 'application/json'
            res.status_code = 403
            return res

        # compare boat ownership id's
        # owner sub and boat owned by someone else
        if owner_sub != boats.get("owner"):
            res = make_response(json.dumps({"Error": "Boat owner ID does not match"}))
            res.mimetype = 'application/json'
            res.status_code = 403
            return res

        client.delete(boat_key)
        return ('', 204) # for delete no return body

    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res
