import argparse
import json
from datetime import datetime

from .core import library
from .core import helpers
from .core import silab

root = argparse.ArgumentParser(add_help=True)
root.add_argument("-u", "--username", help="your unimi email (e.g. mario.rossi@studenti.unimi.it)", type=str)
root.add_argument("-p", "--password", help="your unimi password", type=str)
actions = root.add_subparsers(required=True, metavar="ACTION", dest="action")


def argument(*name_or_flags, **kwargs):
    return list(name_or_flags), kwargs


def subcommand(items=None, parent=actions):
    if items is None:
        items = list()

    def decorator(func):
        parser = parent.add_parser(func.__name__.rstrip("_"),
                help=func.__doc__)
        for item in items:
            if type(item) is list:
                group = parser.add_mutually_exclusive_group()
                for arg in item:
                    group.add_argument(*arg[0], **arg[1])
                continue
            parser.add_argument(*item[0], **item[1])
        parser.set_defaults(func=func)
    return decorator


@subcommand()
def list_lessons(args):
    """Lists available lessons based on your profile"""
    es = helpers.login(args)
    lectures = es.get_all_lectures()
    helpers.print_lectures(lectures)


@subcommand([
    argument(
        "--dry-run", "-D",
        help="dry run, don't really book anything",
        action='store_true',
    ),
    argument(
        "--fiscal-code", "-cf",
        help="your IT fiscal code (e.g. RSAMRA70A41F205Z). you can use the UNIMI_CF environment variable, too."
    ),
    [
        argument(
            "--all", "-a",
            help="book ALL the available lectures (use this with responsibility)",
            action="store_true",
        ),
        argument(
            "--date", "-d",
            help="book the lectures of a specificed date (e.g. 'today', 'tomorrow', '31/12/2020')"
        ),
        argument(
            "--id",
            help="book a specific lesson with its ID",
            nargs='+',
            type=int,
        )
    ],
    argument(
        "--exclude", "-e",
        help="exclude the lectures who's names contain the specified string",
        nargs='+',
    ),
    argument(
        "--exclude-day", "-ed",
        help="exclude the lectures of the day i.e. monday",
        nargs='+',
    ),
])
def book_lesson(args):
    """Book one or more lectures."""
    if not args.all and not args.date and not args.id:
        raise ValueError("Use --help to see usage")

    es = helpers.login(args, cf_code_required=True)
    lectures = es.get_all_lectures()
    date = helpers.parse_date(args.date)
    booked = []
    if args.exclude_day:
        args.exclude_day = helpers.parse_weekday(args.exclude_day)
    for lecture in lectures:
        if args.date and date != lecture["date"]:
            continue
        if args.id and lecture["entry_id"] not in args.id:
            continue
        if args.exclude and any([bool(s.lower() in lecture["nome"].lower()) for s in args.exclude]):
            continue
        if args.exclude_day and lecture["date"].weekday() in args.exclude_day:
            continue
        ris = es.book_lecture(lecture["entry_id"], dummy=args.dry_run)
        if ris:
            lecture["prenotata"] = True
        booked.append(lecture)
    if len(booked) > 0:
        print(f"Booked {len(booked)} lectures.")
        helpers.print_lectures(booked, just_booked=True)
    else:
        print("No lectures matched the provided filters.")


@subcommand([
    argument(
        "--full-name", "-fn",
        help="Your full name e.g. \"First_name [Middle_name] Last_name\"",
    ),
    argument(
        "--fiscal-code", "-cf",
        help="Your IT fiscal-code",
    ),
])
def list_libraries(args):
    """Lists available libraries and related services"""
    if not args.username or not args.full_name or not args.fiscal_code:
        raise ValueError("You MUST specify username, full-name and fiscal-code")
    lib = library.Library(args.fiscal_code, args.full_name, args.username)
    results, services = lib.get_available_libraries()
    print("ID\tLibrary")
    print("Services")
    for lib_id in results:
        if lib_id == "":
            continue
        print(lib_id + "\t" + results[lib_id])
        for service_id in services[lib_id]:
            print(service_id, end="\t")
        print()


@subcommand()
def list_silab(args):
    """Lists available timeslots for booking for SiLab"""
    lab = silab.SiLab()
    if args.username and args.password:
        lab.login(args.username, args.password)
    print("Date\t\tDaytime\t\tSeats left\tBooked\tID")
    data = lab.get_slots()[0]
    capacity = data["capacity"]
    for slot in data["slots"]:
        if slot["daytime"] == "afternoon":
            print(f'{slot["date"]}\t{slot["daytime"]}\t{capacity - slot["bookings"]}\t\t{slot["bookedbyme"]}\t{slot["slotid"]}')
        else:
            print(f'{slot["date"]}\t{slot["daytime"]}\t\t{capacity - slot["bookings"]}\t\t{slot["bookedbyme"]}\t{slot["slotid"]}')


@subcommand([
    argument(
        "--all", "-a",
        help="Book everything (Avoid using this)",
        action="store_true"
    ),
    argument(
        "--id",
        help="Book by ID",
        nargs="+"
    ),
    argument(
        "--exclude-day", "-ed",
        help="If using --all this excludes by day",
        nargs="+"
    )
])
def book_silab(args):
    """Books a seat in SiLab"""
    if not args.all and not args.id:
        raise ValueError("Use --help")
    if not args.username or not args.password:
        raise ValueError("Insert login credentials")
    lab = silab.SiLab()
    lab.login(args.username, args.password)
    if args.exclude_day:
        args.exclude_day = helpers.parse_weekday(args.exclude_day)
    if args.all:
        for slot in lab.get_slots()[0]["slots"]:
            if slot["bookedbyme"]:
                continue
            date = datetime.strptime(slot["date"], "%Y-%m-%d")
            if args.exclude_day and date.weekday() in args.exclude_day:
                continue
            if lab.book_slot(slot["slotid"]):
                print("Booked {} {}".format(date.date(), slot["daytime"]))
    else:
        for id_ in args.id:
            if lab.book_slot(id_):
                print("Booked slot {}".format(id_))
            else:
                print("Couldn't book slot {}".format(id_))


@subcommand([
    argument(
        "--all", "-a",
        help="Book everything (Avoid using this)",
        action="store_true"
    ),
    argument(
        "--id",
        help="Book by ID",
        nargs="+"
    )
])
def unbook_silab(args):
    """Cancels a booking for SiLab"""
    if not args.all and not args.id:
        raise ValueError("Use --help")
    if not args.username or not args.password:
        raise ValueError("Insert login credentials")
    lab = silab.SiLab()
    lab.login(args.username, args.password)
    if args.all:
        for slot in lab.get_slots()[0]["slots"]:
            if not slot["bookedbyme"]:
                continue
            if lab.unbook_slot(slot["slotid"]):
                print("Unbooked {} {}".format(slot["date"], slot["daytime"]))
    else:
        for id_ in args.id:
            if lab.unbook_slot(id_):
                print("Unbooked slot {}".format(id_))
            else:
                print("Couldn't unbook slot {}".format(id_))


@subcommand([
    argument(
        "--full-name", "-fn",
        help="Your full name",
    ),
    argument(
        "--fiscal-code", "-cf",
        help="Your IT fiscal-code",
    ),
    argument(
        "--library-id", "-libid",
        help="The library ID to choose",
    ),
    argument(
        "--service-id", "-servid",
        help="The service ID of the library",
    ),
])
def list_library_timeslots(args):
    """Lists available bookings for a specific library"""
    if not args.library_id or not args.service_id:
        raise ValueError("Both library-id and service-id are REQUIRED")
    if not args.username or not args.full_name or not args.fiscal_code:
        raise ValueError("You MUST specify username, full-name and fiscal-code")
    lib = library.Library(args.fiscal_code, args.full_name, args.username)
    print("slotID\t\tTime")
    for slot in lib.get_available_timeslots(args.library_id, args.service_id):
        print(int(slot.timestamp()), slot.strftime("%d-%m-%Y %H:%M"), sep="\t")


@subcommand([
    argument(
        "--full-name", "-fn",
        help="Your full name",
    ),
    argument(
        "--fiscal-code", "-cf",
        help="Your IT fiscal-code",
    ),
    argument(
        "--library-id", "-libid",
        help="The library ID to choose",
    ),
    argument(
        "--service-id", "-servid",
        help="The service ID of the library",
    ),
    argument(
        "--slot-id", "-sid",
        help="Slot ID",
    ),
])
def book_library(args):
    """Books a seat in the library"""
    if not args.library_id or not args.service_id or not args.slot_id:
        raise ValueError("Library-id, service-id and slot-id are REQUIRED")
    if not args.username or not args.full_name or not args.fiscal_code:
        raise ValueError("You MUST specify username, full-name and fiscal-code")
    lib = library.Library(args.fiscal_code, args.full_name, args.username)
    lib.book_timeslot(args.library_id, args.service_id, args.slot_id)
    print("Prenotazione effettuata") # I probably need to check the response first


@subcommand()
def silab_penalty(args):
    """Shows your penalties for SiLab"""
    if not args.username and not args.password:
        raise ValueError("Username and password are required for this action")
    lab = silab.SiLab()
    lab.login(args.username, args.password)
    abse, maxbook = lab.get_penalty()
    print("Absences:", abse)
    print("Max bookings allowed:", maxbook)


@subcommand([
    argument(
        "--room", "-r", type=int, required=True,
        help="ID of the room to attend"
    )
])
def confirm_silab(args):
    """Confirms your attendance at SiLab"""
    if not args.username and not args.password:
        raise ValueError("Username and password are required for this action")
    lab = silab.SiLab()
    lab.login(args.username, args.password)
    print(lab.confirm_silab(args.room))


def main():
    arguments = root.parse_args()
    arguments.func(arguments)


if __name__ == "__main__":
    main()
