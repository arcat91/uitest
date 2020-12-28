from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from poium.common.exceptions import PageSelectException, PageElementError, FindElementTypesError
from Base.BaseLoggers import logger
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.command import Command

from appium.webdriver.common.mobileby import MobileBy

# Map PageElement constructor arguments to webdriver locator enums
LOCATOR_LIST = {
    # selenium
    'css': By.CSS_SELECTOR,
    'id_': By.ID,
    'name': By.NAME,
    'xpath': By.XPATH,
    'link_text': By.LINK_TEXT,
    'partial_link_text': By.PARTIAL_LINK_TEXT,
    'tag': By.TAG_NAME,
    'class_name': By.CLASS_NAME,
    # appium
    'ios_uiautomation': MobileBy.IOS_UIAUTOMATION,
    'ios_predicate': MobileBy.IOS_PREDICATE,
    'ios_class_chain': MobileBy.IOS_CLASS_CHAIN,
    'android_uiautomator': MobileBy.ANDROID_UIAUTOMATOR,
    'android_viewtag': MobileBy.ANDROID_VIEWTAG,
    'android_datamatcher': MobileBy.ANDROID_DATA_MATCHER,
    'accessibility_id': MobileBy.ACCESSIBILITY_ID,
    'image': MobileBy.IMAGE,
    'custom': MobileBy.CUSTOM,
}
# 公共超时
global_timeout = 0


def my_click(self):
    """重写click方法"""
    for i in range(3):
        try:
            self._execute(Command.CLICK_ELEMENT)
            return
        except WebDriverException as e:
            if 'not clickable' in str(e):
                continue
    else:
        self._parent.execute_script('arguments[0].click()', self)


WebElement.click = my_click


class PageObject:
    """
    Page Object pattern.
    """

    def __init__(self, driver, url=None):
        """
        :param driver: `selenium.webdriver.WebDriver` Selenium webdriver instance
        :param url: `str`
        Root URI to base any calls to the ``PageObject.get`` method. If not defined
        in the constructor it will try and look it from the webdriver object.
        """
        self.driver = driver
        self.context = driver
        self.root_uri = url if url else getattr(self.driver, 'url', None)
        self.locator = None

    def get(self, uri):
        """
        :param uri:  URI to GET, based off of the root_uri attribute.
        """
        root_uri = self.root_uri or ''
        self.driver.get(root_uri + uri)
        self.driver.implicitly_wait(5)

    def run_script(self, js=None):
        """
        run JavaScript script
        """
        if js is None:
            raise ValueError("Please input js script")
        else:
            return self.driver.execute_script(js)

    # 找不到元素时进行重试
    @staticmethod
    def _re_find(func, retry, *args):
        for i in range(retry):
            re_elems = func(*args)
            if re_elems:
                return re_elems
        else:
            raise Exception('找不到元素')

    # 通过locator方式查找元素
    def find(self, parent_elem=None, multi=False, retry=3, **kwargs):
        """
        通过locator方式查找元素，支持父级节点继承查找，支持page查找，只返回可见元素
        :param parent_elem: 待查找元素的父节点元素
        :param multi: 是否返回多个目标元素
        :param retry: 重试次数
        :return:
        """
        if not kwargs:
            raise ValueError("""请定义一个locator，格式如xpath='//*[@id="name"]'""")
        if len(kwargs) > 1:
            raise ValueError("只能定义一个locator")
        by, loc = next(iter(kwargs.items()))
        try:
            self.locator = (LOCATOR_LIST[by], loc)
        except KeyError:
            raise FindElementTypesError('不支持该定位方式%s' % str(by))

        # 如果有父节点，从父节点找元素，否则通过page查找
        try:
            if parent_elem:
                elems = self._re_find(parent_elem.find_elements, retry, *self.locator)
            else:
                elems = self._re_find(self.driver.find_elements, retry, *self.locator)
        except:
            return self

        # 将可见元素放入列表，根据multi返回1个或多个
        displayed_list = []
        for elem in elems:
            if elem.is_displayed():
                displayed_list.append(elem)
        if displayed_list and multi:
            return displayed_list
        elif displayed_list and not multi:
            return displayed_list[0]
        else:
            return self


class PageElement(object):
    """
    Page Element descriptor.
    :param css:    `str`
        Use this css locator
    :param id_:    `str`
        Use this element ID locator
    :param name:    `str`
        Use this element name locator
    :param xpath:    `str`
        Use this xpath locator
    :param link_text:    `str`
        Use this link text locator
    :param partial_link_text:    `str`
        Use this partial link text locator
    :param tag:    `str`
        Use this tag name locator
    :param class_name:    `str`
        Use this class locator
    :param context: `bool`
        This element is expected to be called with context
    Page Elements are used to access elements on a page. The are constructed
    using this factory method to specify the locator for the element.
        >> from poium import Page, PageElement
        >> class MyPage(Page):
                elem1 = PageElement(css='div.myclass')
                elem2 = PageElement(id_='foo')
                elem_with_context = PageElement(name='bar', context=True)
    Page Elements act as property descriptors for their Page Object, you can get
    and set them as normal attributes.
    """

    def __init__(self, context=False, timeout=3, log=True, describe="", **kwargs):
        global global_timeout
        global_timeout = timeout
        self.timeout = timeout
        self.context = None
        self.log = log
        self.describe = describe
        if not kwargs:
            raise ValueError("Please specify a locator")
        if len(kwargs) > 1:
            raise ValueError("Please specify only one locator")
        self.k, self.v = next(iter(kwargs.items()))
        try:
            self.locator = (LOCATOR_LIST[self.k], self.v)
        except KeyError:
            raise FindElementTypesError("Element positioning of type '{}' is not supported. ".format(self.k))
        self.has_context = bool(context)

    def _get_element(self):
        try:
            elem = self.context.find_element(*self.locator)
        except NoSuchElementException:
            logger.debug('找不到元素，%s' % str(self.locator))
            return self
        except UnexpectedAlertPresentException:
            logger.debug('未知弹框报错')
            try:
                self.context.switch_to.alert.accept()
            except NoAlertPresentException:
                logger.debug('没有弹框')
        else:
            try:
                style_red = 'arguments[0].style.border="1px solid red"'
                self.context.execute_script(style_red, elem)
            except BaseException:
                return elem
            return elem

    def _find(self):
        # 多次查找元素
        for i in range(self.timeout):
            elem = self._get_element()
            if page_exist(elem):
                break
        else:
            return self
        # 多次判断元素是否可见
        for i in range(self.timeout):
            try:
                if elem.is_displayed():
                    return elem
                else:
                    sleep(1)
            except StaleElementReferenceException:
                return self
        else:
            return self._get_element()

    def __get__(self, instance, owner, context=None):
        if not instance:
            return None

        if not context and self.has_context:
            return lambda ctx: self.__get__(instance, owner, context=ctx)

        if not context:
            context = instance.driver

        self.context = context
        return self._find()

    def __set__(self, instance, value):
        if self.has_context:
            raise PageElementError("Sorry, the set descriptor doesn't support elements with context.")
        elem = self.__get__(instance, instance.__class__)
        if not elem:
            raise PageElementError("Can't set value, element not found")
        elem.click()  # 部分输入框需要重新点击一次，才能清空文本
        sleep(0.3)
        elem.clear()  # 清空文本
        sleep(0.3)
        elem.send_keys(value)


class PageElements(PageElement):
    """
    Like `PageElement` but returns multiple results.
    >> from page import Page, PageElements
    >> class MyPage(Page):
            all_table_rows = PageElements(tag='tr')
            elem2 = PageElement(id_='foo')
            elem_with_context = PageElement(tag='tr', context=True)
    """

    def _find(self):
        try:
            return self.context.find_elements(*self.locator)
        except NoSuchElementException:
            return []

    def __set__(self, instance, value):
        if self.has_context:
            raise PageElementError("Sorry, the set descriptor doesn't support elements with context.")
        elems = self.__get__(instance, instance.__class__)
        if not elems:
            raise PageElementError("Can't set value, no elements found")
        [elem.send_keys(value) for elem in elems]


class PageSelect(object):
    """
    Processing select drop-down selection box
    """

    def __init__(self, select_elem, value=None, text=None, index=None):
        if value is not None:
            Select(select_elem).select_by_value(value)
        elif text is not None:
            Select(select_elem).select_by_visible_text(text)
        elif index is not None:
            Select(select_elem).select_by_index(index)
        else:
            raise PageSelectException('"value" or "text" or "index" options can not be all empty.')


class PageWait(object):
    def __init__(self, elem, timeout=3):
        """
        等待元素可见
        """
        # 如果定义元素时没有找到元素，此处将继续查找元素，直至超时；
        if not page_exist(elem):
            elem = WebDriverWait(driver=elem.context, timeout=int(timeout - global_timeout),
                                 poll_frequency=0.5).until(presence_of_element_located(elem.locator))

        # 找到元素后，才开始判断是否可见；
        for i in range(timeout):
            try:
                if elem.is_displayed():
                    break
                else:
                    sleep(1)
            except:
                sleep(1)
        else:
            raise TimeoutError("超时，元素不可见")


class PageWaitDisappear(object):
    def __init__(self, elem, timeout=3):
        """
        等待元素消失
        """
        try:
            PageWait(elem)  # 指定时间内未出现，则判断元素不可见；若出现了，则循环等待判断元素不可见；
        except:
            return

        for i in range(timeout):
            try:
                if elem.is_displayed():
                    sleep(1)
                else:
                    return
            except:
                break
        else:
            raise TimeoutError('超时，元素仍可见')


def page_exist(elem):
    """返回元素是否存在"""
    if type(elem).__name__ == 'WebElement':
        return True
    else:
        return False
