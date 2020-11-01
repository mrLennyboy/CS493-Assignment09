boats = "boats"
loads = "loads"

# keys for boat response body
check_keys = {"name", "type", "length"}

# keys for loads response body
check_keys_3 = {"weight", "content", "delivery_date"}


# Errors
# Missing an attribute (boat & loads)
error_miss_attribute = {"Error": "The request object is missing at least one of the required attributes"}

# No boat with boat #id
error_miss_bID = {"Error": "No boat with this boat_id exists"}

# No load with load #id
error_miss_loadID = {"Error": "No load with this load_id exists"}

# Load or boat does not exist
error_miss_load_boat = {"Error": "The specified boat and/or load does not exist"}

# Load already assigned to a boat
error_load_already_assigned = {"Error": "The load has already been assigned to a boat"}

# The boat data does not match load carrier data for removal
error_miss_boat_load_del = {"Error": "No boat with this boat_id is carrying this load with this load_id"}

# The load data does not match boat data for removal
error_miss_load_boat_del = {"Error": "No load with this load_id is associated with the boat and this boat_id"}