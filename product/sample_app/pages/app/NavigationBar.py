#!/usr/bin/python
# -*- coding: utf-8 -*-
from poium import Page, PageElement
from product.sample_app.config.my_driver import app_driver


class NavigationBar(Page):
    name_map = {'首页': 'homepage',
                '待办': 'todo',
                '报表': 'report',
                '工作台': 'workbench',
                '我': 'me'}
    btn_me = PageElement(xpath='//*[text()="我"]')
    btn_homepage = PageElement(xpath='//*[text()="首页"]')
    btn_todo = PageElement(xpath='//*[text()="待办"]')
    btn_report = PageElement(xpath='//*[text()="报表"]')
    btn_workbench = PageElement(xpath='//*[text()="工作台"]', timeout=1)
    header = PageElement(xpath='//*[@class="layout-header"]', describe='顶部布局，用于判断已登录', timeout=1)


nav_bar = NavigationBar(app_driver())
