import os
from datetime import datetime, timedelta

from . import EasyStaff


def print_lectures(lectures, just_booked=False):
    # used by the tabulator; probably bad code but it works just fine...
    max_lengths = [len("ID"), len("Date"), len("Hours"), len("Room"),
                   len("Lecture name"), len("Seats left"), len("Booked?")]
    text = ""
    for lecture in lectures:
        fix_booked = not lecture["prenotata"] and just_booked
        id_str = (str(lecture["entry_id"]))
        date_str = lecture["date"].strftime("%d/%m/%Y")
        hours_str = f"{lecture['ora_inizio']}-{lecture['ora_fine']}"
        room_str = lecture["aula"]
        lecture_str = lecture["nome"]
        seats_left_str = f"{lecture['capacita'] - lecture['presenti'] - 1 if fix_booked else 0}/{lecture['capacita']}"
        booked = ("yes️" if lecture["prenotata"] or fix_booked else "no")
        max_lengths = [
            len(id_str) if len(id_str) > max_lengths[0] else max_lengths[0],
            len(date_str) if len(date_str) > max_lengths[1] else max_lengths[1],
            len(hours_str) if len(hours_str) > max_lengths[2] else max_lengths[2],
            len(room_str) if len(room_str) > max_lengths[3] else max_lengths[3],
            len(lecture_str) if len(lecture_str) > max_lengths[4] else max_lengths[4],
            len(seats_left_str) if len(seats_left_str) > max_lengths[5] else max_lengths[5],
            len(booked) if len(booked) > max_lengths[6] else max_lengths[6],
        ]
    # ...ok, this is bad code :/
    for lecture in lectures:
        id_str = (str(lecture["entry_id"])).ljust(max_lengths[0])
        date_str = lecture["date"].strftime("%d/%m/%Y").ljust(max_lengths[1])
        hours_str = f"{lecture['ora_inizio']}-{lecture['ora_fine']}".ljust(max_lengths[2])
        room_str = lecture["aula"].ljust(max_lengths[3])
        lecture_str = lecture["nome"].ljust(max_lengths[4])
        seats_left_str = f"{lecture['capacita'] - lecture['presenti']}/{lecture['capacita']}".ljust(max_lengths[5])
        booked = ("yes️" if lecture["prenotata"] else "no").ljust(max_lengths[6])
        text += "\n" + "\t".join([id_str, date_str, hours_str, room_str, lecture_str, seats_left_str, booked])
    text = "\t".join([
        "ID".ljust(max_lengths[0]),
        "Date".ljust(max_lengths[1]),
        "Hours".ljust(max_lengths[2]),
        "Room".ljust(max_lengths[3]),
        "Lecture name".ljust(max_lengths[4]),
        "Seats left".ljust(max_lengths[5]),
        "Booked?".ljust(max_lengths[6]),
    ]) + "\n" + "\t".join([(n * "-").ljust(n) for n in max_lengths]) + text
    print(text)


def login(args, cf_code_required=False):
    username = os.environ.get("UNIMI_USERNAME", None if not hasattr(args, "username") else args.username)
    password = os.environ.get("UNIMI_PASSWORD", None if not hasattr(args, "password") else args.password)
    if not username:
        raise ValueError("Please provide your UniMi username via the --username parameter or "
                         "the UNIMI_USERNAME environment variable.")
    if not password:
        raise ValueError("Please provide your UniMi password via the --password parameter or "
                         "the UNIMI_PASSWORD environment variable.")
    cf_code = os.environ.get("UNIMI_CF", None if not hasattr(args, "fiscal_code") else args.fiscal_code)
    if cf_code_required and not cf_code:
        raise ValueError("Please provide your italian fiscal code via the --fiscal-code parameter or "
                         "the UNIMI_CF environment variable.")
    return EasyStaff(username=username, password=password, cf_code=cf_code)


def parse_date(date):
    if not date:
        return date
    if date == "today":
        return datetime.today().date()
    elif date == "tomorrow":
        return (datetime.today() + timedelta(days=1))
    parsed = datetime.strptime(date, "%d/%m/%Y")
    if not parsed:
        raise ValueError("The provided date is invalid, use the %d/%m/%Y format.")
    if parsed < datetime.today().date():
        raise ValueError("The provided date is in the past.")
    return parsed


def parse_weekday(days):
    ris = []
    for day in days:
        if type(day) == int:
            ris.append(day)
        if day == "monday":
            ris.append(0)
        if day == "tuesday":
            ris.append(1)
        if day == "wednesday":
            ris.append(2)
        if day == "thursday":
            ris.append(3)
        if day == "friday":
            ris.append(4)
        if day == "saturday":
            ris.append(5)
        if day == "sunday":
            ris.append(6)
    return ris
