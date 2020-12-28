from Base.BaseDriver import AppInit
from product.sample_app.config.my_config import f, config_info, app_reset


def app_driver():
    device_alias = f['device_alias']
    app = config_info.get_app()

    app_ins = AppInit(device_alias, app)
    if not app_ins.driver:
        app_ins.start(reset=app_reset)
    return app_ins.driver


if __name__ == '__main__':
    app_driver()
