from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from time import sleep

class E2ETests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(E2ETests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(E2ETests, cls).tearDownClass()
        cls.selenium.quit()

    def test_abc(self):
        self.selenium.get(self.live_server_url + '/')
        self.selenium.find_element_by_id('id_name').send_keys('Bruce Wayne')
        self.selenium.find_element_by_id('id_email').send_keys('bruce@wayne.com')
        self.selenium.find_element_by_id('checkout').click()
        sleep(2)
        assert False

