#!/usr/bin/python
# -*- coding: utf-8 -*-
import shelve
from time import strftime
from Base.BaseYaml import get_yaml
from Base.BaseAndroidPhone import *
from Base.BaseApk import ApkInfo
from Base.BaseAdb import AndroidDebugBridge
from Base.utils import singleton, slash_format

# 获取项目根目录
root_path = slash_format(os.path.dirname(__file__)).replace('/Base', '')
dir_time = strftime('%Y%m%d_%H%M%S')


# 获取配置文件信息
@singleton
class ConfigInfo:
    def __init__(self, product=None, env=None):
        self.product = product
        self.env = env
        self.product_path = root_path + '/product/' + self.product
        self.all = get_yaml(self.product_path + '/config/config.yaml')
        self.my_db = self.product_path + '/config/my_db'

    # 获取邮件配置
    def get_email_info(self):
        email_info = self.all["email"]
        return email_info

    # 获取数据库连接配置
    def get_mysql_link(self):
        mysql_link = self.all["mysql_link"][self.env]
        db_host = mysql_link["host"]
        db_port = mysql_link["port"]
        db_user = mysql_link["user"]
        db_pwd = mysql_link["pwd"]
        db_name = mysql_link["db_name"]
        return db_host, db_port, db_user, db_pwd, db_name

    # 获取浏览器名称
    def get_browser_name(self):
        return self.all["browserName"]

    # 获取web端初始化url
    def get_init_url(self):
        return self.all['login_url'][self.env]

    # 获取自动化报告名称
    def get_report_name(self):
        return self.all['report_name']

    # 获取app路径
    def get_app(self):
        return root_path + '/app_pkg/' + self.all['app'][self.env]

    # 获取app是否重置
    def get_app_reset(self):
        return self.all.get('app_reset')


# 设备信息
class DeviceInfo:
    def __init__(self):
        path = root_path + r"/config/devices.yaml"
        self.device_info = get_yaml(path)
        self.webview_file = root_path + r"/config/device_webview"
        self.adb = AndroidDebugBridge()

    def get_desired_caps(self, device_alias, app):
        desired_caps = self.device_info.get(device_alias)
        if not desired_caps:
            raise Exception('找不到此设备：%s，请检查配置./config/devices.yaml' % device_alias)
        # app包
        desired_caps['app'] = app
        # 闲置超时时间
        desired_caps['newCommandTimeout'] = 3600

        # 如果配置文件定义了appPackage、appActivity，则按配置文件来，否则根据apk包自动获取；
        if not desired_caps["appPackage"] or not desired_caps["appActivity"]:
            apk_info = ApkInfo(app)
            if not desired_caps["appPackage"]:
                desired_caps["appPackage"] = apk_info.get_package_name()
            if not desired_caps["appActivity"]:
                desired_caps["appActivity"] = apk_info.get_activity()

        # 先检查有线连接是否OK，若未连接，采用无线连接
        device_name = desired_caps['deviceName']
        if not self.adb.is_connected(device_name):
            device_list = desired_caps['device_address']
            if not device_list:
                device_list = []
            for i in device_list:
                try:
                    device_name = self.adb.connect(i)
                    # 兼容性模拟器调试
                    if not device_name:
                        continue
                    break
                except ConnectionError as e:
                    print(e)
            desired_caps['deviceName'] = device_name

        phone_info = get_phone_info(device_name)

        # 自动设置platformVersion
        desired_caps["platformVersion"] = phone_info["release"]

        # 从记忆库中选择chromedriver，如果没有则自动选择，并记录到记忆库
        webview_version = self._read_webview_version(phone_info["model"])
        if not webview_version:
            webview_version = get_webview_version(device_name, desired_caps['appPackage'], desired_caps['appActivity'])
            self._save_webview_version(phone_info["model"], webview_version)

        desired_caps['chromedriverExecutable'] = auto_chromedriver(webview_version)
        return desired_caps

    def _save_webview_version(self, device_name, webview_version):
        if webview_version:
            logger.info('设备%s写入webview版本号：%s' % (device_name, webview_version))
            with shelve.open(self.webview_file, writeback=True) as file_db:
                file_db[device_name] = webview_version

    def _read_webview_version(self, device_name):
        try:
            with shelve.open(self.webview_file, flag='r') as file_db:
                print(list(file_db.items()))
                try:
                    webview_version = file_db[device_name]
                    logger.info('已存在记录的webview版本号：%s' % webview_version)
                    if webview_version:
                        return webview_version
                except KeyError:
                    return None
        except Exception as e:
            print(e)
            return None


def auto_chromedriver(webview_version):
    """根据webview大版本，自动选择chromedriver
    :return:
    """
    chromedriver_path = root_path + r'/chromedriver/'
    driver_list = os.listdir(chromedriver_path)
    for driver in driver_list:
        version_num = re.findall(r'chromedriver(.*)\.exe', driver)[0]
        version_num = version_num.split('-')
        if len(version_num) == 2:
            version_range = range(int(version_num[0]), int(version_num[1]) + 1)
        else:
            version_range = [int(version_num[0])]
        if int(webview_version) in version_range:
            print('正在使用%s' % (chromedriver_path + driver))
            return chromedriver_path + driver
    else:
        raise Exception(f'没有找到版本为{webview_version}的chromedriver，请将对应的chromedriver存放到{chromedriver_path}')


if __name__ == '__main__':
    print(root_path)
    c = ConfigInfo('ydzj', 'test')
    # print(c.get_app())
    # print(DeviceInfo().get_desired_caps('chuizi_2', c.get_app()))
    # print(c.product_path)
    print(c.get_email_info())
