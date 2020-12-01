boats = "boats"
loads = "loads"
reg_users = "reg_users"

# keys for boat response body
check_keys = {"name", "type", "length", "public"}

# keys for loads response body
check_keys_3 = {"weight", "content", "delivery_date"}

# Errors
# Missing an attribute (boat & loads)
error_miss_attribute = {"Error": "The request object is missing at least one of the required attributes"}

# No boat with boat #id
error_miss_bID = {"Error": "No boat with this boat_id exists"}

# Boat with name already exists
error_boat_name_exists = {"Error": "This boat name already exists"}

# unsupported accept type (406 Not Acceptable). Client requests medita type the server can't offer.
error_unsupported_accept_type = {"Error": "Client requests media type the server can't offer"}

# unsupported media type (415). For request not JSON. Client send unsupported media typ to the server
# the server will respond to the client it is not acceptable
error_unsupported_media_type = {"Error": "Client has sent Unsupported Media Type"}

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
error_method_not_allowed = {"Error": "Method not allowed for this endpoint"}

# boat public data type is not int
error_boat_public_type = {"Error": "Boat public type is not bool type"}

# load content description data type is not string type
error_content_desc_type = {"Error": "Load content description data type is not str type"}

# content description length exceeds char length 128 (400)
error_content_desc_length = {"Error": "Load description length is greater than 128 characters in length"}

# load description input val for content is invalid. Should be only alpha char and space, no special char or nums
error_content_desc_invalid = {"Error": "Load description is invalid, needs to be only alpha characters and spaces."}

# check delivery date input data type as xx/xx/xxxx (MM/DD/YYYY) and delivery date char length
error_delivery_date_str = {"Error": "Delivery date type is not str type"}

# char length for delivery date shall be 10 char with num and special char no less or greater
error_delivery_date_length = {"Error": "Delivery date char length is to 10 char length"}

# load type input val for delivery date is invalid. Should be only alpha char and space, no special char or nums
error_delivery_date_invalid = {"Error": "Delivery date is invalid, needs to be MM/DD/YYYY format"}

# load weight data type is not int
error_load_weight_type = {"Error": "Load weight data type is not int type"}

# load weight is out of range 0 - 100,000 lbs
error_load_weight_limit = {"Error": "Load weight is out of range, it can not be less than 0 or greater than 100,000 lbs"}

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