from google.cloud import datastore
from flask import Flask, request, Blueprint
import json
import constants

client = datastore.Client()

# Python Blueprint template that creates Blueprint named 'boat', 2nd par __name__ the blueprint
# know where it's defined, url_prefix will prepend to all URLs associated with the blueprint.
bp = Blueprint('load', __name__, url_prefix='/loads')

@bp.route('', methods=['POST','GET'])
def loads_post_get():
    if request.method == 'POST':
        content = request.get_json()
        # using comparison operator for key value check, True if all keys present
        if not (content.keys()) >= constants.check_keys_3:
            return (json.dumps(constants.error_miss_attribute), 400)

        # creat datastore entity
        new_load = datastore.entity.Entity(key=client.key(constants.loads))
        new_load.update({"weight": content["weight"], "carrier": None,
          "content": content["content"], "delivery_date": content["delivery_date"]})
        # put new entity to datastore
        client.put(new_load)
        
        # build self_url from request info and new new_load entity key id
        self_url = str(request.base_url) + '/' + str(new_load.key.id)
        # update new_load json with id and self url
        new_load.update({"id": str(new_load.key.id), "self": self_url})
        #return tuple of new_load json string and status code 201
        return (json.dumps(new_load), 201)

    elif request.method == 'GET':
        # pagination by w04 math implementation
        query = client.query(kind=constants.loads)
        # pull limit and offset from argument of url, if none use 3 and 0.
        query_limit = int(request.args.get('limit', '3'))
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
            
        # Add load list to output
        output = {"loads": results}
        if next_url:
            output["next"] = next_url
        return (json.dumps(output), 200)
    else:
        return 'Method not recogonized'

@bp.route('/<load_id>', methods=['GET', 'DELETE'])
def loads_get_delete(load_id):
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
        results = json.dumps(loads)
        return (results, 200)
    
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
    else:
        return 'Method not recognoized'