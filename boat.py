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
          "length": content["length"], "loads": content["loads"]})
        # put new entity to datastore
        client.put(new_boat)
        
        # build self_url from request info and new new_boat entity key id
        self_url = str(request.base_url) + '/' + str(new_boat.key.id)
        # update new_boat json with id and self url
        new_boat.update({"id": new_boat.key.id, "self": self_url})
        #return tuple of new_boat json string and status code 201
        return (json.dumps(new_boat), 201)

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        query_limit = int(request.args.get("limit", "2"))
        query_offset = int(request.args.get("offset", "0"))
        boat_iterator = query.fetch(limit=query_limit, offset=query_offset)
        pages = boat_iterator.pages
        results = list(next(pages))
        if boat_iterator.next_page_token:
            next_offset = query_offset + query_limit
            next_url = request.base_url + "?limit=" + str(query_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        
        for e in results:
            e["id"] = e.key.id
             # build self_url from request info and boat entity key id
            self_url = str(request.base_url) + '/' + str(e.key.id)
            # update new_boat json with id and self url
            e.update({"self": self_url})
        
        if next_url:
            output["next"] = next_url
        return (json.dumps(output), 200)
    else:
        return 'Method not recogonized'

@bp.route('/<boat_id>', methods=['GET', 'PATCH', 'DELETE'])
def boats_get_patch_delete(boat_id):
    if request.method == 'GET':
        boat_key = client.key(constants.boats, int(boat_id))
        boats = client.get(key=boat_key)
        # if boats entity is nonetype return error message and status code
        if boats is None:
            return (json.dumps(constants.error_miss_bID), 404)

        self_url = str(request.base_url)
        boats.update({"id": boats.key.id, "self": self_url})
        results = json.dumps(boats)
        return (results,200)

    elif request.method =='PATCH':
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

    elif request.method =='DELETE': # still needs method to make slip empty when boat deleted
        boat_key = client.key(constants.boats, int(boat_id))
        # get boat entity with the key requested
        boats = client.get(key=boat_key)
        # if boat entity is nonetype (id doesn't exist) return error message and status code
        if boats is None:
            return (json.dumps(constants.error_miss_bID), 404)

        client.delete(boat_key)

        # very inefficent method to search slips and remove boat when deleted
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            if e["current_boat"] == int(boat_id):
                finder_slip_id = e["id"]
                # once current boat found in slip and id obtained get slip entity to update
                slip_key = client.key(constants.slips, int(finder_slip_id))
                edit_slips = client.get(key=slip_key)
                edit_slips.update({"current_boat": None}) 
                client.put(edit_slips)
                break
        return ('', 204)

    else:
        return 'Method not recogonized'