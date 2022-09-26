import argparse
from easystaff import Easystaff


def list_lessons(args):
    a = Easystaff()
    a.login(args.u, args.p)
    lessons = a.get_lessons()
    print(lessons)


def book_lesson(args):
    a = Easystaff()
    a.login(args.u, args.p)
    a.book_lesson(args.cf, args.entry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(required=True)

    list_l = sub.add_parser("list")
    list_l.add_argument("-u", help="email", required=True)
    list_l.add_argument("-p", help="password", required=True)
    list_l.set_defaults(func=list_lessons)

    book_l = sub.add_parser("book")
    book_l.add_argument("-cf", help="fiscal code", required=True)
    book_l.add_argument("entry", help="the id of the lesson")
    book_l.set_defaults(func=book_lesson)

    args = parser.parse_args()
    args.func(args)
