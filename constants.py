boats = "boats"


# keys for boat response body
check_keys = {"name", "type", "length"}

# Errors
# Missing an attribute (boat & loads)
error_miss_attribute = {"Error": "The request object is missing at least one of the required attributes"}

# No boat with boat #id
error_miss_bID = {"Error": "No boat with this boat_id exists"}