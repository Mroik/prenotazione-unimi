import easystaff

import sys
import os

# Example usage
if len(sys.argv) == 1:
    es = easystaff.EasyStaff(
            username = os.environ["UNIMI_USERNAME"],
            password = os.environ["UNIMI_PASSWORD"],
            cf_code = os.environ["UNIMI_CF"],
    )
else:
    excludes = []
    for i in range(4, len(sys.argv)):
        excludes.append(sys.argv[i])
    es = easystaff.EasyStaff(
            username = sys.argv[1],
            password = sys.argv[2],
            cf_code = sys.argv[3],
            excludes = excludes
    )
for lecture_id in es.get_available_bookings():
    es.book_lecture(lecture_id)
