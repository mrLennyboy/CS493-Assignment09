from google.cloud import datastore
from flask import Flask, request, Blueprint, make_response
import json
import constants
from json2html import *

client = datastore.Client()

# Python Blueprint template that creates Blueprint named 'boat', 2nd par __name__ the blueprint
# know where it's defined, url_prefix will prepend to all URLs associated with the blueprint.
bp = Blueprint('boat', __name__, url_prefix='/boats')

def boat_input_validation():
    return "Hello I'm in the function"

# @bp.route('', methods=['POST','GET'])
@bp.route('', methods=['POST'])
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
                # return (json.dumps(constants.error_unsupported_media_type), 415)

            # get request json
            content = request.get_json()

            # using comparison operator for key value check, True if all keys present
            if not (content.keys()) >= constants.check_keys:
                res = make_response(json.dumps(constants.error_miss_attribute))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_miss_attribute), 400)

            # start of input validation
            # check boat name length and value type
            if type(content["name"]) != str: 
                res = make_response(json.dumps(constants.error_boat_name_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_name_type), 400)
            if len(content["name"]) > 33:
                res = make_response(json.dumps(constants.error_boat_name_length))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_name_length), 400) 

            # boat name passes earlier type and length then check if all alpha or space
            # if string not all alpha or space then return error
            if not all(letter.isalpha() or letter.isspace() for letter in content["name"]):
                res = make_response(json.dumps(constants.error_boat_name_invalid))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_name_invalid), 400) 

            # check boat type data type and length
            if type(content["type"]) != str: 
                res = make_response(json.dumps(constants.error_boat_type_str))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_type_str), 400)
            if len(content["type"]) > 33:
                res = make_response(json.dumps(constants.error_boat_type_length))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_type_length), 400)

            # boat type passes earlier type and length then check if all alpha or space
            # if string not all alpha or space then return error
            if not all(letter.isalpha() or letter.isspace() for letter in content["type"]):
                res = make_response(json.dumps(constants.error_boat_type_invalid))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_type_invalid), 400) 

            # check length data type and have int value below 10,000ft, largest ship around 1,500 ft
            if type(content["length"]) != int:
                res = make_response(json.dumps(constants.error_boat_length_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_length_type), 400)
            if content["length"] > 10000 or content["length"] < 0:
                res = make_response(json.dumps(constants.error_boat_length_limit))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_length_limit), 400)
            
            # input validation, check boat name if unique or not
            query = client.query(kind=constants.boats)
            results = list(query.fetch())
            for e in results:
                # if the boat name is already assigned to a boat then return 403 and error
                if e["name"] == content["name"]:
                    res = make_response(json.dumps(constants.error_boat_name_exists))
                    res.mimetype = 'application/json'
                    res.status_code = 403
                    return res
                    # return (json.dumps(constants.error_boat_name_exists), 403)

            # create datastore entity
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))

            # Update new entity with content data
            new_boat.update({"name": content["name"], "type": content["type"],
            "length": content["length"]})
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
            # print(res.mimetype)
            return res

        else: #else statement for request.accept_mimetype text/html type
            # return "This client doesn't accept application/json" as text/html
            return (json.dumps(constants.error_unsupported_accept_type), 406)
    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res

@bp.route('/<boat_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
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
            return (json.dumps(constants.error_unsupported_accept_type), 406)

    elif request.method =='DELETE':
        boat_key = client.key(constants.boats, int(boat_id))
        # get boat entity with the key requested
        boats = client.get(key=boat_key)
        # if boat entity is nonetype (id doesn't exist) return error message and status code
        if boats is None:
            res = make_response(json.dumps(constants.error_miss_bID))
            res.mimetype = 'application/json'
            res.status_code = 404
            return res
            # return (json.dumps(constants.error_miss_bID), 404)

        client.delete(boat_key)
        return ('', 204) # for delete no return body

    elif request.method == 'PATCH':
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

            # check if request is json
            if not request.is_json:
                # return simple status code for unsupported media type (want JSON)
                res = make_response(json.dumps(constants.error_unsupported_media_type))
                res.mimetype = 'application/json'
                res.status_code = 415
                return res
                # return (json.dumps(constants.error_unsupported_media_type), 415)

            content = request.get_json()
            # iterate throguh content keys to check if there are matchs to constant keys
            # increament for tracking and append to list. Ignoring race conditions of duplicate keys
            key_match_count = 0
            key_match_list = []
            for key_check in content.keys():
                if key_check in constants.check_keys:
                    key_match_count += 1
                    key_match_list.append(key_check)
            # return error if there are no key value matches for PATCH
            if key_match_count == 0:
                res = make_response(json.dumps(constants.error_miss_attribute))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_miss_attribute), 400)

            # input validation for keys that passed, not elegant
            for value_check in key_match_list:
                # check boat name length and value type
                if value_check == 'name':
                    if type(content["name"]) != str:
                        res = make_response(json.dumps(constants.error_boat_name_type))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 
                        # return (json.dumps(constants.error_boat_name_type), 400)
                    if len(content["name"]) > 33:
                        res = make_response(json.dumps(constants.error_boat_name_length))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 
                        # return (json.dumps(constants.error_boat_name_length), 400)
                    # boat name passes earlier type and length then check if all alpha or space
                    # if string not all alpha or space then return error
                    if not all(letter.isalpha() or letter.isspace() for letter in content["name"]):
                        res = make_response(json.dumps(constants.error_boat_name_invalid))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 
                        # return (json.dumps(constants.error_boat_name_invalid), 400) 

                elif value_check == 'type':
                    # check boat type data type and length
                    if type(content["type"]) != str:
                        res = make_response(json.dumps(constants.error_boat_type_str))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res  
                        # return (json.dumps(constants.error_boat_type_str), 400)
                    if len(content["type"]) > 33:
                        res = make_response(json.dumps(constants.error_boat_type_length))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 
                        # return (json.dumps(constants.error_boat_type_length), 400)
                    # boat type passes earlier type and length then check if all alpha or space
                    # if string not all alpha or space then return error
                    if not all(letter.isalpha() or letter.isspace() for letter in content["type"]):
                        res = make_response(json.dumps(constants.error_boat_type_invalid))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 
                        # return (json.dumps(constants.error_boat_type_invalid), 400)
                
                elif value_check == 'length':
                    # check length data type and have int value below 10,000ft, largest ship around 1,500 ft
                    if type(content["length"]) != int:
                        res = make_response(json.dumps(constants.error_boat_length_type))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 
                        # return (json.dumps(constants.error_boat_length_type), 400)
                    if content["length"] > 10000 or content["length"] < 0:
                        res = make_response(json.dumps(constants.error_boat_length_limit))
                        res.mimetype = 'application/json'
                        res.status_code = 400
                        return res 
                        # return (json.dumps(constants.error_boat_length_limit), 400)
            
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
                        res = make_response(json.dumps(constants.error_boat_name_exists))
                        res.mimetype = 'application/json'
                        res.status_code = 403
                        return res
                        # return (json.dumps(constants.error_boat_name_exists), 403)

            # update existing entity as put to datastore
            client.put(edit_boats)
            # build self_url from request info
            self_url = str(request.base_url)
            # update edit_boats json with id and self url
            edit_boats.update({"id": edit_boats.key.id, "self": self_url})
            # setting status code and content-type type with make_response function
            res = make_response(json.dumps(edit_boats))
            res.mimetype = 'application/json'
            res.status_code = 200
            # print(res.mimetype)
            return res

        else: #else statement for request.accept_mimetype
            # return "This client doesn't accept application/json" as text/html
            return (json.dumps(constants.error_unsupported_accept_type), 406)

    elif request.method == 'PUT':
        # check to see if application/json is listed in Accept header
        if 'application/json' in request.accept_mimetypes:
            # check if request is json
            if not request.is_json:
                # return simple status code for unsupported media type (want JSON)
                res = make_response(json.dumps(constants.error_unsupported_media_type))
                res.mimetype = 'application/json'
                res.status_code = 415
                return res
                # return (json.dumps(constants.error_unsupported_media_type), 415)

            content = request.get_json()
            # using comparison operator for key value check, True if all keys present
            if not (content.keys()) >= constants.check_keys:
                res = make_response(json.dumps(constants.error_miss_attribute))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_miss_attribute), 400)

            # start of input validation
            # check boat name length and value type
            if type(content["name"]) != str: 
                res = make_response(json.dumps(constants.error_boat_name_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_name_type), 400)
            if len(content["name"]) > 33:
                res = make_response(json.dumps(constants.error_boat_name_length))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_name_length), 400) 

            # boat name passes earlier type and length then check if all alpha or space
            # if string not all alpha or space then return error
            if not all(letter.isalpha() or letter.isspace() for letter in content["name"]):
                res = make_response(json.dumps(constants.error_boat_name_invalid))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_name_invalid), 400) 

            # check boat type data type and length
            if type(content["type"]) != str: 
                res = make_response(json.dumps(constants.error_boat_type_str))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_type_str), 400)
            if len(content["type"]) > 33:
                res = make_response(json.dumps(constants.error_boat_type_length))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_type_length), 400)

            # boat type passes earlier type and length then check if all alpha or space
            # if string not all alpha or space then return error
            if not all(letter.isalpha() or letter.isspace() for letter in content["type"]):
                res = make_response(json.dumps(constants.error_boat_type_invalid))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_type_invalid), 400) 

            # check length data type and have int value below 10,000ft, largest ship around 1,500 ft
            if type(content["length"]) != int:
                res = make_response(json.dumps(constants.error_boat_length_type))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_length_type), 400)
            if content["length"] > 10000 or content["length"] < 0:
                res = make_response(json.dumps(constants.error_boat_length_limit))
                res.mimetype = 'application/json'
                res.status_code = 400
                return res
                # return (json.dumps(constants.error_boat_length_limit), 400)
            
            # input validation, check boat name if unique or not
            query = client.query(kind=constants.boats)
            results = list(query.fetch())
            for e in results:
                # if the boat name is already assigned to a boat then return 403 and error
                if e["name"] == content["name"]:
                    res = make_response(json.dumps(constants.error_boat_name_exists))
                    res.mimetype = 'application/json'
                    res.status_code = 403
                    return res
                    # return (json.dumps(constants.error_boat_name_exists), 403)

            boat_key = client.key(constants.boats, int(boat_id))
            # print(boat_key)
            edit_boats = client.get(key=boat_key)
            # if boats entity is nonetype return error message and status code
            if edit_boats is None:
                res = make_response(json.dumps(constants.error_miss_bID))
                res.mimetype = 'application/json'
                res.status_code = 404
                return res
                # return (json.dumps(constants.error_miss_bID), 404)

            # check boat name if unique or not
            if "name" in content.keys():
                query = client.query(kind=constants.boats)
                results = list(query.fetch())
                for e in results:
                    # if the boat name is already assigned to a boat then return 403 and error
                    if e["name"] == content["name"]:
                        res = make_response(json.dumps(constants.error_boat_name_exists))
                        res.mimetype = 'application/json'
                        res.status_code = 403
                        return res
                        # return (json.dumps(constants.error_boat_name_exists), 403)

            # update entity values
            edit_boats.update({"name": content["name"], "type": content["type"],
            "length": content["length"]})
            # update existing entity as put to datastore
            client.put(edit_boats)
            # build self_url from request info
            self_url = str(request.base_url)
            # update edit_boats json with id and self url
            edit_boats.update({"id": edit_boats.key.id, "self": self_url})
            # setting status code and content-type type with make_response function
            res = make_response(json.dumps(edit_boats))
            # res.mimetype = 'application/json'
            res.headers.set('Content-Type', 'application/json')
            res.headers.set('Location', self_url)
            res.status_code = 303
            # print(res.mimetype)
            return res

        else: #else statement for request.accept_mimetype
            # return "This client doesn't accept application/json" as text/html
            return (json.dumps(constants.error_unsupported_accept_type), 406)

    else:
        # return 'Method not recogonized'
        res = make_response(json.dumps(constants.error_method_not_allowed))
        res.mimetype = 'application/json'
        res.status_code = 405
        return res

