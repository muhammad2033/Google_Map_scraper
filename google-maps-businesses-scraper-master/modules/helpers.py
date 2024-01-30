import requests
import re
from bs4 import BeautifulSoup

def generate_headers(args, example_dict):
    '''
    Generates headeers from the data dictionary by capitalizing it's keys.

    Parameters:
            args (object): Object containging CLI arguments passed as they can affect which columns are needed
            example_dict (dict): Data dictionary with keys

    Returns:
            list (list): List of capitalized strings representing headers
    '''
    headers = example_dict.keys()
    if not args.scrape_website:
        del example_dict["website"]

    headers = example_dict.keys()
    
    return [header.capitalize() for header in headers]

def print_table_headers(worksheet, headers):
    '''
    Writes headers to the worksheet.

    Parameters:
            worksheet (worksheet object): Worksheet where headsers should be written
            headers (list): List of headers to vrite
    '''
    col = 0
    for header in headers:
        worksheet.write(0, col, header)
        col += 1

def write_data_row(worksheet, data, row):
    '''
    Writes data dictionary to row.

    Parameters:
            worksheet (worksheet object): Worksheet where data should be written
            data (dict): Dictionary containing data to write
            row (int): No. of row to write to
    '''
    col = 0
    for key in data:
        worksheet.write(row, col, data[key])
        col += 1

def find_emails(content, base_soup, i, queries=[], found=[]):
    '''

    '''
    if i < len(queries) and content is not None:
        # Get the emails with regex
        soup = BeautifulSoup(content, 'html.parser')
        body = soup.find('body')
        html_text_only = body.get_text()
        match = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', html_text_only)

        # Removes duplicate values
        if match is not None:
            found = found + match

        # Advance to next page
        links = base_soup.find_all('a')
        next_page_url = None
        for link in links:
            curr_url = link.get("href")
            if curr_url is not None and queries[i] in curr_url:
                next_page_url = curr_url
                print(f"NPU found {next_page_url}")
                break

        cont = None
        if next_page_url is not None:
            try:
                response = requests.get(next_page_url, allow_redirects=True, timeout=10)
                cont = response.content.decode("utf-8")
                print(f"NPU: Looking for emails in {next_page_url}")
            except:
                print("Error occurred while looking for emails in NPU")
                cont = None

        return find_emails(cont, base_soup, i + 1, queries, found)
    else:
        return found


def get_website_data(url):
    """
    Retrieves the website URL and email address from a given URL.

    Parameters:
        url (str): The URL to scrape the website and email from.

    Returns:
        tuple: A tuple containing the website URL and email address.
    """
    website = None
    email = None

    if url is not None:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                website = url

                # Extract email addresses from the website content
                email = extract_email_addresses(response.text)
        except requests.exceptions.RequestException:
            print(f"Failed to retrieve data from website: {url}")

    return website, email

def extract_email_addresses(text):
    """
    Extracts email addresses from a given text.

    Parameters:
        text (str): The text to extract email addresses from.

    Returns:
        list: A list of email addresses.
    """
    soup = BeautifulSoup(text, "html.parser")
    emails = []
    for link in soup.find_all("a"):
        email = link.get("href")
        if email and email.startswith("mailto:"):
            emails.append(email[7:])  # Remove "mailto:" prefix

    return emails

def get_services_and_about(url):
    '''
    Extracts services and about section from the given URL.

    Parameters:
        url (str): The URL to scrape.

    Returns:
        tuple: A tuple containing the services and about_section as strings.
    '''
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException


    chrome_driver_path = "chromedriver_win32\chromedriver.exe"
    options = Options()


    service = Service(executable_path=chrome_driver_path)


    driver = webdriver.Chrome(service=service, options=options)

    import time
    driver.get(url)
    time.sleep(5)  # Wait for the page to load properly

    # Find the element containing services information
    try:
        services_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Services')]/following-sibling::span")
        services = services_element.text
    except NoSuchElementException:
        services = ""

    # Find the element containing about section information
    try:
        about_element = driver.find_element(By.XPATH, "//span[contains(text(), 'About this place')]/following-sibling::span")
        about_section = about_element.text
    except NoSuchElementException:
        about_section = ""

    return services, about_section


def extract_about_section(website_content):
    # Use BeautifulSoup or any other HTML parsing library to extract the about section
    # Example using BeautifulSoup:
    soup = BeautifulSoup(website_content, 'html.parser')
    about_section = soup.find('div', class_='about-section')
    
    if about_section:
        return about_section.text.strip()
    else:
        return None


def extract_services(website_content):
    # Use BeautifulSoup or any other HTML parsing library to extract the services
    # Example using BeautifulSoup:
    soup = BeautifulSoup(website_content, 'html.parser')
    services_section = soup.find('div', class_='services-section')
    
    if services_section:
        services = [service.text.strip() for service in services_section.find_all('li')]
        return services
    else:
        return None


# Example usage:
url = "https://maps.google.com"  # Replace with the actual URL of a location
about, services = get_services_and_about(url)
if about is not None:
    print(f"About section:\n{about}")
if services is not None:
    print(f"Services:\n{services}")
