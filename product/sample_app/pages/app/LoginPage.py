#!/usr/bin/python
# -*- coding: utf-8 -*-
from poium import Page, PageElement
from product.sample_app.config.my_driver import app_driver
from Base.utils import XpathLocator as Xl


class LoginPage(Page):
    input_corpId = PageElement(name='corpId', describe='企业代码')
    input_username = PageElement(name='username')
    input_password = PageElement(name='password')
    # btn_clear = PageElement(css='.input-clear', describe='文本框内容清除按钮')
    btn_login = PageElement(css='.btn-wrap')
    # btn_login_loading = PageElement(xpath='//*[contains(@class,"app-btn-activing")]', describe='正在转圈的登录按钮')
    btn_resetPassword = PageElement(css='.recover-pwd', describe='找回密码')
    tips_hot_upgrade = PageElement(xpath='//*[contains(text(),"正在更新程序，请稍候...")]', timeout=5)
    tips_init_data = PageElement(xpath='//*[contains(text(),"正在为您初始化数据")]', timeout=5)
    tips_corpId_error = PageElement(xpath='//*[contains(text(),"无效企业代码")]')
    tips_username_error = PageElement(xpath='//*[contains(text(),"帐号或密码错误")]')
    tips_password_error1 = PageElement(xpath='//*[contains(text(),"企业账号、个人帐号或密码错误，已失败")]')
    tips_password_error2 = PageElement(xpath='//*[contains(text(),"次，失败10次帐号将被锁定30分钟!")]')
    sel_user_privacy = PageElement(xpath='//*[contains(@class,"van-icon-success")]', describe='用户隐私勾选框')
    tips_privacy = PageElement(xpath='//*[contains(text(),"请在下方阅读并同意《用户协议》和《隐私声明》")]')
    input_corpId_reset = PageElement(xpath='//*[@placeholder="请输入企业代码"]')
    input_phone_reset = PageElement(xpath='//*[@placeholder="请输入手机号码"]')
    btn_next_reset = PageElement(xpath='//*[text()="下一步"]')
    tips_update_msg = PageElement(xpath=Xl.by_class_text('button button-default', '我知道了'), timeout=1)
    tips_do_not_update = PageElement(xpath=Xl.by_class_text('button button-default', '暂不更新'), timeout=1)


login_page = LoginPage(app_driver())
