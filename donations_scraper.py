import csv
import time
import argparse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from datetime import datetime


from webdriver_manager.firefox import GeckoDriverManager

def create_browser():

    options = FirefoxOptions()
    options.add_argument("--headless")

    s=Service(GeckoDriverManager().install())
    browser = webdriver.Firefox(service=s, options=options)
    browser.implicitly_wait(5)
    print("Made browser...")

    return browser

def main(browser, url, username, password):

    browser.get(url)
    print("Got webpage...")

    email = browser.find_elements(by=By.CLASS_NAME, value="username")[0]
    email.send_keys(username)

    pwd = browser.find_elements(by=By.CLASS_NAME, value="password")[0]
    pwd.send_keys(password)  

    pwd.send_keys(Keys.ENTER)

    time.sleep(10)

    donations_loaded = browser.find_elements(by=By.CLASS_NAME, value='sqs-commerce-donation-list-content')[0]
    print("Logged in and donations list loaded...")

    try:
        while True:
            load_more = browser.find_element(by=By.CSS_SELECTOR, value="div[title='Load more']")
            load_more.click()
            print("Clicked load more...")
            time.sleep(3)
    except NoSuchElementException:
        print("No more donations to load!")

    donations = browser.find_elements(by=By.CLASS_NAME, value='sqs-commerce-donation-content')

    with open(f'donations_{datetime.today().strftime("%Y-%m-%d")}.csv', mode='w') as csv_file:
        fieldnames = ['count', 'amount', 'parent_name', 'email', 'address', 'phone', 
                        'student_name', 'description', 'school']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for idx, element in enumerate(donations):

            print()
            print(f"Scraping donation #{idx+1}")

            element.click()

            time.sleep(2)

            dialog = browser.find_elements(by=By.CLASS_NAME, value='dialog-contribution-summary')[0]

            amount = dialog.find_elements(by=By.CLASS_NAME, value='contribution-amount')[0].get_attribute('innerText')

            details = dialog.find_elements(by=By.TAG_NAME, value='div')

            donor = details[2].get_attribute('innerText').split("<br>")[0].split('\n')
            parent_name, email, address, phone = donor[0], donor[1], ' '.join(donor[2:5]), donor[5]

            student_name, description, school = '', '', ''
            if len(details) > 3:
                addl_info = details[3].find_elements(by=By.CSS_SELECTOR, value="*")
                for pair in [(addl_info[i], addl_info[i+1]) for i in range(len(addl_info)-1)]:

                    if pair[0].tag_name == 'div' and pair[1].tag_name == 'table':
                        
                        key = pair[0].get_attribute('innerText').lower()
                        val = pair[1].find_elements(by=By.TAG_NAME, value='td')[0].get_attribute('innerText')

                        if 'name' in key:
                            student_name = val
                        elif 'donation' in key:
                            description = val
                        elif 'school' in key:
                            school = val

            print(amount, parent_name, email, address, phone, student_name, description, school)
            
            writer.writerow({
                'count': idx+1, 
                'amount': amount, 
                'parent_name': parent_name, 
                'email': email, 
                'address': address, 
                'phone': phone, 
                'student_name': student_name,
                'description': description,
                'school': school
                })

            close = browser.find_element(by=By.CLASS_NAME, value='cancel')

            close.click()

            time.sleep(2)

    browser.quit()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-l", "--url", help="website link to visit")
    parser.add_argument("-u", "--username", help="username to log in with")
    parser.add_argument("-p", "--password", help="password to log in with")

    args = parser.parse_args()

    if args.url and args.username and args.password:
        print(f"url: {args.url}")
        print(f"username: {args.username}")
        print(f"password: {args.password}")

        browser = create_browser()

        try:
            main(browser, args.url, args.username, args.password)
        except Exception as e:
            browser.quit()
            raise e

    else:
        raise ValueError("Missing arguments! Run `python3 donations_parser.py --help`.")
