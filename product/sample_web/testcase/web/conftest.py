# #!/usr/bin/python
# # -*- coding: utf-8 -*-
import pytest
from product.sample_web.business.web.Login import login
from product.sample_web.config.my_config import admin_info
from product.sample_web.config.my_driver import web_driver


@pytest.fixture(scope='module')
def admin_login():
    login(admin_info)


@pytest.fixture(scope='session', autouse=True)
def destroy():
    yield
    print('关闭进程')
    web_driver().quit()
