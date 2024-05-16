import argparse

from selenium import webdriver

from parser.parser import AliParser


# def parse_arguments():
#     arguments = argparse.ArgumentParser(description='Scrape product data from AliExpress category page.')
#     arguments.add_argument('--url', type=str, required=True, help='URL of the AliExpress category page')
#     return arguments.parse_args()


if __name__ == '__main__':
    # args = parse_arguments()
    url = 'https://www.aliexpress.com/w/wholesale-RC-Airplanes.html'
    scraper = AliParser(webdriver.Chrome(), url)
    scraper.web_driver.get(url)
    scraper.scrape_page()
    # scraper.web_driver.get(CONFIG.get('BASE_URL'))
    # scraper.write_residences_to_json()
