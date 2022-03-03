import re
import csv
import time
import argparse
from tqdm import tqdm
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from datetime import datetime

from webdriver_manager.firefox import GeckoDriverManager

TYPE_TO_URL_MAP = {
    "ld": "https://hsld.debatecoaches.org/Main/",
    "policy": "https://hspolicy.debatecoaches.org/",
    "pf": "https://hspf.debatecoaches.org/Main/",
}

all_emails = []

def strip_html(data):

    p = re.compile(r'<.*?>')

    return p.sub('', data)

def extract_emails(data):

    return re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', data)

def flatten(lst):

    return [item for sublist in lst for item in sublist]

def clean_emails(emails):

    clean_emails = []
    tlds = [".com", ".edu", ".org", ".net"]
    
    for email in emails:

        for tld in tlds:

            if tld in email:

                clean_emails.append(email[:email.index(tld)+4])
                continue

    return set(clean_emails)

def create_browser():

    options = FirefoxOptions()
    options.add_argument("--headless")

    s=Service(GeckoDriverManager().install())
    browser = webdriver.Firefox(service=s, options=options)
    browser.implicitly_wait(5)
    print("Made browser...")

    return browser

def main(browser, url):

    browser.get(url)
    print("Got webpage...")

    schools = browser.find_elements(by=By.CSS_SELECTOR, value='span[class="wikilink"] a')
    school_pages = [i.get_attribute('href') for i in schools]
    first_school = [1 if 'recently' in url.lower() else 0 for url in school_pages].index(1)
    school_pages = school_pages[first_school+1:]

    for school_page in tqdm(school_pages):

        print(f"Opening {school_page}")

        browser.get(school_page)

        team_details = browser.find_elements(by=By.CSS_SELECTOR, value='table[id="tblTeams"] span[class="wikilink"] a')
        team_detail_pages = [i.get_attribute('href') for i in team_details]
        
        for team_detail_page in team_detail_pages:

            # print(f"Opening {team_detail_page}")

            browser.get(team_detail_page)

            # They have a typo in this CSS Selector LOL, don't fix.
            contact_info = browser.find_elements(by=By.CSS_SELECTOR, value='table[id="tblCites"] tr')
            table_content = [i.get_attribute('innerHTML') for i in contact_info]
            table_content = [strip_html(data) for data in table_content]
            emails = flatten([extract_emails(data) for data in table_content])

            all_emails.extend(emails)

    browser.quit()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--type", help="which site to visit. one of: ['ld', 'policy', 'pf']", required=True)

    args = parser.parse_args()

    if args.type and args.type in TYPE_TO_URL_MAP.keys():
        print(f"site type: {args.type}")

        browser = create_browser()

        try:

            main(browser, TYPE_TO_URL_MAP[args.type])

            all_emails = clean_emails(all_emails)

            print(all_emails)

            # TODO: Instead of just printing the emails, save them to individual files.
            # These files should be in a directory called 'ndca_emails', and name them 'pf.txt', 'policy.txt', and 'ld.txt'.

        except Exception as e:
            browser.quit()
            raise e

    else:
        raise ValueError("Missing or invalid arguments! Run `python3 ndca_scraper.py --help`.")
