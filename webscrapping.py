import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_yellowpages(session, industry, pageNumber):
    base_url = "https://www.yellowpages.com.au/search/listings?"
    
    # Concatenating parameters to the base_url
    url = f"{base_url}clue={industry}&locationClue=New+South+Wales&pageNumber={pageNumber}"
    
    USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
    ]

    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:  # Fixed exception name
        print(f"Error fetching the webpage: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Adjust the selector as needed
    business_elements = soup.select("h3.MuiTypography-h3")  # Selector to be adjusted
    business_names = [biz.text.split('&')[0].strip() for biz in business_elements]
    
    return business_names

def get_all_business_names(industry, page_limit):
    all_names = []
    page_number = 1  # Initializing page_number
    with requests.Session() as session:
        while page_number <= page_limit:  # Setting a limit on page numbers to scrape
            names = scrape_yellowpages(session, industry, page_number)
            if not names:
                break
            all_names.extend(names)
            page_number += 1
            sleep_time = random.uniform(3, 6)
            time.sleep(sleep_time) # Adhere to a respectful rate limiting
        all_names = list(set(all_names))
    return all_names