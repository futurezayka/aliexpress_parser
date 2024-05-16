from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from csv_recorder.csv_recorder import DataRecorder
from parser.config import FILTERS, SETTINGS
from parser.selectors import XPATH, CLASS, CSS, ID


class AliParser:
    def __init__(self, driver, url):
        self.web_driver = driver
        self.count_of_pages = None
        self.max_price = FILTERS.get('MAX_PRICE')
        self.max_reviews = FILTERS.get('MAX_REVIEWS')
        self.max_orders = FILTERS.get('MAX_ORDERS')
        self.timeout = SETTINGS.get('TIMEOUT')
        self.url = url

    def find_elements_by(self, by, value, multiple=False, is_clickable=False):
        locator_methods = {
            "xpath": By.XPATH,
            "class": By.CLASS_NAME,
            "id": By.ID,
            "css": By.CSS_SELECTOR
        }

        locator_method = locator_methods.get(by.lower())

        if not locator_method:
            raise ValueError("Unsupported 'by' argument")

        wait = WebDriverWait(self.web_driver, self.timeout)
        wait_condition = ec.visibility_of_all_elements_located if multiple else ec.presence_of_element_located

        if is_clickable:
            wait_condition = ec.element_to_be_clickable

        try:
            return wait.until(wait_condition((locator_method, value)))
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
            return None

    def get_count_of_pages(self):
        try:
            pagination = self.find_elements_by('xpath', XPATH.get('PAGINATION'))
            if pagination:
                count = list(filter(lambda word: word.isdigit(), pagination.text.split()))[-1]
                return int(count)
        except (NoSuchElementException, TypeError):
            return 1

    def scroll_to_bottom_smoothly(self):
        scale = 0.1
        while scale < 9.9:
            self.web_driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight/{scale});")
            scale += 0.01

    def collect_links(self):
        self.count_of_pages = self.count_of_pages or self.get_count_of_pages()
        links = []

        for page in range(1, min(self.count_of_pages, 5) + 1):  # Limit to first 5 pages for testing
            list_view_button = self.find_elements_by('xpath', XPATH.get('LIST_VIEW'), is_clickable=True)
            if list_view_button:
                list_view_button.click()

            self.scroll_to_bottom_smoothly()
            links.extend(self.get_valid_items_links())
            self.web_driver.get(f"{self.url}?page={page + 1}")

        return links

    def filter(self, price, orders):
        return price <= self.max_price and orders <= self.max_orders

    def get_valid_items_links(self):
        valid_links = []
        items = self.find_elements_by('css', CSS.get('CARDS'), multiple=True)
        for item in items:
            try:
                orders_el = item.find_element(By.CLASS_NAME, CLASS.get('SOLD_ITEMS'))
                price_el = item.find_element(By.CLASS_NAME, CLASS.get('PRICE')).find_elements(By.TAG_NAME, 'span')
            except NoSuchElementException:
                continue

            if orders_el and price_el:
                try:
                    orders = int(orders_el.text.split()[0].replace('.', '').replace('+', ''))
                    price = float(price_el[0].text)
                except (ValueError, TypeError) as e:
                    continue

                if self.filter(price, orders):
                    link = item.find_element(By.CSS_SELECTOR, CSS.get('LINK')).get_attribute('href')
                    valid_links.append(link)
        return valid_links

    def parse_images(self):
        images = []
        image_el = self.find_elements_by('xpath', XPATH.get('IMAGES'))
        if image_el:
            try:
                images_el = image_el.find_elements(By.TAG_NAME, 'img')
                for image in images_el:
                    images.append(image.get_attribute('src'))
            except NoSuchElementException:
                print("Image elements not found")
        return images

    def get_product_data(self, link):
        data = []
        self.web_driver.get(link)

        price_el = self.find_elements_by('xpath', XPATH.get('PRICE_DETAIL'))
        title_el = self.find_elements_by('css', CSS.get('TITLE'))
        product = {
            'title': title_el.text if title_el else '',
            'price': price_el.text.replace(' ', '') if price_el else '',
            'description': self.parse_description(),
            'images': self.parse_images(),
            'link': link,
        }
        data.append(product)
        return data

    def parse_description(self):
        descriptions = []
        self.scroll_to_bottom_smoothly()
        try:
            description_el = self.web_driver.find_element(By.ID, ID.get('DESCRIPTION'))
            if description_el:
                for span in description_el.find_elements(By.TAG_NAME, 'span'):
                    try:
                        descriptions.append(span.text)
                    except Exception as e:
                        print(e)
        except NoSuchElementException:
            pass
        return descriptions

    def scrape_page(self):
        recorder = DataRecorder()
        pages_links = self.collect_links()
        for link in pages_links:
            self.web_driver.get(link)
            reviews = self.find_elements_by('css', CSS.get('REVIEWS')).text.split()[0]
            if reviews:
                try:
                    reviews = int(reviews)
                except (TypeError, ValueError):
                    reviews = 0
                if reviews > self.max_reviews:
                    continue

            data = self.get_product_data(link)
            recorder.append_to_csv(data)
