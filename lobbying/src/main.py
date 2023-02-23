import logging, pickle, sys, getopt, argparse
import datetime
from lobbyingDataPage import *
from lobbyingScraper import *
from settings import *

filename = 'all_current_urls.pkl'

# Grab records_per_year for each year between start_year and end_year
def generate_test_data(start_year = 2005, end_year = 2022, records_per_year = 10):
    all_urls = load_and_update_saved_urls()
    years = list(range(start_year,end_year+1))*records_per_year
    url_iterator = iter(all_urls)
    while years:
        page = PageFactory(next(url_iterator))
        if type(page) == DataPage and page.year in years:
            print(f'Page found, year {page.year}, {len(years)} remaining')
            page.save()
            years.remove(page.year)

def process_saved_urls(offset = 0):
    all_urls = load_and_update_saved_urls()
    process_urls(all_urls, offset=offset)

def scrape_latest_urls():
    new_urls = get_latest_disclosures()
    unique_new_urls = load_and_update_saved_urls(new_urls, return_all=False)
    process_urls(unique_new_urls)

def scrape_recent_urls():
    new_urls = get_recent_disclosures()
    unique_new_urls = load_and_update_saved_urls(new_urls, return_all=False)
    process_urls(unique_new_urls)

def load_and_update_saved_urls(new_urls = None, return_all = True):
    with open(filename, 'rb') as f:
        old_urls = pickle.load(f)
    if new_urls:
        old_urls_set = set(old_urls)
        new_urls_set = set(new_urls).difference(old_urls_set)
        all_urls_set = old_urls_set.union(new_urls_set)
        all_urls = list(all_urls_set)
        new_urls = list(new_urls_set)
        with open(filename, 'wb') as f: pickle.dump(all_urls, f)
    else:
        all_urls = old_urls
    return all_urls if return_all else new_urls

def scrape_urls_from_year(year):
    url_list = get_disclosures_by_year(year)
    load_and_update_saved_urls(url_list)
    process_urls(url_list)

def process_urls(urls, offset = 0):
    for url in urls[offset:]:
        PageFactory(url).save()

def create_list():
    with open(filename, 'rb') as f:
        current_urls = pickle.load(f)

    current_urls= list(current_urls)

    with open(filename, 'wb') as f:
        pickle.dump(current_urls, f)

def parse_arguments():
    verbosity_levels = [logging.ERROR, logging.INFO, logging.DEBUG]
    process_help = """Process saved urls. Can include index to start from"""
    recent_help = """Scrape, save, adn process disclosure reports from the last 2 years"""
    scrape_help = """Scrape, save, and process disclosure reports from a given year from sec.state.ma.us"""
    test_help = """Create test data from saved urls and upload them to the database"""
    verbose_help = "set logging level. Default = 0, max = 2"
    help_msg = f"""Maple Lobbying Scraper"""

    parser = argparse.ArgumentParser(description = help_msg)
    parser.add_argument('-p','--process', help = process_help, nargs='?', const = 0, type=int)
    parser.add_argument('-r', '--recent', help = recent_help, action='store_true')
    parser.add_argument('-t', '--test', help = test_help, action = 'store_true')
    parser.add_argument('-v',"--verbose", help=verbose_help, action='count', default=0)
    parser.add_argument('-s', '--scrape', help = scrape_help)

    args = parser.parse_args()
    logging.basicConfig(level=verbosity_levels[args.verbose])

    if args.process is not None:
        logging.info(f'Processing saved urls starting at index {args.process}')
        process_saved_urls(args.process)
    if args.recent:
        get_recent_disclosures()
    if args.text:
        generate_test_data()
    if args.latest:
        scrape_latest_urls()
    if args.scrape:
        scrape_urls_from_year(args.scrape)

#I want to find and upload five pages of each type for each year.
def generate_test_database():
    current_urls = load_and_update_saved_urls()
    start_year = 2005
    end_year = 2022
    tally = [[0]*3]*(end_year-start_year)

    for url in current_urls:
        page=PageFactory(url)


    for year in range(start_year, end_year+1):
        tables = ['campaign_contributions', 'client_compensation']
        activity_tables = ['pre_2010_lobbying_activity','pre_2016_lobbying_activity','lobbying_activity']
        index = year-start_year
        if year < 2010:
            tables.append(activity_tables[0])
        elif year < 2016:
            tables.append(activity_tables[1])
        else:
            tables.append(activity_tables[2])




if __name__ == "__main__":
    #parse_arguments()
    create_list()

