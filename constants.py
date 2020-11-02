boats = "boats"


# keys for boat response body
check_keys = {"name", "type", "length"}

# Errors
# Missing an attribute (boat & loads)
error_miss_attribute = {"Error": "The request object is missing at least one of the required attributes"}

# No boat with boat #id
error_miss_bID = {"Error": "No boat with this boat_id exists"}

# Boat with name already exists
error_boat_name_exists = {"Error": "This boat name already exists"}

# unsupported accept type (406). Client requests medita type the server can't offer.
error_unsupported_accept_type = {"Error": "Not Acceptable"}

# unsupported media type (415). For request not JSON
error_unsupported_media_type = {"Error": "Unsupported Media Type"}

