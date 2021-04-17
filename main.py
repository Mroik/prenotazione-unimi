import argparse
import os

import easystaff

root = argparse.ArgumentParser(add_help=True)
root.add_argument("-u", "--username", help="your unimi email (e.g. mario.rossi@studenti.unimi.it)", type=str)
root.add_argument("-p", "--password", help="your unimi password", type=str)
actions = root.add_subparsers(title="actions")
actions.required = True
actions.dest = "action"


def argument(*name_or_flags, **kwargs):
    return list(name_or_flags), kwargs


def subcommand(args=None, parent=actions):
    if args is None:
        args = list()

    def decorator(func):
        parser = parent.add_parser(func.__name__.rstrip("_"), description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


def login(args):
    username = os.environ.get("UNIMI_USERNAME", None if not hasattr(args, "username") else args.username)
    password = os.environ.get("UNIMI_PASSWORD", None if not hasattr(args, "password") else args.password)
    if not username or not password:
        return print("PROVIDE USERNAME AND PASSWORD!!1")  # TODO: proper exception
    cf_code = os.environ.get("UNIMI_CF", None if not hasattr(args, "cf") else args.cf)
    return easystaff.EasyStaff(username=username, password=password, cf_code=cf_code)


@subcommand()
def list_(args):
    ef = login(args)
    lectures = ef.get_available_bookings()
    max_lengths = [0, 0, 0, 0]  # used by the simple tabulator
    text = ""
    for lecture in lectures:
        date_str = lecture["data"].ljust(max_lengths[0])
        hours_str = f"{lecture['ora_inizio']}-{lecture['ora_fine']}".ljust(max_lengths[1])
        room_str = lecture["aula"].ljust(max_lengths[2])
        lecture_str = lecture["nome"].ljust(max_lengths[3])
        max_lengths = [
            len(date_str) if len(date_str) > max_lengths[0] else max_lengths[0],
            len(hours_str) if len(hours_str) > max_lengths[1] else max_lengths[1],
            len(room_str) if len(room_str) > max_lengths[2] else max_lengths[2],
            len(lecture_str) if len(lecture_str) > max_lengths[3] else max_lengths[3],
        ]
        text += "\n" + "\t".join([date_str, hours_str, room_str, lecture_str])
    text = "\t".join([
        "Date".ljust(max_lengths[0]),
        "Hours".ljust(max_lengths[1]),
        "Room".ljust(max_lengths[2]),
        "Lecture name".ljust(max_lengths[3])
    ]) + "\n" + "\t".join([(n * "-").ljust(n) for n in max_lengths]) + text
    print(text)


@subcommand([argument("--date", "-d"), argument("--cf")])
def book(args):
    pass


if __name__ == "__main__":
    arguments = root.parse_args()
    arguments.func(arguments)
