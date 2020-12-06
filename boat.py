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

# For GET all boats, bool val if owner_sub is valid or not. If no JWT is provided 
# or an invalid JWT is provided, return all public boats and 200 status code
def get_sub_valid(sub_info):
    if sub_info == "Error: No Authorization in request header":
        return False
    elif sub_info == "Error: JWT is invalid":
        return False
    else:
        return True

# error check for getting owner sub info
def sub_return_status(sub_info):
    if sub_info == "Error: No Authorization in request header":
        res = make_response({"Error": "No Authorization in request header"})
        res.mimetype = 'application/json'
        res.status_code = 401
        return res
    elif sub_info == "Error: JWT is invalid":
        res = make_response({"Error": "JWT is invalid"})
        res.mimetype = 'application/json'
        res.status_code = 401
        return res
    else:
        pass

@bp.route('', methods=['POST','GET'])
def boats_post_get():
    if request.method == 'POST':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # error check for getting owner sub info
        res_auth_jwt = sub_return_status(owner_sub)
        if res_auth_jwt:
            return res_auth_jwt

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

            # Update new entity with content data, empty load explicit defined
            new_boat.update({"name": content["name"], "type": content["type"],
            "length": content["length"], "public": content["public"],
            "owner": owner_sub, "loads": []})
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
            
        if 'application/json' in request.accept_mimetypes:
            # query data store for boats
            query = client.query(kind=constants.boats)

            # # If no JWT is provided or an invalid JWT is provided,
            # # return all public boats and 200 status code
            if owner_sub_valid == True:
                query.add_filter("owner", "=", owner_sub)
            else:
                query.add_filter("public", "=", True)
            
            # number of total items that are in the collection from filtered or non-filtered query
            content_length = len(list(query.fetch()))

            # pull limit and offset from argument of url, if none use 5 and 0.
            query_limit = int(request.args.get('limit', '5'))
            query_offset = int(request.args.get('offset', '0'))
            # call query.fetch to set the query to start at a particular point and limit of boat entity
            boat_iterator = query.fetch(limit=query_limit, offset=query_offset)
            # get query pages attribute, iterator container to contain one page
            pages = boat_iterator.pages
            # list() constuctor returns list consisting of iterable items since parameter was an iterable
            # next() retrieve next item from iterator
            results = list(next(pages))
            # iterator property (next_page_token) which is string we pass to query to start up where where left off
            if boat_iterator.next_page_token:
                # if next_page_token exists there are more pages left and need to calculat next URL
                next_offset = query_offset + query_limit
                next_url = request.base_url + "?limit=" + str(query_limit) + "&offset=" + str(next_offset)
            else:
                next_url = None

            for e in results:
                e["id"] = str(e.key.id)
                # build self_url from request info and boat entity key id
                self_url = str(request.base_url) + '/' + e["id"]
                # update new_load json with self url
                e.update({"self": self_url})
                if e["loads"]:
                    # iterate loads list and adds self
                    for cargo_item in e["loads"]:
                        load_key = client.key(constants.loads, int(cargo_item["id"]))
                        loads = client.get(key=load_key)
                        self_url_cargo = str(request.url_root) + 'loads/' + cargo_item["id"]
                        cargo_item.update({"self": self_url_cargo, "carrier": loads["carrier"], 
                                        "content": loads["content"]})

            # Add boat list to output
            output = {"Collection_Total": content_length, "boats": results}
            # output = {"boats": results}
            if next_url:
                output["next"] = next_url

            results = output
            res = make_response(json.dumps(results))
            res.mimetype = 'application/json'
            res.status_code = 200
            return res

        else: #else statement for request.accept_mimetype
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res

@bp.route('/<boat_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
def boat_id_get_delete_patch_put(boat_id):
    if request.method == 'GET':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # error check for getting owner sub info
        res_auth_jwt = sub_return_status(owner_sub)
        if res_auth_jwt:
            return res_auth_jwt

        if 'application/json' in request.accept_mimetypes:
            boat_key = client.key(constants.boats, int(boat_id))
            boats = client.get(key=boat_key)
            # if boat entity is nonetype (id doesn't exist) return error message and status code
            if boats is None:
                res = make_response(json.dumps(constants.error_miss_bID))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res

            # compare boat ownership id's
            # owner sub and boat owned by someone else
            if owner_sub != boats.get("owner"):
                res = make_response(json.dumps(constants.error_boat_owner_match))
                res.mimetype = 'application/json'
                res.status_code = 403
                return res

            if 'loads' in boats.keys():
                for cargo_item in boats["loads"]:
                    load_key = client.key(constants.loads, int(cargo_item["id"]))
                    loads = client.get(key=load_key)
                    cargo_item.update({"self": (str(request.url_root) + "loads/" + cargo_item["id"]),
                                    "carrier": loads["carrier"], "content": loads["content"]})

            self_url = str(request.base_url)
            boats.update({"id": str(boats.key.id), "self": self_url})
            results = boats
            # setting status code and content-type type with make_response function
            res = make_response(json.dumps(results))
            res.mimetype = 'application/json'
            res.status_code = 200
            return res

        else: #else statement for request.accept_mimetype
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    elif request.method =='DELETE':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # error check for getting owner sub info
        res_auth_jwt = sub_return_status(owner_sub)
        if res_auth_jwt:
            return res_auth_jwt

        if 'application/json' in request.accept_mimetypes:
            boat_key = client.key(constants.boats, int(boat_id))
            # get boat entity with the key requested
            boats = client.get(key=boat_key)

            # if boat entity is nonetype (id doesn't exist) return error message and status code
            if boats is None:
                res = make_response(json.dumps({constants.error_miss_bID}))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res

            # compare boat ownership id's
            # owner sub and boat owned by someone else
            if owner_sub != boats.get("owner"):
                res = make_response(json.dumps(constants.error_boat_owner_match))
                res.mimetype = 'application/json'
                res.status_code = 403
                return res

            # delete boat first then all associated loads
            client.delete(boat_key)

            # write method to search different load carrier data and remove it
            # very inefficent method to search loads and remove boat when deleted
            query = client.query(kind=constants.loads)
            results = list(query.fetch())
            for e in results:
                e["id"] = e.key.id
                if e["carrier"] is not None:
                    if e["carrier"]["id"] == boat_id:
                        finder_load_id = e["id"]
                        # once current boat found in carrier info and id obtained, get load entity to update
                        load_key = client.key(constants.loads, int(finder_load_id))
                        edit_loads = client.get(key=load_key)
                        edit_loads.update({"carrier": None}) 
                        client.put(edit_loads)
                        # break # <--- commented out since boat can have more than 1 load
            # return ('', 204) # for delete no return body
            # if I want to return no content response
            res = make_response('')
            res.mimetype = 'application/json'
            res.status_code = 204
            return res

        else: #else statement for request.accept_mimetype
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    elif request.method == 'PATCH':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # error check for getting owner sub info
        res_auth_jwt = sub_return_status(owner_sub)
        if res_auth_jwt:
            return res_auth_jwt

        # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes:
            boat_key = client.key(constants.boats, int(boat_id))
            edit_boats = client.get(key=boat_key)
            # if boats entity is nonetype return error message and status code
            # if boat entity is nonetype (id doesn't exist) return error message and status code
            if edit_boats is None:
                res = make_response(json.dumps(constants.error_miss_bID))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res

            # compare boat ownership id's
            # owner sub and boat owned by someone else
            if owner_sub != edit_boats.get("owner"):
                res = make_response(json.dumps(constants.error_boat_owner_match))
                res.mimetype = 'application/json'
                res.status_code = 403
                return res

            # check if request is json
            if not request.is_json:
                # return simple status code for unsupported media type (want JSON)
                res = make_response(json.dumps(constants.error_unsupported_media_type))
                res.mimetype = 'application/json'
                res.status_code = 415
                return res

            content = request.get_json()

            # iterate throguh content keys to check if there are matchs to constant keys
            # increament for tracking and append to list. Ignoring race conditions of duplicate keys
            key_match_count = 0
            key_match_list = []
            for key_check in content.keys():
                if key_check in constants.check_keys:
                    key_match_count += 1
                    key_match_list.append(key_check)

            if key_match_count == 0:
                res = make_response(json.dumps(constants.error_miss_attribute))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # input validation for keys that passed, not elegant
            for value_check in key_match_list:
                # check boat name length and value type
                if value_check == 'name':
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

                elif value_check == 'type':
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
                
                elif value_check == 'length':
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

                elif value_check == 'public':
                    # check public data type, needs to be bool.
                    if type(content["public"]) != bool:
                        res = make_response(json.dumps(constants.error_boat_public_type))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 

            # Add entity comparator to check what subset of attributes changed
            # update entity values with for loop and if statement that iterates throguh list
            for value_check in key_match_list:
                if edit_boats[value_check] != content[value_check]:
                    edit_boats.update({value_check: content[value_check]})

            # check boat name if unique or not
            if "name" in content.keys():
                query = client.query(kind=constants.boats)
                results = list(query.fetch())
                for e in results:
                    # if the boat name is already assigned to a boat then return 403 and error
                    if e["name"] == content["name"]:
                        # in case client perfers PUT to update same boat, error will be returned
                        # when boat id is not the same as in endpoint.
                        if str(e.key.id) != boat_id:
                            res = make_response(json.dumps(constants.error_boat_name_exists))
                            res.mimetype = 'application/json'
                            res.status_code = 403
                            return res

            # update existing entity to datastore
            client.put(edit_boats)
            # build self_url from request info
            self_url = str(request.base_url)
            # update edit_boats json with id and self url
            edit_boats.update({"id": edit_boats.key.id, "self": self_url})
            # # setting status code and content-type type with make_response function
            # res = make_response(json.dumps(edit_boats))
            # res.mimetype = 'application/json'
            # res.status_code = 200
            # return res
            # if I want to return no content response
            res = make_response('')
            res.mimetype = 'application/json'
            res.status_code = 204
            return res

        else: #else statement for request.accept_mimetype
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    elif request.method == 'PUT':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # error check for getting owner sub info
        res_auth_jwt = sub_return_status(owner_sub)
        if res_auth_jwt:
            return res_auth_jwt

        # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes:
            boat_key = client.key(constants.boats, int(boat_id))
            edit_boats = client.get(key=boat_key)
            # if boat entity is nonetype (id doesn't exist) return error message and status code
            if edit_boats is None:
                res = make_response(json.dumps(constants.error_miss_bID))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res

            # compare boat ownership id's
            # owner sub and boat owned by someone else
            if owner_sub != edit_boats.get("owner"):
                res = make_response(json.dumps(constants.error_boat_owner_match))
                res.mimetype = 'application/json'
                res.status_code = 403
                return res

            # check if request is json
            if not request.is_json:
                # return simple status code for unsupported media type (want JSON)
                res = make_response(json.dumps(constants.error_unsupported_media_type))
                res.mimetype = 'application/json'
                res.status_code = 415
                return res

            content = request.get_json()

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

            # check public data type, needs to be bool.
            if type(content["public"]) != bool:
                res = make_response(json.dumps(constants.error_boat_public_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res 
            
            # input validation, check boat name if unique or not
            query = client.query(kind=constants.boats)
            results = list(query.fetch())
            for e in results:
                # if the boat name is already assigned to a boat then return 403 and error
                if e["name"] == content["name"]:
                    # in case client perfers PUT to update same boat, error will be returned
                    # when boat id is not the same as in endpoint.
                    if str(e.key.id) != boat_id:
                        res = make_response(json.dumps(constants.error_boat_name_exists))
                        res.mimetype = 'application/json'
                        res.status_code = 403
                        return res

            # update entity values
            edit_boats.update({"name": content["name"], "type": content["type"],
            "length": content["length"]})
            # update existing entity as put to datastore
            client.put(edit_boats)
            # build self_url from request info
            self_url = str(request.base_url)
            # update edit_boats json with id and self url
            edit_boats.update({"id": edit_boats.key.id, "self": self_url})
            # # if I want to return response with payload
            # res = make_response(json.dumps(edit_boats))
            # res.mimetype = 'application/json'
            # res.status_code = 200
            # return res
            # if I want to return no content response # <---- switch over before submission
            res = make_response('')
            res.mimetype = 'application/json'
            res.status_code = 204
            return res
        
        else: #else statement for request.accept_mimetype
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res

# Assign or remove load from boat
@bp.route('/<boat_id>/loads/<load_id>', methods=['PUT', 'DELETE'])
def boats_loads_put_delete(boat_id, load_id):
    if request.method == 'PUT':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # error check for getting owner sub info
        res_auth_jwt = sub_return_status(owner_sub)
        if res_auth_jwt:
            return res_auth_jwt

        # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes:

            load_key = client.key(constants.loads, int(load_id))
            loads = client.get(key=load_key)

            boat_key = client.key(constants.boats, int(boat_id))
            boats = client.get(key=boat_key)

            # if boats or loads entity  doesnt exist return error message and status code
            if loads is None or boats is None:
                res = make_response(json.dumps(constants.error_miss_load_boat))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res

            # if the load entity is already assigned to a boat then return 403 and error
            elif loads["carrier"] is not None: 
                res = make_response(json.dumps(constants.error_load_already_assigned))
                res.mimetype = 'application/json'
                res.status_code = 403
                return res
            
            # if authenticated user is not the owner of the boat return 403 and error
            # authenticated user needs to be owner of boat to be authorize to edit
            # compare boat ownership id's, owner sub and boat owned by someone else
            elif owner_sub != boats.get("owner"):
                res = make_response(json.dumps(constants.error_boat_owner_match))
                res.mimetype = 'application/json'
                res.status_code = 403
                return res

            loads.update({"carrier": {"id": boat_id, "name": boats["name"]}})
            # put update loads entity
            client.put(loads)
            # pull loads list from boat
            temp_list = boats["loads"]
            loads_dict = {"id": load_id}
            # append load dictionary to list
            temp_list.append(loads_dict)
            # datastore method update entity loads key
            boats.update({"loads": temp_list})
            # put updated boats entity
            client.put(boats)

            res = make_response('')
            res.mimetype = 'application/json'
            res.status_code = 204
            return res
        
        else: #else statement for request.accept_mimetype
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    elif request.method =='DELETE':
        #owner of the boat, value of sub property in the JWT
        owner_sub = get_sub_info()

        # error check for getting owner sub info
        res_auth_jwt = sub_return_status(owner_sub)
        if res_auth_jwt:
            return res_auth_jwt

        # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes: 

            load_key = client.key(constants.loads, int(load_id))
            loads = client.get(key=load_key)

            boat_key = client.key(constants.boats, int(boat_id))
            boats = client.get(key=boat_key)

            # if boats or loads entity doesnt exist return error message and status code
            if loads is None or boats is None:
                res = make_response(json.dumps(constants.error_miss_load_boat))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res
                
            # if authenticated user is not the owner of the boat return 403 and error
            # authenticated user needs to be owner of boat to be authorize to edit
            # compare boat ownership id's, owner sub and boat owned by someone else
            elif owner_sub != boats.get("owner"):
                res = make_response(json.dumps(constants.error_boat_owner_match))
                res.mimetype = 'application/json'
                res.status_code = 403
                return res

            # if no load id matches in boat cargo then throw error
            # elif 'loads' in boats.keys():
            elif 'loads' in boats.keys():
                load_count = 0
                boat_key_num = len(boats["loads"])
                for cargo_item in boats["loads"]:
                    if load_id != cargo_item["id"]:
                        load_count += 1

                if load_count >= boat_key_num:
                    res = make_response(json.dumps(constants.error_miss_load_boat_del))
                    res.mimetype = 'application/json'
                    res.status_code = 404
                    return res

            # check if boat_id matches carrier id in load,
            # TypeError: 'NoneType' object is not subscriptable
            if boat_id != loads["carrier"]["id"]:
                res = make_response(json.dumps(constants.error_miss_boat_load_del))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res      

            # update load information and remove carrier info
            loads.update({"carrier": None})
            client.put(loads)

            # search boat load list to search and delete dictionary of the load
            boat_load_list_temp = boats["loads"]

            # using list comprehension to delete dictionary in list, geeksforgeeks
            filtered_list = [i for i in boat_load_list_temp if not (i['id'] == load_id)]

            # update the boat info when load removed the boat, input valid at begining
            boats.update({"loads": filtered_list})
            client.put(boats)

            res = make_response('')
            res.mimetype = 'application/json'
            res.status_code = 204
            return res

        else: #else statement for request.accept_mimetype
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res