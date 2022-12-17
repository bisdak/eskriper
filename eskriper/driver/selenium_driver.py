import logging
import time
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    format='%(asctime)s %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class SeleniumDriver:

    def __init__(self, proxy: str = '', user_agent: str = '', headless=True, download_path='./download_files'):
        self._headless = headless
        self._proxy = proxy
        self._user_agent = user_agent
        self._download_path = download_path
        self._options = uc.ChromeOptions()
        self.setup_driver()

    def setup_driver(self):
        self.set_options()
        self.driver = uc.Chrome()
        #self.set_proxy()
        self.driver.maximize_window()
    
    def set_options(self):
        self._options.headless = self._headless

        if self._user_agent:
            self._options.add_argument("user-agent=%s" % self._user_agent)
        
        prefs = {
            "download.default_directory" : self._download_path,
            "profile.default_content_settings": {"images": 2},
            "profile.managed_default_content_settings": {"images": 2}
        }
        self._options.add_experimental_option("prefs",prefs)

    def set_proxy(self, proxy=''):
        _proxy = proxy if proxy else self._proxy
        if _proxy:
            _type = 'https'
            self.driver.proxy = {
                _type: '%s://%s' % (_type, _proxy)
            }
            logging.info(f'Using {_proxy} proxy')

    def load(self, url, pattern="", by=By.ID, timeout=10):
        self.driver.get(url)
        if pattern:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, pattern))
            )
            except:
                logging.info('Element not found')

    def extract(self, pattern, by=By.CSS_SELECTOR, source=None, attr='text'):
        if not source:
            source = self.driver

        if attr == 'text':
            result = source.find_element(by, pattern).text 
        else:
            result = source.find_element(by, pattern).get_attribute(attr)
        return result.strip()

    def extracts(self, pattern, by=By.CSS_SELECTOR, source=None, attr='text'):
        if not source:
            source = self.driver

        if attr == 'text':
            results = [el.text for el in source.find_elements(by, pattern)]
        else:
            results = [el.get_attribute(attr) for el in source.find_elements(by, pattern)]

        results = [el.strip() for el in results if el.strip()]
        return results

    def login(self, credential, timeout=5):
        user = credential.get('username')
        password = credential.get('password')
        submit = credential.get('submit')
        after_login = credential.get('after_login')

        while True:
            try:
                user_tb = self.driver.find_element(user['by'], user['path'])
                pwd_tb = self.driver.find_element(password['by'], password['path'])
                submit_btn = self.driver.find_element(submit['by'], submit['path'])
                break
            except:
                time.sleep(timeout)

        user_tb.send_keys(user['value'])
        pwd_tb.send_keys(password['value'])
        submit_btn.click()
        time.sleep(timeout)

        while True:
            try:
                self.driver.find_element(after_login['by'], after_login['path'])
                break
            except Exception:
                time.sleep(timeout)

    def scroll_into(self, pattern, by=By.CSS_SELECTOR):
        element = None
        while True:
            try:
                element = self.driver.find_element(by, pattern)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'})", element);
                time.sleep(1)
                break
            except Exception:
                time.sleep(.5)
        return element

    @property
    def response(self):
        for request in self.driver.requests:
            if request.response:
                return request.response

    @property
    def user_agent(self):
        return str(self.driver.execute_script("return navigator.userAgent;"))