from poium import Page
from product.ydkf_app.config.my_driver import app_driver
from product.ydkf_app.business.app.Login import login_app
from Base.utils import to_html

driver = app_driver()
page = Page(driver)
page.switch_to_web()
to_html(page)
# login(['apitest', 'ui_js1', 'Test1234'])
login_app('retesting','retesting','123')