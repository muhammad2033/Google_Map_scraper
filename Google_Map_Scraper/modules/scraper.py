from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from modules.helpers import *
from modules.const.settings import SETTINGS
from modules.const.colors import fore

import time
import json
import xlsxwriter

chrome_driver_path = "C:\Users\Alpha Tech\Downloads\chromedriver_win32\chromedriver.exe"
options = Options()
options.add_argument("--remote-debugging-port=9222")  # Use an arbitrary port number
options.add_experimental_option("detach", True)  # Keep the browser window open after exiting the script
service = Service(executable_path=chrome_driver_path)

driver = webdriver.Chrome(service=service, options=options)


def scroll():
    print("scrolled")
    # find the tag or div using by
    div = driver.find_element(By.XPATH, "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]")
    # scroll to the end of the div
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", div)
    time.sleep(2)


def scrape(args):
    '''
    Scrapes the results and puts them in the excel spreadsheet.

    Parameters:
        args (object): CLI arguments
    '''
    if args.pages is not None:
        SETTINGS["PAGE_DEPTH"] = args.pages
    SETTINGS["BASE_QUERY"] = args.query
    SETTINGS["PLACES"] = args.places.split(',')

    # set main box class name
    BOX_CLASS = "lI9IFe"

    # initialize workbook/worksheet
    workbook = xlsxwriter.Workbook('ScrapedData_GoogleMaps4.xlsx')
    worksheet = workbook.add_worksheet()

    # headers and data
    data = {
    "name": "",
    "phone": "",
    "category": "",
    "address": "",
    "website": "",
    "email": "",
    "services": "",
    "about": "",
    "facebook":"",
    "linkedin":"",
    "instagram":"",
    "youtube":"",
    "twitter":"",
    
}

    headers = generate_headers(args, data)
    print_table_headers(worksheet, headers)

    # Start from second row in xlsx, as the first one is reserved for headers
    row = 1

    # Remember scraped addresses to skip duplicates
    addresses_scraped = {}
    start_time = time.time()

    for place in SETTINGS["PLACES"]:
        # go to the index page
        driver.get(SETTINGS["MAPS_INDEX"])

        # Build the query string
        query = "{0} {1}".format(SETTINGS["BASE_QUERY"], place)
        print(f"{fore.GREEN}Moving on to {place}{fore.RESET}")

        # Fill in the input and press enter to search
        q_input = driver.find_element(By.NAME, "q")
        q_input.send_keys(query, Keys.ENTER)

        time.sleep(10)
        locs = 0
        while locs ==2:
            try:
                scroll()
                locs += 1
                time.sleep(1)
            except:
                print("Scrolled End")
                break

        # Loop through pages and results
        for _ in range(0, SETTINGS["PAGE_DEPTH"]):
            print("entered loop")
            time.sleep(1)

            # get all the results boxes
            boxes = driver.find_elements(By.CLASS_NAME, BOX_CLASS)
            print(len(boxes))
            # Loop through all boxes and get the info from it and store into an excel
            for box in boxes:
                # Just get the values, add only after we determine this is not a duplicate (or duplicates should not be skipped)
                name = box.find_element(By.CLASS_NAME, "fontHeadlineSmall").text

                address_tag = box.find_elements(By.CLASS_NAME, "W4Efsd")[-2]
                address_full = (address_tag.text).strip()
                address_split = address_full.split('·')
                if len(address_split) >= 2:
                    category = address_split[0]
                    address = address_split[1]
                else:
                    category = ""
                    address = address_split[0]

                scraped = address in addresses_scraped

                if scraped and args.skip_duplicate_addresses:
                    print(f"{fore.WARNING}Skipping {name} as duplicate by address{fore.RESET}")
                else:
                    phone_tag = box.find_elements(By.CLASS_NAME, "W4Efsd")[-1]
                    phone = phone_tag.text.split('·')[-1].strip()

                    if scraped:
                        addresses_scraped[address] += 1
                        print(f"{fore.WARNING}Currently scraping on{fore.RESET}: {name}, for the {addresses_scraped[address]}. time")
                    else:
                        addresses_scraped[address] = 1
                        print(f"{fore.GREEN}Currently scraping on{fore.RESET}: {name}")

                    if args.scrape_website:
                        try:
                            url = box.find_element(By.TAG_NAME, "a").get_attribute('href')
                        except:
                            url = None
                        website, email, social_media = get_website_data(url)
                        if website is not None:
                            data["website"] = url
                        if email is not None:
                            data["email"] = ','.join(email)
                        if social_media is not None:
                            data["facebook"] = social_media.get("facebook", "")
                            data["linkedin"] = social_media.get("linkedin", "")
                            data["instagram"]= social_media.get("instagram", "")
                            data["youtube"]  = social_media.get("youtube", "")
                            data["twitter"]  = social_media.get("twitter", "")
                        
                        # Scrape services and about data if the flags are set
                    if args.services:
                        try:
                            services_tag = box.find_element(By.CLASS_NAME, ".oKM9Me")[-1]
                            services = services_tag.text.split('.')[-1].strip()
                            data["services"] = services
                        except:
                            print(f"{fore.WARNING}Services not found for {name}{fore.RESET}")

                    if args.about:
                        try:
                            about_tag = box.find_element(By.CLASS_NAME, ".TkjJEe")[-1]
                            about = about_tag.text.split('.')[-1].strip()
                            data["about"] = about
                        except:
                            print(f"{fore.WARNING}About not found for {name}{fore.RESET}")


                    data["name"] = name
                    data["category"] = category
                    data["address"] = address
                    data["phone"] = phone

                        # If additional output is requested
                    if args.verbose:
                        print(json.dumps(data, indent=1))

                    write_data_row(worksheet, data, row)
                    row += 1
                    print("wrote successful")

            # go to the next page
            try:
                next_page_link = driver.find_element(By.ID, "n7lv7yjyC35__section-pagination-button-next")
                next_page_link.click()
            except WebDriverException:
                print(f"{fore.WARNING}No more pages for this search. Advancing to the next one.{fore.RESET}")

            # wait for the next page to load
            time.sleep(2)
        print("-------------------")

    workbook.close()
    driver.close()

    end_time = time.time()
    elapsed = round(end_time - start_time, 2)
    print(f"{fore.GREEN}Done. Time it took was {elapsed}s{fore.RESET}")
