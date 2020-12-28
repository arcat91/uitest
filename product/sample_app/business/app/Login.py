from poium import PageWaitDisappear, PageWait, page_exist
from product.sample_app.pages.app import login_page, nav_bar, my_page
from product.sample_app.business.app.Common import back_to_homepage, DialogHandler as Dh
from Base.BaseLoggers import logger
from Base.utils import loop_accept_alert, elem_has_attr


def login(info_list, test_err=False):
    loop_accept_alert(login_page.driver, timeout=3)  # 处理权限弹框
    # 切换到webview
    login_page.switch_to_web()
    # 大版本更新
    if page_exist(login_page.tips_do_not_update):
        logger.info('暂不更新')
        login_page.tips_do_not_update.click()
    # 判断是否已登录
    if page_exist(nav_bar.header):
        # 可能存在热更新，等待热更新完成
        if page_exist(login_page.tips_hot_upgrade):
            logger.info('等待热更新完成')
            PageWaitDisappear(login_page.tips_hot_upgrade, timeout=90)
            if page_exist(login_page.tips_update_msg):
                logger.info('有更新内容提示')
                login_page.tips_update_msg.click()
        # 检查当前登录用户与期望登录用户是否一致，不一致则重新登录
        user_code = login_page.driver.execute_script('return localStorage.user_code;')
        if user_code.lower() != info_list[1].lower():
            logout()
        else:
            logger.info('已登录')
            return
    # 登录页面
    logger.info('App正在登录')
    login_page.input_corpId.click()
    login_page.clear_text_by_backspace()  # 模拟器时clear无效，所以用回退键
    login_page.input_corpId = info_list[0]
    login_page.input_username.click()
    login_page.clear_text_by_backspace()
    login_page.input_username = info_list[1]
    login_page.input_password.click()
    login_page.clear_text_by_backspace()
    login_page.input_password = info_list[2]
    click_privacy()
    login_page.btn_login.click()
    # loop_accept_alert(login_page.driver, 5)  # 处理权限弹框
    # 测试登录失败时，不走下面的流程
    if not test_err:
        # PageWaitDisappear(login_page.btn_login_loading, timeout=10)
        if page_exist(login_page.tips_hot_upgrade):
            loop_accept_alert(login_page.driver, timeout=1)  # 处理权限弹框
            logger.info('等待热更新完成')
            PageWaitDisappear(login_page.tips_hot_upgrade, timeout=90)
            logger.info('热更新完成')
        if page_exist(login_page.tips_init_data):
            loop_accept_alert(login_page.driver, timeout=1)  # 处理权限弹框
            logger.info('等待数据初始化完成')
            PageWaitDisappear(login_page.tips_init_data, timeout=90)
            logger.info('数据初始化完成')
        if page_exist(login_page.tips_update_msg):
            logger.info('有热更新内容提示')
            login_page.tips_update_msg.click()
        # 登录后校验
        PageWait(nav_bar.header, timeout=30)
        logger.info('App登录完成')


def logout():
    logger.info('App正在退出登录')
    back_to_homepage()
    nav_bar.btn_me.click()
    my_page.btn_personal_info.click()
    my_page.btn_logout.click()
    Dh.confirm()
    PageWait(login_page.input_username, timeout=60)
    logger.info('App退出登录完成')


def click_privacy(choose=True):
    choose_status = elem_has_attr(elem=login_page.sel_user_privacy, attr_name='class', attr_value='single-check')
    if not choose_status and choose:
        login_page.sel_user_privacy.click()
    if choose_status and not choose:
        login_page.sel_user_privacy.click()


if __name__ == '__main__':
    login(['apitest', 'ui_sg1', 'Test1234'])
    # app_login('zjfunctest', 'huang_js', 'Test1234')
