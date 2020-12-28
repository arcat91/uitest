#!/usr/bin/python
# *- coding: utf-8 -*-
import pytest
from poium import PageWait, page_exist
from product.sample_app.business.app.Login import login, click_privacy
from product.sample_app.config.my_config import *
from product.sample_app.pages.app import login_page


@pytest.mark.login
class Test:
    def test_corpId_error(self):
        login(['ttt', admin_info[1], admin_info[2]], test_err=True)
        assert page_exist(login_page.tips_corpId_error)

    def test_username_error(self):
        login([admin_info[0], 'ttt', admin_info[2]], test_err=True)
        assert page_exist(login_page.tips_username_error)

    def test_password_error(self):
        login([admin_info[0], admin_info[1], 'ttt'], test_err=True)
        assert page_exist(login_page.tips_password_error1)
        assert page_exist(login_page.tips_password_error2)

    # 取消勾选用户协议
    def test_no_privacy(self):
        click_privacy(False)
        login_page.btn_login.click()
        PageWait(login_page.tips_privacy)

    def test_admin_login(self, admin_login):
        pass
