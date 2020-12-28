#!/usr/bin/python
# -*- coding: utf-8 -*-
from appium import webdriver as adriver
from selenium import webdriver as wdriver
from time import sleep
from Base.BaseConfig import DeviceInfo, root_path, auto_chromedriver
from Base.utils import singleton
from Base.BaseLoggers import logger
from Base.BaseAndroidPhone import install_app, adb_command
from Base.AutoAppium import AutoAppium
import re


@singleton
class AppInit:
    def __init__(self, device_alias=None, app=None):
        """

        :param device_alias: 设备别名，如yeshen1
        :param app: APP包路径
        """
        self.desired_caps = DeviceInfo().get_desired_caps(device_alias, app)
        self.appium_server = DeviceInfo().device_info['appium_server']
        self.driver = None

    def start(self, reset=True, reinstall=False, start_appium=False, implicitly_wait=1):
        """
        打开app
        :param reset: 是否重置app，默认是
        :param reinstall: 是否重新安装app，默认否
        :param start_appium: 是否自启动Appium，默认禁用
        :param implicitly_wait: 隐式等待时间，默认1秒
        :return: driver instance
        """
        # 重置APP
        if reset:
            self.desired_caps['noReset'] = False
        else:
            self.desired_caps['noReset'] = True
        # 重装APP
        self.desired_caps['fullReset'] = bool(reinstall)
        device_name = self.desired_caps['deviceName']

        # 使用appium输入法，结束后恢复
        adb_command(device=device_name, cmd='shell ime disable io.appium.settings/.UnicodeIME')
        adb_command(device=device_name, cmd='shell ime disable io.appium.settings/.AppiumIME')
        self.desired_caps["unicodeKeyboard"] = True
        self.desired_caps["resetKeyboard"] = True

        # 自启动appium服务时，自动分配端口；否则，需手动启动appium服务，并使用配置文件的端口；
        if bool(start_appium):
            auto_appium = AutoAppium(device_name, self.appium_server)
            self.desired_caps['systemPort'] = auto_appium.get_system_port()
            self.desired_caps['mjpegServerPort'] = auto_appium.get_mjpeg_server_port()
            appium_port = auto_appium.start_appium()
        else:
            if not self.desired_caps['appium_port']:
                raise Exception('设备%s的appium_port没有定义，请检查devices.yaml文件' % device_name)
            appium_port = self.desired_caps['appium_port']

        # 连接appium服务
        remote = "http://%s:%s/wd/hub" % (self.appium_server, appium_port)

        # 不指定app连接手机，安装app
        # no_app_caps = self.desired_caps.copy()
        # for i in ['app', 'appPackage', 'appActivity']:
        #     no_app_caps.pop(i)
        # self.driver = adriver.Remote(remote, no_app_caps)
        # install_app(self.driver, self.desired_caps['deviceName'], self.desired_caps['app'])

        # 指定app连接手机，启动app
        self.driver = adriver.Remote(remote, self.desired_caps)
        sleep(3)

        # 对native设置隐式等待
        self.driver.switch_to.context('NATIVE_APP')
        self.driver.implicitly_wait(implicitly_wait)

        # 对webview设置隐式等待
        for i in self.driver.contexts:
            if 'WEBVIEW' in i and i != 'WEBVIEW_chrome':
                self.driver.switch_to.context(i)
                self.driver.implicitly_wait(implicitly_wait)
                break


@singleton
class WebInit:
    def __init__(self, browser_name=None, init_url=None):
        self.browser_name = str(browser_name).lower()
        self.driver = None
        self.init_url = init_url

    def start(self, headless=False, window_size='1920,1080', maximize_window=True, implicitly_wait=1):
        """
        打开web
        :param headless: 无头模式，默认关闭，当前只支持chrome
        :param window_size: 浏览器分辨率，默认为"1920,1080"
        :param maximize_window: 最大化窗口，默认开启
        :param implicitly_wait: 隐式等待时间，默认1秒
        :return: driver
        """
        if self.browser_name == "chrome":
            options = wdriver.ChromeOptions()
            # 无头模式
            if bool(headless):
                options.add_argument('--headless')
            # 分辨率
            options.add_argument(f'--window-size={window_size}')
            # 打开浏览器
            driver = wdriver.Chrome(executable_path=auto_chromedriver(self.get_chrome_version()),
                                    options=options)
            # 最大化窗口
            if bool(maximize_window):
                driver.maximize_window()
            # 隐式等待
            driver.implicitly_wait(implicitly_wait)
            logger.info("Starting Chrome browser.")
        # elif self.browser_name == "firefox":
        #     driver = wdriver.Firefox()
        #     logger.info("Starting Firefox browser.")
        #     return driver
        # elif self.browser_name == "ie":
        #     driver = wdriver.Ie()
        #     logger.info("Starting IE browser.")
        #     return driver
        else:
            raise Exception('当前只支持Chrome')
        # 打开初始化页面
        if self.init_url:
            driver.get(self.init_url)
            sleep(1)
        self.driver = driver

    # 自动获取并设置chromedriver版本
    @staticmethod
    def get_chrome_version():
        options = wdriver.ChromeOptions()
        options.add_argument('--headless')  # chrome从60版本后支持无头模式
        d = wdriver.Chrome(executable_path=root_path + '/chromedriver/chromedriver62-64.exe', options=options)
        try:
            d.get('http://localhost:80')
        except Exception as e:  # 提取错误信息里提示的合适版本号
            chrome_version = int(re.findall(r'chrome=(\d{2})', str(e))[0])
        else:
            chrome_version = 62
        finally:
            d.quit()
        return chrome_version


if __name__ == '__main__':
    w = WebInit(browser_name='chrome')
    # print(w.get_chrome_version())
    print(auto_chromedriver(w.get_chrome_version()))
