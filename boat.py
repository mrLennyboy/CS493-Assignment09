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
            e.update({"self": self_url})

        # Add boat list to output
        output = {"boats": results}
        if next_url:
            output["next"] = next_url
        return (json.dumps(output), 200)
    else:
        return 'Method not recogonized'

# update code
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

        #also add loads idea to each load dictionary
        
        results = json.dumps(boats)
        return (results,200)
# update code
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
# update code
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

@bp.route('/<boat_id>/loads/<load_id>', methods=['PUT', 'DELETE'])
def boats_loads_put_delete(boat_id, load_id):
    if request.method == 'PUT':
        load_key = client.key(constants.loads, int(load_id))
        loads = client.get(key=load_key)

        boat_key = client.key(constants.boats, int(boat_id))
        boats = client.get(key=boat_key)

        # if boats or loads entity id doesnt exist return error message and status code
        if loads is None or boats is None:
            return (json.dumps(constants.error_miss_load_boat), 404)

        # # if the load entity is already assigned to a boat then return 403 and error
        elif loads["carrier"] is not None: 
            return (json.dumps(constants.error_load_already_assigned), 403)

        # # very inefficent method to search boats and prevent multiple same load assignments
        # query = client.query(kind=constants.boats)
        # results = list(query.fetch())
        # for e in results:
        #     e["id"] = e.key.id
        #     if e["current_boat"] == int(boat_id):
        #         return(json.dumps(constants.error_one_boat_slip), 403)

        # add carrier info to load before adding load info to boat
        # loads.update({"carrier": {"id": boat_id, "name": boats["name"], "self": (str(request.url_root) + "boats/" + boat_id)}})
        loads.update({"carrier": {"id": boat_id, "name": boats["name"]}})
        # put update loads entity
        client.put(loads)
        # pull loads list from boat
        temp_list = boats["loads"]
        # make dictionary of load id and self link, track cargo load on boat
        # loads_dict = {"id": str(loads.key.id), "self": (str(request.url_root) + "loads/" + load_id)}
        loads_dict = {"id": str(loads.key.id)}
        # append dictionary to list
        temp_list.append(loads_dict)
        # datastore method update entity loads key
        boats.update({"loads": temp_list})
        # put updated boats entity
        client.put(boats)
        return ('', 204)

    elif request.method =='DELETE':
        slip_key = client.key(constants.slips, int(slip_id))
        slips = client.get(key=slip_key)

        boat_key = client.key(constants.boats, int(boat_id))
        boats = client.get(key=boat_key)

        if slips is None or boats is None:
            return (json.dumps(constants.error_miss_boat_this_slip), 404)

        # comparators not combine since datatype error if slips["current_boat"] is first
        # with invalid slip, unsubscriptable dict value error when nonetype.
        elif int(boat_id) != slips["current_boat"]:
            return (json.dumps(constants.error_miss_boat_this_slip), 404)

        # update the slip info for boat leaving the slip
        slips.update({"current_boat": None})
        client.put(slips)
        return ('', 204)