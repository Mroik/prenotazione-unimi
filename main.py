import easystaff

import os

# Example usage
es = easystaff.EasyStaff(
    username=os.environ["UNIMI_USERNAME"],
    password=os.environ["UNIMI_PASSWORD"],
    cf_code=os.environ["UNIMI_CF"],
)
print(es.get_available_bookings())
