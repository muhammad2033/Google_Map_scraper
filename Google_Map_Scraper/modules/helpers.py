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
   
    
    headers = list(example_dict.keys())
    if not args.scrape_website:

        headers.remove("website")
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
    
    worksheet.write(row, 0, data["name"])
    worksheet.write(row, 1, data["phone"])
    worksheet.write(row, 2, data["category"])
    worksheet.write(row, 3, data["address"])
    worksheet.write(row, 4, data["website"])
    worksheet.write(row, 5, data["email"])
    worksheet.write(row, 6, data["services"])
    worksheet.write(row, 7, data["about"])
    worksheet.write(row, 8, data["facebook"])
    worksheet.write(row, 9, data["linkedin"])
    worksheet.write(row, 10, data["instagram"])
    worksheet.write(row, 11, data["youtube"])
    worksheet.write(row, 12, data["twitter"])






def find_emails(content, base_soup, i, queries=[], found=[]):
    '''

    '''
    if i < len(queries) and content is not None:
        # Get the emails with regex
        soup = BeautifulSoup(content, 'html.parser')
        body = soup.find('html')
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
    Retrieves the website URL, email address, and social media links from a given URL.

    Parameters:
        url (str): The URL to scrape the website, email, and social media links from.

    Returns:
        tuple: A tuple containing the website URL, email address, and social media links.
    """
    website = None
    email = None
    social_media = {
        "facebook": "",
        "linkedin": "",
        "instagram": "",
        "youtube": "",
        "twitter":""
    }

    if url is not None:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                website = url

                # Extract email addresses from the website content
                email = extract_email_addresses(response.text)

                # Extract social media links from the website content
                social_media = extract_social_media_links(response.text)
        except requests.exceptions.RequestException:
            print(f"Failed to retrieve data from website: {url}")

    return website, email, social_media     

def extract_social_media_links(text):
    """
    Extracts social media links (Facebook, LinkedIn, Instagram, and YouTube) from a given text.

    Parameters:
        text (str): The text to extract social media links from.

    Returns:
        dict: A dictionary containing the social media links.
    """
    soup = BeautifulSoup(text, "html.parser")
    social_media = {
        "facebook": "",
        "linkedin": "",
        "instagram": "",
        "youtube": "",
        "twitter":""

    }

    # Extract social media links
    facebook_link = soup.find("a", href=re.compile(r"facebook\.com"))
    if facebook_link:
        social_media["facebook"] = facebook_link["href"]

    linkedin_link = soup.find("a", href=re.compile(r"linkedin\.com"))
    if linkedin_link:
        social_media["linkedin"] = linkedin_link["href"]

    instagram_link = soup.find("a", href=re.compile(r"instagram\.com"))
    if instagram_link:
        social_media["instagram"] = instagram_link["href"]

    youtube_link = soup.find("a", href=re.compile(r"youtube\.com"))
    if youtube_link:
        social_media["youtube"] = youtube_link["href"]

    twitter = soup.find("a", href=re.compile(r"twitter\.com"))
    if twitter:
        social_media["twitter"] = twitter["href"]    

    return social_media


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
