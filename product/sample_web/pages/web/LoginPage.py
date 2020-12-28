from poium import Page, PageElement, PageElements
from product.sample_web.config.my_driver import web_driver


class LoginPage(Page):
    # 登录界面
    input_corpId = PageElement(name='tenantCode', describe='企业代码')
    input_username = PageElement(name='userName')
    input_password = PageElement(name='password')
    btn_login = PageElement(xpath='//*[@type="submit"]')
    btn_logout = PageElement(xpath='//*[contains(text(),"退出")]')
    tips_corpId_error1 = PageElement(xpath='//*[contains(text(),"无效企业代码，已失败"])')
    tips_corpId_error2 = PageElement(xpath='//*[contains(text(),"次，失败10次帐号将被锁定30分钟!"])')
    tips_user_passwd_error1 = PageElement(xpath='//*[contains(text(),"企业账号、个人帐号或密码错误，已失败")]')
    tips_user_passwd_error2 = PageElement(xpath='//*[contains(text(),"次，失败10次帐号将被锁定30分钟!")]')

    logo_index = PageElement(css='.logo', describe='左上角logo')
    btn_role = PageElement(xpath='//*[contains(@aria-controls,"dropdown-menu")]', describe='右上角，角色下拉按钮')
    menu_managementCenter = PageElement(xpath='//*[text()="管理中心"]')


login_page = LoginPage(web_driver())
