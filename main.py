import argparse
from functools import partial
from time import sleep
import schedule
from selenium import webdriver
from parser.config import SETTINGS
from parser.parser import AliParser


def parse_arguments():
    arguments = argparse.ArgumentParser(description='Scrape product data from AliExpress category page.')
    arguments.add_argument('--url', type=str, required=True, help='URL of the AliExpress category page')
    return arguments.parse_args()


def job(arguments):
    print('Job started!')
    print(arguments)
    scraper = AliParser(webdriver.Chrome(), arguments.url)
    scraper.web_driver.get(arguments.url)
    scraper.scrape_page()


if __name__ == '__main__':
    time = SETTINGS.get('TIME_TO_COLLECT_DATA')
    args = parse_arguments()
    print(args)
    schedule.every().day.at('14:32').do(partial(job, args))

    while True:
        try:
            schedule.run_pending()
            print('PENDINGS DONE!')
        except Exception as e:
            print(e)

        sleep(1)

