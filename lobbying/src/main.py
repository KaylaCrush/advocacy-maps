import logging, pickle, sys, getopt, argparse
import datetime
from lobbyingDataPage import *
from lobbyingScraper import *
from settings import *

filename = 'all_current_urls.pkl'

def process_saved_urls(offset = 0):
    all_urls = load_and_update_saved_urls()
    process_urls(all_urls, offset=offset)

def scrape_latest_urls():
    new_urls = get_latest_disclosures()
    load_and_update_saved_urls(new_urls)
    process_urls(new_urls)

def load_and_update_saved_urls(new_urls = None):
    with open(filename, 'rb') as f:
        current_urls = pickle.load(f)
    if new_urls:
        current_urls = current_urls.union(set(new_urls))
        with open(filename, 'wb') as f: pickle.dump(current_urls, f)
    return current_urls

def scrape_urls_from_year(year):
    url_list = get_disclosures_by_year(year)
    load_and_update_saved_urls(url_list)
    process_urls(url_list)

def process_urls(urls, offset = 0):
    for url in list(urls)[offset:]:
        PageFactory(url).save()

def create_set():
    with open(filename, 'rb') as f:
        current_urls = pickle.load(f)

    current_urls= set(current_urls)

    with open(filename, 'wb') as f:
        pickle.dump(current_urls, f)

def parse_arguments():
    verbosity_levels = [logging.ERROR, logging.INFO, logging.DEBUG]
    process_help = """Process saved urls. Can include index to start from"""
    latest_help = """Scrape, save, and process latest urls from sec.state.ma.us"""
    scrape_help = """Scrape, save, and process urls from a given year from sec.state.ma.us"""
    verbose_help = "increase output verbosity"
    help_msg = f"""Maple Lobbying Scraper"""

    parser = argparse.ArgumentParser(description = help_msg)
    parser.add_argument('-p','--process', help = process_help, nargs='?', const = 0, type=int)
    parser.add_argument('-l','--latest', help = latest_help, nargs = '?')
    parser.add_argument('-v',"--verbose", help=verbose_help, action='count', default=0)
    parser.add_argument('-s', '--scrape', help = scrape_help)

    args = parser.parse_args()
    logging.basicConfig(level=verbosity_levels[args.verbose])

    if args.process is not None:
        logging.info(f'Processing saved urls starting at index {args.process}')
        process_saved_urls(args.process)
    if args.latest:
        scrape_latest_urls()
    if args.scrape:
        scrape_urls_from_year(args.scrape)

if __name__ == "__main__":
    parse_arguments()

