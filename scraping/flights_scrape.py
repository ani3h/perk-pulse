import csv
import os
import cloudscraper
from bs4 import BeautifulSoup

url = "https://www.makemytrip.com/flights/domestic-flight-offer.html"


def clean_text(text):
    """Remove unwanted symbols and characters from the extracted text."""
    cleaned_text = text.replace(
        '\xa0', ' ')  # Replace non-breaking spaces with regular spaces
    cleaned_text = cleaned_text.replace(
        '\n', ' ')  # Replace newlines with spaces
    cleaned_text = cleaned_text.replace(
        '\u200b', '')  # Remove zero-width spaces
    cleaned_text = cleaned_text.replace('‘', "'").replace(
        '’', "'")  # Replace fancy quotes with regular quotes
    cleaned_text = cleaned_text.replace('“', '"').replace(
        '”', '"')  # Replace double fancy quotes
    cleaned_text = ' '.join(cleaned_text.split())  # Remove extra spaces
    return cleaned_text.strip()


def clean_offer_dict(offer_dict):
    """Apply cleaning to each value in the offer dictionary."""
    return {key: clean_text(value) for key, value in offer_dict.items()}


def getURLs(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
        'DNT': '1',
        'Connection': 'close'
    }

    scraper = cloudscraper.create_scraper()

    try:
        response = scraper.get(url, headers=headers)
        response.raise_for_status()  # Ensure the request was successful

        soup = BeautifulSoup(response.content, 'html.parser')

        product_links = []
        # Find all the product links using the specified class
        product_list = soup.find_all(
            "a", class_='button font-semibold is-inline-flex text-uppercase align-items-center justify-content-end')
        for product in product_list:
            link = product.get('href')
            if link:
                product_links.append(link)

        return product_links

    except Exception as e:
        print(f"Error extracting product links: {e}")
        return []


def getFeatures(links):
    data = []
    scraper = cloudscraper.create_scraper()  # Returns a CloudScraper instance

    for link in links[1:]:  # Adjust the number of links to process as needed
        try:
            r = scraper.get(link)
            r.raise_for_status()  # Ensure the request was successful
            soup = BeautifulSoup(r.text, 'html.parser')

            # Debugging output
            print(f"Scraping {link}")

            # Extract the card name
            card = soup.find(
                'span', class_='font-size-larger font-semibold text-uppercase gray-dark copy-text')
            card_name = card.text.strip() if card else "N/A"

            # Find the table
            table = soup.find('table', class_='br-10')
            if table:
                # Extract the headers
                headers = [th.get_text().strip()
                           for th in table.find_all('th')]

                # Extract the rows and create a list of cleaned dictionaries
                offers = []
                for tr in table.find_all('tr')[1:]:  # Skip the header row
                    cells = [clean_text(td.get_text().strip())
                             for td in tr.find_all('td')]
                    offer_dict = dict(zip(headers, cells))
                    cleaned_offer_dict = clean_offer_dict(offer_dict)
                    offers.append(cleaned_offer_dict)
            else:
                offers = []

            # Extract the terms and conditions
            terms_conditions_div = soup.find(
                'div', class_='panal font-size-base font-semibold gray-dark')

            other_conditions = ""

            if terms_conditions_div:
                # Check for <li> elements
                terms_conditions_list = terms_conditions_div.find_all('li')
                if terms_conditions_list:
                    other_conditions = "\n".join(
                        [clean_text(li.get_text().strip()) for li in terms_conditions_list])

                # If <li> elements are not found, check for <p> elements
                elif not other_conditions:
                    terms_conditions_paragraphs = terms_conditions_div.find_all(
                        'p')
                    if terms_conditions_paragraphs:
                        other_conditions = "\n".join([clean_text(p.get_text().strip(
                        )) for p in terms_conditions_paragraphs if p.get_text().strip()])

            if not other_conditions:
                other_conditions = "N/A"

            valid_till_element = soup.find('span', class_='brand-primary')
            valid_till = valid_till_element.get_text().strip() if valid_till_element else "N/A"

            offer_data = {
                'tag': 'cleartrip',
                'Card': card_name,
                'Offer': offers,
                'Valid Till': valid_till,
                'Other Conditions': other_conditions,
                'link': link
            }

            data.append(offer_data)
        except Exception as e:
            print(f"Error fetching product details from {link}: {e}")

    return data


def write_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['tag', 'Card', 'Offer', 'Valid Till',
                        'Other Conditions', 'link'])
        for entry in data:
            writer.writerow([
                entry['tag'],
                entry['Card'],
                entry['Offer'],
                entry['Valid Till'],
                entry['Other Conditions'],
                entry['link']
            ])


product_data = getFeatures(getURLs(url))

# CSV features
csv_file_path = '/Users/anishkantheti/Documents/PerkPulse/data/flights.csv'

# Append the scraped data to the CSV file
write_to_csv(product_data, csv_file_path)
