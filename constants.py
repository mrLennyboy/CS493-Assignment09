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

# boat name type is not string type
error_boat_name_type = {"Error": "Boat name is not string type"}

# boat name length exceeds char length 33 (400)
error_boat_name_length = {"Error": "Boat name length is greater than 33 characters in length"}

# boat type is not string type
error_boat_type_str = {"Error": "Boat type description is not string type"}

# boat type length exceeds char length 33 (400)
error_boat_type_length = {"Error": "Boat type length is greater than 33 characters in length"}

# boat length data type is not int
error_boat_length_type = {"Error": "Boat length data type is not int type"}

# boat length is out of range 0 - 10,000 ft
error_boat_length_limit = {"Error": "Boat length is out of range, it can not be less than 0 or greater than 10,000 ft"}

# boat name input val for name is invalid. Should be only alpha char and space, no special char or nums
error_boat_name_invalid = {"Error": "Boat name is invalid, needs to be only alpha characters and spaces."}

# boat type input val for name is invalid. Should be only alpha char and space, no special char or nums
error_boat_type_invalid = {"Error": "Boat type description is invalid, needs to be only alpha characters and spaces."}

# method not allowed error
error_method_not_allowed = {"Error": "Method not allowed"}