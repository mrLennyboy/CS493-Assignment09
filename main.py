'''
Name:   Jasper Wong
Date:   10-24-2020`
Source: CS 493 W03 HW, CS CS 493 W04 Ex., Google Cloud Platform docs

'''
from google.cloud import datastore
from flask import Flask, request
import json
import constants
import boat
import load

app = Flask(__name__)
# register blueprints on application
app.register_blueprint(boat.bp)
app.register_blueprint(load.bp)
client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /boats and /slips to use this API"\

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