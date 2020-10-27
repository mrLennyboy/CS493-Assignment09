boats = "boats"
slips = "slips" # (from HW03 delete)
loads = "loads"

# keys for boat response body
check_keys = {"name", "type", "length", "loads"}

# keys for slip response body (from HW03 delete)
check_keys_2 = {"number"}

# keys for loads response body
check_keys_3 = {"weight", "content", "delivery_date"}


# Errors
# Missing an attribute (boat & loads)
error_miss_attribute = {"Error": "The request object is missing at least one of the required attributes"}

# No boat with boat #id
error_miss_bID = {"Error": "No boat with this boat_id exists"}

# Missing num attribute (slip)
error_miss_num = {"Error": "The request object is missing the required number"}

# No slip with slip #id
error_miss_sID = {"Error": "No slip with this slip_id exists"}

# Slip not empty
error_slip_not_empty = {"Error": "The slip is not empty"}

# Slip or boat does not exist
error_miss_slip_boat = {"Error": "The specified boat and/or slip does not exist"}

# Boat with boat_id is at the slip with slip_id (delete, i made typo with the and this)
error_miss_boat_at_slip = {"Error": "No boat with this boat_id is at the slip with the slip_id"}

# Non-existant boat try top depart from slip (to match 'DEL boat not at slip tries to depart 404')
error_miss_boat_this_slip = {"Error": "No boat with this boat_id is at the slip with this slip_id"}

# boat can't be moored to more than one boat slip
error_one_boat_slip = {"Error": "The specified boat is already moored at another slip"}

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