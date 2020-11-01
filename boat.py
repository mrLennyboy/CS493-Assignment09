from google.cloud import datastore
from flask import Flask, request, Blueprint
import json
import constants

client = datastore.Client()

# Python Blueprint template that creates Blueprint named 'boat', 2nd par __name__ the blueprint
# know where it's defined, url_prefix will prepend to all URLs associated with the blueprint.
bp = Blueprint('boat', __name__, url_prefix='/boats')

@bp.route('', methods=['POST','GET'])
def boats_post_get():
    if request.method == 'POST':
        content = request.get_json()
        # using comparison operator for key value check, True if all keys present
        if not (content.keys()) >= constants.check_keys:
            return (json.dumps(constants.error_miss_attribute), 400)

        # creat datastore entity
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"]})
        # put new entity to datastore
        client.put(new_boat)
        
        # build self_url from request info and new new_boat entity key id
        self_url = str(request.base_url) + '/' + str(new_boat.key.id)
        # update new_boat json with id and self url
        new_boat.update({"id": str(new_boat.key.id), "self": self_url})
        #return tuple of new_boat json string and status code 201
        return (json.dumps(new_boat), 201)

    elif request.method == 'GET':
        # pagination by w04 math implementation
        query = client.query(kind=constants.boats)
        # pull limit and offset from argument of url, if none use 3 and 0.
        query_limit = int(request.args.get('limit', '3'))
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
            e["id"] = e.key.id
             # build self_url from request info and boat entity key id
            self_url = str(request.base_url) + '/' + str(e.key.id)
            # update new_boat json with id and self url
            e.update({"self": self_url, "id": str(e.key.id)})

        # Add boat list to output
        output = {"boats": results}
        if next_url:
            output["next"] = next_url
        return (json.dumps(output), 200)
    else:
        return 'Method not recogonized'

@bp.route('/<boat_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
def boats_get_delete_patch_put(boat_id):
    if request.method == 'GET':
        boat_key = client.key(constants.boats, int(boat_id))
        boats = client.get(key=boat_key)
        # if boats entity is nonetype return error message and status code
        if boats is None:
            return (json.dumps(constants.error_miss_bID), 404)

        if 'loads' in boats.keys():
            for cargo_item in boats["loads"]:
                cargo_item.update({"self": (str(request.url_root) + "loads/" + cargo_item["id"])})

        self_url = str(request.base_url)
        boats.update({"id": str(boats.key.id), "self": self_url})
        results = json.dumps(boats)
        return (results,200)

    elif request.method =='DELETE':
        boat_key = client.key(constants.boats, int(boat_id))
        # get boat entity with the key requested
        boats = client.get(key=boat_key)
        # if boat entity is nonetype (id doesn't exist) return error message and status code
        if boats is None:
            return (json.dumps(constants.error_miss_bID), 404)

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
                    break
        return ('', 204)

    elif request.method == 'PATCH':
        content = request.get_json()
        # using comparison operator for key value check, True if all keys present
        if not (content.keys()) >= constants.check_keys:
            return (json.dumps(constants.error_miss_attribute), 400)

        boat_key = client.key(constants.boats, int(boat_id))
        # print(boat_key)
        edit_boats = client.get(key=boat_key)
        # if boats entity is nonetype return error message and status code
        if edit_boats is None:
            return (json.dumps(constants.error_miss_bID), 404)
        
        # Add entity comparator to check what subset of attributes changed
        # update entity values with lots of if statements
        if edit_boats["name"] != content["name"]:
            edit_boats.update({"name": content["name"]})

        if edit_boats["type"] != content["type"]:
            edit_boats.update({"type": content["type"]})

        if edit_boats["length"] != content["length"]:
            edit_boats.update({"length": content["length"]})

        # update existing entity as put to datastore
        client.put(edit_boats)
        # build self_url from request info
        self_url = str(request.base_url)
        # update edit_boats json with id and self url
        edit_boats.update({"id": edit_boats.key.id, "self": self_url})
        return (json.dumps(edit_boats), 200)

    elif request.method == 'PUT':
        content = request.get_json()
        # using comparison operator for key value check, True if all keys present
        if not (content.keys()) >= constants.check_keys:
            return (json.dumps(constants.error_miss_attribute), 400)

        boat_key = client.key(constants.boats, int(boat_id))
        # print(boat_key)
        edit_boats = client.get(key=boat_key)
        # if boats entity is nonetype return error message and status code
        if edit_boats is None:
            return (json.dumps(constants.error_miss_bID), 404)

        # update entity values
        edit_boats.update({"name": content["name"], "type": content["type"],
          "length": content["length"]})
        # update existing entity as put to datastore
        client.put(edit_boats)
        # build self_url from request info
        self_url = str(request.base_url)
        # update edit_boats json with id and self url
        edit_boats.update({"id": edit_boats.key.id, "self": self_url})
        return (json.dumps(edit_boats), 200)
    else:
        return 'Method not recogonized'