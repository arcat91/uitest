from poium import PageWait
from product.sample_web.pages.web import login_page
from Base.BaseLoggers import logger
from time import sleep


def login(info_list, test_err=False):
    logger.info('Web正在登录')
    login_page.input_corpId = info_list[0]
    login_page.input_username = info_list[1]
    login_page.input_password = info_list[2]
    login_page.btn_login.click()
    if not test_err:
        PageWait(login_page.menu_managementCenter)
        logger.info('Web登录完成')


def logout():
    logger.info('Web正在退出登录')
    if login_page.btn_logout.is_displayed():
        login_page.btn_logout.click()
    else:
        login_page.btn_role.click()
        sleep(1)
        login_page.btn_logout.click()
    PageWait(login_page.btn_login)
    sleep(3)
    logger.info('Web退出登录完成')
