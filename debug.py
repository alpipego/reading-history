import argparse

from reading_history import firefox
from reading_history.firefox import read_history
from reading_history.url_sorter import UrlSorter


def print_urls_raw():
    entries = read_history()
    for url, title, desc in entries:
        print(url)


def print_urls():
    entries = read_history()
    url_sorter = UrlSorter()
    for url, title, desc in entries:
        try:
            url = url_sorter.is_valid(url)
            print(url)
        except ValueError:
            pass


def print_urls_bad():
    entries = read_history()
    url_sorter = UrlSorter()
    for url, title, desc in entries:
        try:
            url_sorter.is_valid(url)
        except ValueError as e:
            print(e)

def main():
    firefox.copy_places_db()

    parser = argparse.ArgumentParser(description='Show more info about your history.')
    parser.add_argument('--urls', action='store_true', help='List all URLs considered for the reading history')
    parser.add_argument('--urls-raw', action='store_true', help='List all URLs retrieved from the Firefox history')
    parser.add_argument('--urls-bad', action='store_true', help='List all URLs that are considered invalid')
    args = parser.parse_args()

    if args.urls:
        print_urls()
    elif args.urls_raw:
        print_urls_raw()
    elif args.urls_bad:
        print_urls_bad()
    else:
        print("Normal mode.")


if __name__ == "__main__":
    main()
