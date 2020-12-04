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

from datetime import datetime

# files for constants and boat routes by blueprint
import client_info

# Python Blueprint template that creates Blueprint named 'loads', 2nd par __name__ the blueprint
# know where it's defined, url_prefix will prepend to all URLs associated with the blueprint.
bp = Blueprint('load', __name__, url_prefix='/loads')

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

@bp.route('', methods=['POST','GET'])
def loads_post_get():
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

            # using comparison operator for key value check, True if all keys present
            if not (content.keys()) >= constants.check_keys_3:
                res = make_response(json.dumps(constants.error_miss_attribute))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # start of input validation
            # check content description length and value type
            if type(content["content"]) != str: 
                res = make_response(json.dumps(constants.error_content_desc_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
 
            # for content length description random length
            if len(content["content"]) > 129:
                res = make_response(json.dumps(constants.error_content_desc_length))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # check delivery date input data type as xx/xx/xxxx (MM/DD/YYYY) and delivery date char length
            if type(content["delivery_date"]) != str: 
                res = make_response(json.dumps(constants.error_delivery_date_str))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # check delivery_date datetime format mm/dd/yyyy
            try:
                date = datetime.strptime(content["delivery_date"], "%m/%d/%Y")
            except ValueError:
                # return json.dumps({"Error":"Invalid date entered, date format needs to be mm/dd/yyyy."})
                res = make_response(json.dumps(constants.error_delivery_date_format))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # check weight data type and have int value below 100,000, unitless (assume in lb)
            if type(content["weight"]) != int:
                res = make_response(json.dumps(constants.error_load_weight_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            if content["weight"] > 100000 or content["weight"] < 0:
                res = make_response(json.dumps(constants.error_load_weight_limit))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # creat datastore entity
            new_load = datastore.entity.Entity(key=client.key(constants.loads))

            # Update new entity with content data, empty carrier explicit defined
            new_load.update({"weight": content["weight"], "carrier": None,
            "content": content["content"], "delivery_date": content["delivery_date"]})
            # put new entity to datastore
            client.put(new_load)
            
            # build self_url from request info and new new_load entity key id
            self_url = str(request.base_url) + '/' + str(new_load.key.id)
            # update new_load json with id and self url
            new_load.update({"id": str(new_load.key.id), "self": self_url})
            # setting status code and content-type type with make_response function
            res = make_response(json.dumps(new_load))
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
        # pagination by w04 math implementation
        query = client.query(kind=constants.loads)
        
        # number of total items that are in the collection from filtered or non-filtered query
        content_length = len(list(query.fetch()))

        # pull limit and offset from argument of url, if none use 3 and 0.
        query_limit = int(request.args.get('limit', '5'))
        query_offset = int(request.args.get('offset', '0'))
        # call query.fetch to set the query to start at a particular point and limit of boat entity
        load_iterator = query.fetch(limit=query_limit, offset=query_offset)
        # get query pages attribute, iterator container to contain one page
        pages = load_iterator.pages
        # list() constuctor returns list consisting of iterable items since parameter was an iterable
        # next() retrieve next item from iterator
        results = list(next(pages))
        # iterator property (next_page_token) which is string we pass to query to start up where where left off
        if load_iterator.next_page_token:
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

        print(results)
            
        # Add load list to output
        output = {"Collection_Total": content_length, "loads": results}
        if next_url:
            output["next"] = next_url

        results = output
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

# DELETE, PUT, and PATCH should be protected
@bp.route('/<load_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
def loads_get_delete_patch_put(load_id):
    if request.method == 'GET':
        load_key = client.key(constants.loads, int(load_id))
        loads = client.get(key=load_key)
        # if loads entity is nonetype return error message and status code
        if loads is None:
            return(json.dumps(constants.error_miss_loadID), 404)

        # if 'carrier' not loads.keys():
        if loads["carrier"] is not None:
            # print(loads["carrier"])
            loads["carrier"].update({"self": (str(request.url_root) + "boats/" + loads["carrier"]["id"])})

        # build self_url from request url
        self_url = str(request.base_url)
        loads.update({"id": str(loads.key.id), "self": self_url})
        results = loads
        res = make_response(json.dumps(results))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res
    
    elif request.method == 'DELETE':
        load_key = client.key(constants.loads, int(load_id))
        # get load entity with the key requested
        loads = client.get(key=load_key)
        # if load entity is noneType (id doesn't exist) return error message and status code
        if loads is None:
            return (json.dumps(constants.error_miss_loadID), 404)
        # delete load by id on datastore side
        client.delete(load_key)

        # very inefficent method to search boats and remove load when deleted
        query = client.query(kind=constants.boats)
        results = list(query.fetch())

        for e in results:
            e["id"] = e.key.id #boat id
            # true if list is not empty
            if e["loads"]:
                for cargo_item in e["loads"]:
                    if cargo_item["id"] == load_id:
                        finder_boat_id = e["id"]
                        boat_key = client.key(constants.boats, int(finder_boat_id))
                        edit_boats = client.get(key=boat_key)
                        edit_boats["loads"].remove({"id": load_id})
                        client.put(edit_boats)
                        break
        #return nothing except 204 status code
        return ('', 204)

    elif request.method == 'PATCH':
        # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes:

            load_key = client.key(constants.loads, int(load_id))
            edit_loads = client.get(key=load_key)

            # if loads entity is nonetype return error message and status code
            if edit_loads is None:
                res = make_response(json.dumps(constants.error_miss_loadID))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res

            # check if request is json
            if not request.is_json:
                # return simple status code for unsupported media type (want JSON)
                res = make_response(json.dumps(constants.error_unsupported_media_type))
                res.mimetype = 'application/json'
                res.status_code = 415
                return res

            # get request json
            content = request.get_json()

            # iterate throguh content keys to check if there are matchs to constant keys
            # increament for tracking and append to list. Ignoring race conditions of duplicate keys
            key_match_count = 0
            key_match_list = []
            for key_check in content.keys():
                if key_check in constants.check_keys_3:
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
                if value_check == 'content':
                    # check content description length and value type
                    if type(content["name"]) != str:
                        res = make_response(json.dumps(constants.error_content_desc_type))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 

                    # for content length description random length
                    if len(content["content"]) > 129:
                        res = make_response(json.dumps(constants.error_content_desc_length))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 

                elif value_check == 'delivery_date':
                    # check delivery date input data type as xx/xx/xxxx (MM/DD/YYYY) and delivery date char length
                    if type(content["delivery_date"]) != str: 
                        res = make_response(json.dumps(constants.error_delivery_date_str))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res

                    # check delivery_date datetime format mm/dd/yyyy
                    try:
                        date = datetime.strptime(content["delivery_date"], "%m/%d/%Y")
                    except ValueError:
                        # return json.dumps({"Error":"Invalid date entered, date format needs to be mm/dd/yyyy."})
                        res = make_response(json.dumps(constants.error_delivery_date_format))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res
                
                elif value_check == 'weight':
                    # check weight data type and have int value below 100,000, unitless (assume in lb)
                    if type(content["weight"]) != int:
                        res = make_response(json.dumps(constants.error_load_weight_type))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res

                    if content["weight"] > 100000 or content["weight"] < 0:
                        res = make_response(json.dumps(constants.error_load_weight_limit))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res

            # Add entity comparator to check what subset of attributes changed
            # update entity values with for loop and if statement that iterates throguh list
            for value_check in key_match_list:
                if edit_loads[value_check] != content[value_check]:
                    edit_loads.update({value_check: content[value_check]})

            # update existing entity to datastore
            client.put(edit_loads)
            # build self_url from request info
            self_url = str(request.base_url)
            # update edit_boats json with id and self url
            edit_loads.update({"id": edit_loads.key.id, "self": self_url})
            # setting status code and content-type type with make_response function
            # res = make_response(json.dumps(edit_loads))
            # res.mimetype = 'application/json'
            # res.status_code = 200
            res = make_response('')
            res.mimetype = 'application/json'
            res.status_code = 204
            return res

            return res

        else: #else statement for request.accept_mimetype text/html type
            # return "This client doesn't accept application/json" as text/html
            res = make_response(json.dumps(constants.error_unsupported_accept_type))
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    elif request.method == 'PUT':
         # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes:

            load_key = client.key(constants.loads, int(load_id))
            edit_loads = client.get(key=load_key)

            # if loads entity is nonetype return error message and status code
            if edit_loads is None:
                res = make_response(json.dumps(constants.error_miss_loadID))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res

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
            if not (content.keys()) >= constants.check_keys_3:
                res = make_response(json.dumps(constants.error_miss_attribute))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # start of input validation
            # check content description length and value type
            if type(content["content"]) != str: 
                res = make_response(json.dumps(constants.error_content_desc_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
 
            # for content length description random length
            if len(content["content"]) > 129:
                res = make_response(json.dumps(constants.error_content_desc_length))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # check delivery date input data type as xx/xx/xxxx (MM/DD/YYYY) and delivery date char length
            if type(content["delivery_date"]) != str: 
                res = make_response(json.dumps(constants.error_delivery_date_str))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # check delivery_date datetime format mm/dd/yyyy
            try:
                date = datetime.strptime(content["delivery_date"], "%m/%d/%Y")
            except ValueError:
                # return json.dumps({"Error":"Invalid date entered, date format needs to be mm/dd/yyyy."})
                res = make_response(json.dumps(constants.error_delivery_date_format))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # check weight data type and have int value below 100,000, unitless (assume in lb)
            if type(content["weight"]) != int:
                res = make_response(json.dumps(constants.error_load_weight_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            if content["weight"] > 100000 or content["weight"] < 0:
                res = make_response(json.dumps(constants.error_load_weight_limit))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res

            # update entity values
            edit_loads.update({"content": content["content"], "delivery_date": content["delivery_date"],
            "weight": content["weight"]})
            # update existing entity as put to datastore
            client.put(edit_loads)
            # build self_url from request info
            self_url = str(request.base_url)
            # update edit_boats json with id and self url
            edit_loads.update({"id": edit_loads.key.id, "self": self_url})
            # # if I want to return response with payload
            # res = make_response(json.dumps(edit_loads))
            # res.mimetype = 'application/json'
            # res.status_code = 200
            # return res

            # if I want to return no content response
            res = make_response('')
            res.mimetype = 'application/json'
            res.status_code = 204
            return res

        else: #else statement for request.accept_mimetype text/html type
            # return "This client doesn't accept application/json" as text/html
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