import pytest
from Base.BaseConfig import dir_time, ConfigInfo, root_path
from Base.BaseDriver import AppInit, WebInit
from Base.utils import create_dir
from py.xml import html
import re
from random import randint


# 新增表头
def pytest_html_results_table_header(cells):
    try:
        cells.insert(2, html.th('ModuleName'))  # 模块名称
        cells.insert(3, html.th('Description'))  # 用例描述
        cells.pop()
    except:
        pass


# 新增表格
def pytest_html_results_table_row(report, cells):
    try:
        cells.insert(2, html.td(report.module_name))  # 模块名称
        cells.insert(3, html.td(report.description))  # 用例描述
        cells.pop()
    except:
        pass


# 将新增描述内容转成HTML对象
def description_html(desc):
    if not desc:
        return '没有定义'
    desc_ = desc.strip()
    if ':param desc' in desc:
        desc_ = re.findall(r'(.*):param desc', desc, flags=re.RegexFlag.DOTALL)[0]
    desc_lines = [i.strip() for i in desc_.split('\n')]
    desc_html = html.html(
        html.head(
            html.meta(name="Content-Type", value="text/html; charset=latin1")),
        html.body(
            [html.p(line) for line in desc_lines]))
    return desc_html


# 获取模块名称
def get_module_name(node_id):
    """获取对应的用例目录的__init__.py文件定义的module_name作为模块名称"""
    s_list = node_id.split('::')  # ['product/ydzj/testcase/web/Login/test_login.py', 'TestLogin', 'test_1']
    s_list1 = s_list[0].split('/')
    path = '/'.join(s_list1[:-1])
    try:
        f = open(root_path + '/' + path + '/__init__.py', encoding='utf-8').read()
        module_name = re.findall(r'module_name\s?=\s?(.*)', f)
        if module_name:
            module_name = module_name[0].replace('"', '').replace("'", '')
    except:
        module_name = ''
    return module_name


# 用例失败时截图
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    """
    Extends the PyTest Plugin to take and embed screenshot in html report, whenever test fails.
    :param item:
    """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    # 模块名称，先读取用例文件是否定义module_name，没有则读取用例目录的__init__.py文件
    report.module_name = description_html(getattr(item.module, 'module_name', ''))
    if report.module_name == '没有定义':
        report.module_name = description_html(get_module_name(report.nodeid))
    # 用例描述
    report.description = description_html(item.function.__doc__)
    extra = getattr(report, 'extra', [])
    config_info = ConfigInfo()
    product_path = config_info.product_path
    # 用start_run.py执行为一个session，此session目录用于收集每个session的所有报告，便于发送
    if not config_info.__dict__.get('session_id'):
        config_info.session_id = f'{dir_time}_{randint(10, 99)}'

    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            create_dir(product_path + '/report')  # 创建report根目录
            create_dir(product_path + '/report/' + config_info.session_id)  # 创建session报告汇总目录
            parent_dir = product_path + '/report/' + config_info.session_id + '/' + dir_time
            create_dir(parent_dir)  # 创建实际报告目录
            abs_img_dir = parent_dir + '/img/'  # 图片绝对路径目录
            create_dir(abs_img_dir)  # 创建图片目录
            img_name = _rename(report.nodeid, replace_type='img') + ".png"
            abs_img_path = abs_img_dir + img_name  # 图片绝对路径，用于保存图片
            rlt_img_path = './img/' + img_name  # 图片相对路径，用于html文件读取
            _capture_screenshot(abs_img_path)  # 截图并保存
            print(report.nodeid)
            if rlt_img_path:
                html = '<div><img src="%s" alt="screenshot" style="width:auto;height:228px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % rlt_img_path
                extra.append(pytest_html.extras.html(html))
        report.extra = extra
    report.nodeid = _rename(report.nodeid, replace_type='report')  # 替换报告节点名称


def _rename(name, replace_type='img'):
    split_name_list = name.split('::')  # ['product/ydzj/testcase/web/Login/test_login.py', 'TestLogin', 'test_1']
    case_file_name = split_name_list[0].split('/')[-1:][0]  # 'test_login.py'
    case_dir_name = split_name_list[0].split('/')[-2:][0]  # Login'
    if replace_type == 'img':  # 图片路径
        try:
            full_case_name = '+'.join(
                [case_dir_name, case_file_name, split_name_list[1],
                 split_name_list[2]])  # 'Login#test_login.py#TestLogin#test_1'
        except IndexError:
            full_case_name = '+'.join(
                [case_dir_name, case_file_name, split_name_list[1]])  # 'Login#test_login.py#test_1'
    elif replace_type == 'report':  # 报告节点路径
        try:
            full_case_name = '%s/%s::%s::%s' % (case_dir_name, case_file_name, split_name_list[1], split_name_list[2])
        except IndexError:
            full_case_name = '%s/%s::%s' % (case_dir_name, case_file_name, split_name_list[1])
    else:
        raise Exception('replace_type仅支持img或report')
    return full_case_name


def _capture_screenshot(name):
    # 截图，暂不支持Web和App同时运行时截图
    if WebInit().driver:
        driver = WebInit().driver
        driver.get_screenshot_as_file(name)
    else:
        driver = AppInit().driver
        # App需要切换到原生才能截图
        driver.switch_to.context('NATIVE_APP')
        driver.get_screenshot_as_file(name)
        # 截图完成后，切换回webview
        for i in driver.contexts:
            if 'WEBVIEW' in i and i != 'WEBVIEW_chrome':
                driver.switch_to.context(i)
                driver.implicitly_wait(1)
                break
