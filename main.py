import argparse

from easystaff import helpers
from easystaff import library

root = argparse.ArgumentParser(add_help=True)
root.add_argument("-u", "--username", help="your unimi email (e.g. mario.rossi@studenti.unimi.it)", type=str)
root.add_argument("-p", "--password", help="your unimi password", type=str)
actions = root.add_subparsers(title="actions")
actions.required = True
actions.dest = "action"


def argument(*name_or_flags, **kwargs):
    return list(name_or_flags), kwargs


def subcommand(items=None, parent=actions):
    if items is None:
        items = list()

    def decorator(func):
        parser = parent.add_parser(func.__name__.rstrip("_"),
                                   description=func.__doc__,
                                   formatter_class=argparse.RawTextHelpFormatter)
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
def list_(args):
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
def book(args):
    """Book one or more lectures.
Example usages:
book -cf abc -a
book -cf abc --exclude "linguaggi formali e automi"
book -cf abc --date today
book -cf abc --id 123132"""
    if not args.all and not args.date and not args.id:
        raise ValueError("Use --help to see usage")

    es = helpers.login(args, cf_code_required=True)
    lectures = es.get_all_lectures()
    date = helpers.parse_date(args.date)
    booked = []
    args.exclude_day = helpers.parse_weekday(args.exclude_day)
    for lecture in lectures:
        if args.date and date != lecture["date"]:
            continue
        if args.id and lecture["entry_id"] not in args.id:
            continue
        if args.exclude and any([bool(s.lower() in lecture["nome"].lower()) for s in args.exclude]):
            continue
        if lecture["date"].weekday() in args.exclude_day:
            continue
        es.book_lecture(lecture["entry_id"], dummy=args.dry_run)
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
    """Below each library is the service they provide"""
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
    if not args.library_id or not args.service_id or not args.slot_id:
        raise ValueError("Library-id, service-id and slot-id are REQUIRED")
    if not args.username or not args.full_name or not args.fiscal_code:
        raise ValueError("You MUST specify username, full-name and fiscal-code")
    lib = library.Library(args.fiscal_code, args.full_name, args.username)
    lib.book_timeslot(args.library_id, args.service_id, args.slot_id)
    print("Prenotazione effettuata") # I probably need to check the response first


if __name__ == "__main__":
    arguments = root.parse_args()
    arguments.func(arguments)
