#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

from selenium.webdriver.support.ui import Select, WebDriverWait as Wait
from selenium.webdriver.remote.webdriver import WebElement
from selenium.common.exceptions import TimeoutException, \
                                       InvalidSelectorException

class FrontendError(Exception):
    pass

class MapPortalElement(WebElement):
    def __repr__(self):
        """Return a pretty name for an element"""

        id = self.get_attribute('id')
        class_ = self.get_attribute('class')

        if len(id) > 0:
            return '#' + id
        elif len(class_) > 0:
            return '.'.join([self.tag_name] + class_.split(' '))
        else:
            return self.tag_name

    def find_elements_by_jquery(self, jq):
        return self.parent.execute_script(
            '''return $(arguments[0]).find('%s').get();''' % jq, self)

    def find_element_by_jquery(self, jq):
        elems = self.find_elements_by_jquery(jq)
        if len(elems) == 1:
            return elems[0]
        else:
            raise InvalidSelectorException(
                "jQuery selector returned %i elements, expected 1" % len(elems))


def MapPortalDriver(base, **kwargs):
    return type('MapPortalDriver', (_BaseMapPortalDriver, base), kwargs)

class _BaseMapPortalDriver(object):
    def create_web_element(self, element_id):
        return MapPortalElement(self, element_id)

    def select_param(self, id, text):
        select = Select(self.find_element_by_id(id))
        select.select_by_visible_text(text)

    def ensure_selected(self, id, text, noptions=None):
        select = Select(self.find_element_by_id(id))
        option = select.first_selected_option
        assert option.text == text

        # FIXME: broken
        # if noptions is not None:
        #     options = filter(lambda o: o.is_displayed(), select.options)
        #     assert len(options) == noptions

    def select_contains(self, select, values):
        select = self.find_element_by_id(select)
        options = select.find_elements_by_tag_name('option')
        opt_values = map(lambda o: o.get_attribute('value'), options)

        assert sorted(values) == sorted(opt_values)

        return True

    def submit(self):
        self.find_element_by_id('submit').click()

    def wait(self, event, timeout=10):
        try:
            Wait(self, timeout).until(event)
        except (TimeoutException, FrontendError) as e:
            # do we have an error dialog
            dialog = self.find_element_by_id('error-dialog')
            if dialog.is_displayed():
                content = dialog.find_element_by_id('error-dialog-content')
                raise FrontendError(content.text)
            else:
                raise e

    def find_elements_by_jquery(self, jq):
        return self.execute_script('''return $('%s').get();''' % jq)

    def find_element_by_jquery(self, jq):
        elems = self.find_elements_by_jquery(jq)
        if len(elems) == 1:
            return elems[0]
        else:
            raise InvalidSelectorException(
                "jQuery selector returned %i elements, expected 1" % len(elems))

def output(src):
    def __call__(browser):
        # check no error dialog
        dialog = browser.find_element_by_id('error-dialog')
        if dialog.is_displayed():
            raise FrontendError()

        # check no loading dialog
        dialog = browser.find_element_by_id('loading-dialog')
        if dialog.is_displayed():
            return False

        outputDiv = browser.find_element_by_id('outputDiv')
        output = outputDiv.find_element_by_tag_name('img')
        return src in output.get_attribute('src')

    return __call__

def jquery(jq):
    def __call__(browser):
        dialog = browser.find_element_by_id('error-dialog')
        if dialog.is_displayed():
            raise FrontendError()

        elems = browser.find_elements_by_jquery(jq)
        return elems > 0

    return __call__

def animation_finished(browser):
    return browser.execute_script('''return $(':animated').length''') == 0
