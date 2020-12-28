# #!/usr/bin/python
# # -*- coding: utf-8 -*-
import pytest
from product.sample_app.business.app.Login import login
from product.sample_app.config.my_config import *


@pytest.fixture(scope='module')
def admin_login():
    login(admin_info)


@pytest.fixture(scope='module')
def js1_login():
    login(js1_info)


@pytest.fixture(scope='module')
def js2_login():
    login(js2_info)


@pytest.fixture(scope='module')
def jl1_login():
    login(jl1_info)


@pytest.fixture(scope='module')
def jl2_login():
    login(jl2_info)


@pytest.fixture(scope='module')
def sg1_login():
    login(sg1_info)


@pytest.fixture(scope='module')
def sg2_login():
    login(sg2_info)
