import argparse
import json
from datetime import datetime

from src import helpers
from src import silab

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
def list_lessons(args):
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


@subcommand()
def list_silab(args):
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
            if date.weekday() in args.exclude_day:
                continue
            if lab.book_slot(slot["slotid"]):
                print("Booked {} {}".format(date.date(), slot["daytime"]))
    else:
        for id_ in args.id:
            if lab.book_slot(id_):
                print("Booked slot {}".format(id_))
            else:
                print("Couldn't book slot {}".format(id_))


def main():
    arguments = root.parse_args()
    arguments.func(arguments)


if __name__ == "__main__":
    main()
