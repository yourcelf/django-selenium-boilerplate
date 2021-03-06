import os
import time
from django.conf import settings
from django.core.urlresolvers import reverse
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select

try:
    from django.contrib.staticfiles.testing import StaticLiveServerTestCase
except ImportError:
    from djanto.test import LiveServerTestCase as StaticLiveServerTestCase

if "DJANGO_LIVE_TEST_SERVER_ADDRESS" not in os.environ:
    os.environ["DJANGO_LIVE_TEST_SERVER_ADDRESS"] = "localhost:7001-7999"

class SeleniumBase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumBase, cls).setUpClass()
        if hasattr(settings, "SELENIUM_FIREFOX_BIN"):
            if not os.path.exists(settings.SELENIUM_FIREFOX_BIN):
                raise OSError("Firefox binary '%s' missing." % (settings.SELENIUM_FIREFOX_BIN))
            firefox_binary = FirefoxBinary(settings.SELENIUM_FIREFOX_BIN)
            cls.selenium = WebDriver(firefox_binary=firefox_binary)
        else:
            cls.selenium = WebDriver()
        cls.selenium.set_window_size(1024, 768)
        cls.selenium.set_page_load_timeout(30)
        super(SeleniumBase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumBase, cls).tearDownClass()

    def url(self, route, *args, **kwargs):
        if route.startswith("/"):
            return u'%s%s' % (self.live_server_url, route)
        else:
            return u'%s%s' % (self.live_server_url, reverse(route, args=args, kwargs=kwargs))
    
    def by_css(self, name):
        """
        Shortcut for find element by css selector.
        """
        return self.selenium.find_element_by_css_selector(name)

    def by_csss(self, name):
        """
        Shortcut for find elementS by css selector.
        """
        return self.selenium.find_elements_by_css_selector(name)

    def await_selector(self, name, timeout=30):
        """
        Shortcut to poll for the presence of a selector before continuing.
        """
        start = time.time()
        while len(self.by_csss(name)) == 0:
            time.sleep(0.1)
            if time.time() - start > timeout:
                raise Exception(
                    "Timeout waiting for selector %s after %s seconds." % (name, timeout)
                )

    def select_option(self, selector, visible_text):
        select = Select(self.by_css(selector))
        select.select_by_visible_text(visible_text)
