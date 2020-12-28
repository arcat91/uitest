import pytest
from product.sample_web.pages.web import login_page
from product.sample_web.business.web.Login import login, logout
from product.sample_web.config.my_config import admin_info, js_info, jl_info


@pytest.mark.test1
class TestLogin:
    # 超管登录成功
    def test_login_success1(self):
        login(admin_info)
        assert login_page.menu_managementCenter
        logout()

    # 建设单位/监理单位登录成功
    @pytest.mark.parametrize('info', [js_info, jl_info])
    def test_login_success2(self, info):
        login(info)
        assert login_page.menu_managementCenter
        logout()


if __name__ == '__main__':
    pytest.main()
