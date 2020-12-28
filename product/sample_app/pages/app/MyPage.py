#!/usr/bin/python
# -*- coding: utf-8 -*-
from poium import Page, PageElement
from product.sample_app.config.my_driver import app_driver


class MyPage(Page):
    btn_personal_info = PageElement(css='.user-header')
    tips_wechat = PageElement(css='.wechat-code-tip')
    btn_setting = PageElement(xpath='//*[text()="设置"]')
    btn_help = PageElement(xpath='//*[text()="帮助"]')
    btn_online_service = PageElement(xpath='//*[text()="在线客服"]')
    btn_problem_feedback = PageElement(xpath='//*[text()="反馈问题"]')
    btn_close_wechat_tips = PageElement(css='wechat-code-tip-btn icon icon-nav-close', describe='首次安装APP会出现')
    # 个人信息页面
    btn_logout = PageElement(xpath='//*[text()="退出登录"]')


my_page = MyPage(app_driver())
