from Base.BaseDriver import WebInit
from product.sample_web.config.my_config import config_info


def web_driver():
    browser_name = config_info.get_browser_name()
    login_url = config_info.get_init_url()

    web_ins = WebInit(browser_name, login_url)
    if not web_ins.driver:
        web_ins.start()
    return web_ins.driver
