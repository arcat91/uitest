import os
import datetime
from time import sleep
import shelve
from selenium.common.exceptions import NoAlertPresentException, StaleElementReferenceException


def singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


def slash_format(path):
    return str(path).replace('\\', '/')


def create_dir(dir_name):
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        pass
    else:
        os.mkdir(dir_name)
    return dir_name


def to_html(page, is_native=False, to_string=False, dir_name='.', file_name='debug'):
    """打印app当前页面的资源文件
    :param page: Page对象
    :param is_native: 是否原生，默认webview
    :param to_string: 直接返回字符串，不输出文件
    :param dir_name: 生成文件目录
    :param file_name: 生成文件名称
    :return:
    """
    create_dir(dir_name + '/debug')
    if is_native:
        page.switch_to_app()
    else:
        page.switch_to_web()
    page_source = page.driver.page_source.strip("'")
    if to_string:
        return page_source
    file_path = dir_name + r'/debug/%s.html' % file_name
    print('当前页面资源文件已输出到【%s】' % file_path)
    with open(file_path, mode='w', encoding='utf-8') as file:
        file.write(page_source)


class Date:
    def __init__(self):
        pass

    def today(self):
        now_ins = datetime.datetime.now()
        return now_ins.strftime('%Y-%m-%d')

    def now(self):
        now_ins = datetime.datetime.now()
        return now_ins.strftime('%Y-%m-%d %H:%M:%S')

    def day_calc(self, day, time_format='%Y-%m-%d'):
        """日期计算，单位天，day=1为当前日期加1，day=-1为当前日期减1"""
        now_ins = datetime.datetime.now()
        d1 = datetime.timedelta(days=day)
        d2 = now_ins + d1
        return d2.strftime(time_format)


# 常用的xpath定位
class XpathLocator:
    @staticmethod
    def by_text(text, tag='*'):
        return '//%s[text()="%s"]' % (tag, text)

    @staticmethod
    def by_partial_text(text, tag='*'):
        return '//%s[contains(text(),"%s")]' % (tag, text)

    @staticmethod
    def by_class(class_value, tag='*'):
        return '//%s[@class="%s"]' % (tag, class_value)

    @staticmethod
    def by_partial_class(class_value, tag='*'):
        return '//%s[contains(@class,"%s")]' % (tag, class_value)

    @staticmethod
    def by_class_text(class_value, text, tag='*'):
        return '//%s[@class="%s"][text()="%s"]' % (tag, class_value, text)

    @staticmethod
    def by_partial_class_text(class_value, text, tag='*'):
        return '//%s[contains(@class,"%s")][contains(text(),"%s")]' % (tag, class_value, text)


# 获取元素属性
def elem_has_attr(elem, attr_name, attr_value):
    if attr_value in elem.get_attribute(attr_name):
        return True
    else:
        return False


# 循环处理弹框
def loop_accept_alert(driver, timeout=90, to_webview=True):
    driver.switch_to.context('NATIVE_APP')
    success_once = False
    for i in range(timeout):
        try:
            driver.switch_to.alert.accept()
            print('接受对话框')
            sleep(1)
            success_once = True
        except NoAlertPresentException:
            sleep(1)
            if success_once:
                break
        except StaleElementReferenceException:
            try:
                driver.find_element_by_xpath('//*[@text="允许"]').click()
                print('点击允许')
                sleep(1)
                success_once = True
            except:
                sleep(1)
                if success_once:
                    break
        finally:
            timeout = timeout - 1
    if to_webview:
        for i in driver.contexts:
            if 'WEBVIEW' in i and i != 'WEBVIEW_chrome':
                driver.switch_to.context(i)


# 记录模块运行时间
def time_recorder(dir_path, module_name, start_time, stop_time):
    with shelve.open(dir_path, writeback=True) as recorder:
        if recorder.get('run_time_record') is None:
            recorder['run_time_record'] = []
        record_list = recorder['run_time_record']
        record_list.append([module_name, int((stop_time - start_time) / 60)])
        recorder['run_time_record'] = record_list


date = Date()
