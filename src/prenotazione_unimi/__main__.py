import argparse
from prenotazione_unimi.easystaff import Easystaff


def list_lessons(args):
    a = Easystaff()
    a.login(args.u, args.p)
    lessons = a.get_lessons()
    for day in lessons:
        print(day["data"])
        for lesson in day["prenotazioni"]:
            print(f"\t{lesson['nome']} {lesson['ora_inizio']} {lesson['entry_id']} | prenotata: {lesson['prenotata']}")


def book_lesson(args):
    a = Easystaff()
    a.login(args.u, args.p)

    if args.a:
        lessons = a.get_lessons()
        for lesson in lessons:
            for en in lesson["prenotazioni"]:
                a.book_lesson(args.cf, en["entry_id"])
                print(f"Booked \"{en['nome']}\" lesson")

    elif args.e:
        a.book_lesson(args.cf, args.e)
    else:
        print("Choose at least one flag between -a and -e")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="email", required=True)
    parser.add_argument("-p", help="password", required=True)

    sub = parser.add_subparsers(required=True)

    list_l = sub.add_parser("list")
    list_l.set_defaults(func=list_lessons)

    book_l = sub.add_parser("book")
    book_l.add_argument("-cf", help="fiscal code", required=True)
    book_l.add_argument("-e", help="the id of the lesson")
    book_l.add_argument("-a", help="book everything available", action="store_true")
    book_l.set_defaults(func=book_lesson)

    args = parser.parse_args()
    args.func(args)
