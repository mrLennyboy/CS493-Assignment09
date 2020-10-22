'''
Name:   Jasper Wong
Date:   10-19-2020
Source: CS 493 W03 example, Google Cloud Enginer docs

'''
from google.cloud import datastore
from flask import Flask, request
import json
import constants

app = Flask(__name__)
client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /boats and /slips to use this API"\

@app.route('/boats', methods=['POST','GET'])
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
        new_boat.update({"id": new_boat.key.id, "self": self_url})
        #return tuple of new_boat json string and status code 201
        return (json.dumps(new_boat), 201)

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
             # build self_url from request info and boat entity key id
            self_url = str(request.base_url) + '/' + str(e.key.id)
            # update new_boat json with id and self url
            e.update({"self": self_url})
        return (json.dumps(results), 200)
    else:
        return 'Method not recogonized'

@app.route('/boats/<boat_id>', methods=['GET', 'PATCH', 'DELETE'])
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

@app.route('/slips', methods=['POST', 'GET'])
def slips_post_get():
    if request.method == 'POST':
        content = request.get_json()
        # use comparison operator for key value check, True if all keys present
        if not (content.keys()) >= constants.check_keys_2:
            return (json.dumps(constants.error_miss_num), 400)

        # create slips datastore entity
        new_slip = datastore.entity.Entity(key=client.key(constants.slips))
        new_slip.update({"number": content["number"], "current_boat": None})
        # put new slip entity to datastore
        client.put(new_slip)

        # build self_url from request info and new_slip entity key id
        self_url = str(request.base_url) + '/' + str(new_slip.key.id)
        # update new_slip json with id and self url
        new_slip.update({"id": new_slip.key.id, "self": self_url})
        #return tuple of new_slip json string and status code 201`
        return(json.dumps(new_slip), 201)

    elif request.method == 'GET':
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
             # build self_url from request info and slips entity key id
            self_url = str(request.base_url) + '/' + str(e.key.id)
            # update new_boat json with id and self url
            e.update({"self": self_url})
        return (json.dumps(results), 200)

    else:
        return 'Method not recogonized'

@app.route('/slips/<slip_id>', methods=['GET', 'DELETE'])
def slips_get_delete(slip_id):
    if request.method == 'GET':
        slip_key = client.key(constants.slips, int(slip_id))
        slips = client.get(key=slip_key)
        # if slips entity is nonetype return error message and status code
        if slips is None:
            return(json.dumps(constants.error_miss_sID), 404)
        # build self_url from request url
        self_url = str(request.base_url)
        slips.update({"id": slips.key.id, "self": self_url})
        results = json.dumps(slips)
        return (results, 200)
    
    elif request.method == 'DELETE':
        slip_key = client.key(constants.slips, int(slip_id))
        # get slip entity with the key requested
        slips = client.get(key=slip_key)
        # if slip entity is noneType (id doesn't exist) return error message and status code
        if slips is None:
            return (json.dumps(constants.error_miss_sID), 404)
        # delete slip by id on datastore side
        client.delete(slip_key)
        #return nothing except 204 status code
        return ('', 204)

    else:
        return 'Method not recognoized'

@app.route('/slips/<slip_id>/<boat_id>', methods=['PUT', 'DELETE'])
def slips_boat_put_delete(slip_id, boat_id):
    # what method to stop a boat from being assigned to multiple slip/how will I track? dict?
    if request.method == 'PUT':
        slip_key = client.key(constants.slips, int(slip_id))
        slips = client.get(key=slip_key)

        boat_key = client.key(constants.boats, int(boat_id))
        boats = client.get(key=boat_key)

        # if boats or slips entity is nonetype return error message and status code
        if slips is None or boats is None:
            return (json.dumps(constants.error_miss_slip_boat), 404)

        # if slip entity current_boat is null then return 403 and error
        elif slips["current_boat"] is not None: 
            return (json.dumps(constants.error_slip_not_empty), 403)

        # very inefficent method to search slips and prevent multiple assignments
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            if e["current_boat"] == int(boat_id):
                return(json.dumps(constants.error_one_boat_slip), 403)

        # slips.update({"current_boat": int(boat_id)}) 
        # updated slips to add numbers in update for 'PUT'
        slips.update({"current_boat": int(boat_id), "number": slips["number"]})
        client.put(slips)
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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)