from poium import Page
from product.ydyf_web.config.my_driver import web_driver
from product.ydyf_web.business.web.Login import login, logout

driver = web_driver()
page = Page(driver)
login(['mysoft', 'mysoft', 'my!@#456'])
