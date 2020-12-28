import os
import time
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from appium.webdriver.common.touch_action import TouchAction as MobileTouchAction
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.keys import Keys
from Base.BaseLoggers import logger
from random import randint

from .page_objects import PageObject


class Page(PageObject):
    """
    Implement the APIs with javascript,
    and selenium/appium extension APIs。
    """

    def window_scroll(self, width=None, height=None):
        """
        JavaScript API, Only support css positioning
        Setting width and height of window scroll bar.
        """
        if width is None:
            width = "0"
        if height is None:
            height = "0"
        js = "window.scrollTo({w},{h});".format(w=str(width), h=height)
        self.driver.execute_script(js)

    @property
    def title(self):
        """
        JavaScript API
        Get page title.
        """
        js = 'return document.title;'
        return self.driver.execute_script(js)

    @property
    def url(self):
        """
        JavaScript API
        Get page URL.
        """
        js = "return document.URL;"
        return self.driver.execute_script(js)

    def switch_to_frame(self, frame_reference):
        """
        selenium API
        Switches focus to the specified frame, by id, name, or webelement.
        """
        self.driver.switch_to.frame(frame_reference)

    def switch_to_parent_frame(self):
        """
        selenium API
        Switches focus to the parent context.
        Corresponding relationship with switch_to_frame () method.
        """
        self.driver.switch_to.parent_frame()

    @property
    def new_window_handle(self):
        """
        selenium API
        Getting a handle to a new window.
        """
        all_handle = self.window_handles
        return all_handle[-1]

    @property
    def current_window_handle(self):
        """
        selenium API
        Returns the handle of the current window.
        """
        return self.driver.current_window_handle

    @property
    def window_handles(self):
        """
        selenium API
        Returns the handles of all windows within the current session.
        """
        return self.driver.window_handles

    def switch_to_window(self, handle, mode='web'):
        """
        selenium API
        Switches focus to the specified window.
        """
        if mode == 'web':
            logger.info('web切换窗口')
            self.driver.switch_to.window(handle)
        elif mode == 'app':
            logger.info('app切换窗口')
            try:  # app一般很少出现多窗口，这里的处理是避免app多窗口切换时出现异常
                self.driver.switch_to.window(handle)
                self.switch_to_app()
                self.switch_to_web()
                self.driver.switch_to.window(handle)
            except Exception as e:
                logger.error(e)
                if 'unable to connect to renderer' in str(e):
                    self.switch_to_app()
                    self.switch_to_web()
                    self.driver.switch_to.window(handle)
        else:
            raise Exception('mode只支持web或app')

    def switch_to_new_window(self, handle='', mode='web'):
        """切换到新窗口（非当前窗口），窗口数量大于2个时必须指定handle"""
        if len(self.window_handles) > 2 and not handle:
            raise Exception('当前窗口数量大于2个，必须指定handle')
        if len(self.window_handles) == 1:
            self.switch_to_window(self.window_handles[0])
            return
        for window in self.window_handles:
            if window != self.current_window_handle:
                self.switch_to_window(handle=window, mode=mode)
                return

    def screenshots(self, path=None, filename=None):
        """
        selenium API
        Saves a screenshots of the current window to a PNG image file
        :param path: The path to save the file
        :param filename: The file name
        """
        if path is None:
            path = os.getcwd()
        if filename is None:
            filename = str(time.time()).split(".")[0] + ".png"
        file_path = os.path.join(path, filename)
        self.driver.save_screenshot(file_path)

    def switch_to_app(self):
        """
        appium API
        Switch to native app.
        """
        self.driver.switch_to.context('NATIVE_APP')
        logger.debug('已切换到native')

    def switch_to_web(self, context=None):
        """
        appium API
        Switch to web view.
        """
        if context is not None:
            self.driver.switch_to.context(context)
        else:
            all_context = self.driver.contexts
            for context in all_context:
                if "WEBVIEW" in context and context != 'WEBVIEW_chrome':
                    self.driver.switch_to.context(context)
                    break
            else:
                raise NameError("No WebView found.")
        logger.debug('已切换到webview')

    def accept_alert(self):
        """
        selenium API
        Accept warning box.
        """
        self.driver.switch_to.alert.accept()

    def dismiss_alert(self):
        """
        selenium API
        Dismisses the alert available.
        """
        self.driver.switch_to.alert.dismiss()

    def alert_is_display(self):
        """
        selenium API
        Determines if alert is displayed
        """
        try:
            self.driver.switch_to.alert
        except NoAlertPresentException:
            return False
        else:
            return True

    @property
    def alert_text(self):
        """
        selenium API
        Get warning box prompt information.
        """
        return self.driver.switch_to.alert.text

    def move_to_element(self, elem):
        """
        selenium API
        Moving the mouse to the middle of an element
        """
        ActionChains(self.driver).move_to_element(elem).perform()

    def click_and_hold(self, elem):
        """
        selenium API
        Holds down the left mouse button on an element.
        """
        ActionChains(self.driver).click_and_hold(elem).perform()

    def move_by_offset(self, x, y):
        """
        selenium API
        Moving the mouse to an offset from current mouse position.

        :Args:
         - x: X offset to move to, as a positive or negative integer.
         - y: Y offset to move to, as a positive or negative integer.
        """
        ActionChains(self.driver).move_by_offset(x, y).perform()

    def release(self):
        """
        selenium API
        Releasing a held mouse button on an element.
        """
        ActionChains(self.driver).release().perform()

    def context_click(self, elem):
        """
        selenium API
        Performs a context-click (right click) on an element.
        """
        ActionChains(self.driver).context_click(elem).perform()

    def js_click(self, elem):
        self.driver.execute_script('arguments[0].click()', elem)

    def drag_and_drop_by_offset(self, elem, x, y):
        """
        selenium API
        Holds down the left mouse button on the source element,
           then moves to the target offset and releases the mouse button.
        :param elem: The element to mouse down.
        :param x: X offset to move to.
        :param y: Y offset to move to.
        """
        ActionChains(self.driver).drag_and_drop_by_offset(elem, xoffset=x, yoffset=y).perform()

    def refresh(self):
        logger.info('刷新页面')
        self.driver.refresh()
        self.page_ready()
        logger.info('页面刷新完成')

    def refresh_element(self, elem, timeout=10):
        """
        selenium API
        Refreshes the current page, retrieve elements.
        """
        try:
            timeout_int = int(timeout)
        except TypeError:
            raise ValueError("Type 'timeout' error, must be type int() ")

        for i in range(timeout_int):
            if elem is not None:
                try:
                    elem
                except StaleElementReferenceException:
                    self.driver.refresh()
                else:
                    break
            else:
                sleep(1)
        else:
            raise TimeoutError("stale element reference: element is not attached to the page document.")

    def tap(self, elem=None, x=0, y=0, count=1):
        """
        appium API
        Perform a tap action on the element
        """
        self.switch_to_app()
        if elem:
            action = MobileTouchAction(self.driver)
            action.tap(elem, x, y, count).perform()
        else:
            self.driver.tap([(x, y)])
        logger.info('点击坐标(%d,%d)' % (x, y))
        self.switch_to_web()

    def press(self, elem, x, y, pressure):
        """
        appium API
        Begin a chain with a press down action at a particular element or point
        """
        action = MobileTouchAction(self.driver)
        action.press(elem, x, y, pressure).perform()

    def long_press(self, elem, x, y, duration):
        """
        appium API
        Begin a chain with a press down that lasts `duration` milliseconds
        """
        action = MobileTouchAction(self.driver)
        action.long_press(elem, x, y, duration).perform()

    def swipe(self, start_x, start_y, end_x, end_y, duration=None):
        """
        appium API
        Swipe from one point to another point, for an optional duration.
        """
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)

    @property
    def window_size(self):
        # 需要切换到原生才能获取窗口大小
        self.switch_to_app()
        size = self.driver.get_window_size()
        self.switch_to_web()
        return size['width'], size['height']

    def swipe_to_refresh(self, scale_up=0.25, scale_down=0.75):
        """
        用于app页面下拉刷新
        :param scale_up: 默认0.25，即起始y坐标为屏幕纵轴25%的地方
        :param scale_down: 默认0.25，即结束y坐标为屏幕纵轴75%的地方
        :return:
        """
        size = self.window_size
        width = size[0]
        height = size[1]
        middle_point_x = int(width * 0.5)
        up_point_y = int(height * scale_up)
        down_point_y = int(height * scale_down)
        logger.info('正在下拉刷新')
        self.switch_to_app()
        self.swipe(middle_point_x, up_point_y, middle_point_x, down_point_y)
        self.switch_to_web()

    # 记录适用的拍照完成按钮
    take_btn = None
    complete_btn = None

    def take_photo(self):
        """
        拍照，只适用于安卓手机
        :return:
        """
        self.switch_to_app()
        sleep(3)
        # 拍照按钮
        take_btn_list = \
            ['self.driver.keyevent(27)',  # 物理拍照键，部分机型不适用
             'self.driver.keyevent(24)',  # 物理音量键，部分插件不适用
             """self.driver.find_element_by_xpath('//*[contains(@resource-id,"take_btn")]').click()"""]

        if self.take_btn:
            eval(self.take_btn)
            self._take_photo_complete()
        else:
            for i in take_btn_list:
                eval(i)
                if self._take_photo_complete():
                    self.take_btn = i
                    break
        sleep(2)

    def _take_photo_complete(self):
        # 拍照完成，点击完成
        complete_btn_list = ['//*[@content-desc="完成"]',
                             '//*[@content-desc="Done"]',
                             '//*[contains(@resource-id, "done")]']
        try:
            # 如果有适用的拍照完成按钮，则使用；否则遍历预置的按钮；
            if self.complete_btn:
                WebDriverWait(self.driver, 4, 0.5).until(
                    presence_of_element_located((By.XPATH, self.complete_btn))).click()
            else:
                for i in complete_btn_list:
                    try:
                        WebDriverWait(self.driver, 4, 0.5).until(presence_of_element_located((By.XPATH, i))).click()
                        self.complete_btn = i  # 保存适用的拍照完成按钮
                        return True
                    except:
                        pass
        except:
            pass

    def click_screen_center_randomly(self, start_scale_x=0.4, end_scale_x=0.6,
                                     start_scale_y=0.4, end_scale_y=0.6):
        """
        在屏幕指定区域随机点击
        :param start_scale_x: x轴起始比例
        :param end_scale_x: x轴结束比例
        :param start_scale_y: y轴起始比例
        :param end_scale_y: y轴结束比例
        :return: 返回点击的坐标tuple
        """
        # 移动到屏幕中央随机点击，并返回点击的坐标tuple
        window_size = self.window_size
        width = window_size[0]
        height = window_size[1]
        random_x = randint(int(width * start_scale_x), int(width * end_scale_x))
        random_y = randint(int(height * start_scale_y), int(height * end_scale_y))
        self.tap(x=random_x, y=random_y)
        return random_x, random_y

    def clear_text_by_backspace(self, times=10, to_webview=True):
        """
        通过回退键清除文本
        :param times: 回退键次数
        :param to_webview: 返回webview
        :return:
        """
        self.switch_to_app()
        ActionChains(self.driver).send_keys(Keys.BACKSPACE * times).perform()
        if to_webview:
            self.switch_to_web()

    def page_ready(self, timeout=5):
        """
        判断页面是否加载完成
        :param timeout: 超时时间
        :return:
        """
        js = 'return window.document.readyState;'
        for i in range(timeout):
            try:
                page_state = self.driver.execute_script(js)
            except Exception as e:
                print(e)
                continue
            if page_state == 'complete':
                logger.info('页面加载完成')
                sleep(1)
                break
            sleep(1)
        else:
            logger.info('页面未加载完成')
