from Base.BaseYaml import get_yaml
from Base.BaseConfig import ConfigInfo
from Base.BaseMysql import DbConn
import os

# ————————————————以下项一般不建议修改——————————————————
dir_name = os.path.dirname(__file__)
f = get_yaml(dir_name + '/config.yaml')
product = f['product']
env = f['env']
config_info = ConfigInfo(product, env)
product_path = config_info.product_path
db = DbConn(product, env)


# ————————————————以下项可根据需要增删改——————————————————
def get_user_info(account=None):
    login_info = f['login_info'][env]
    corp_id = login_info['corp_id']
    # 如果指定用户名，则获取指定用户密码，否则获取全部
    u_p_info = login_info['u_p']
    if account:
        if account in u_p_info:
            password = u_p_info[account][0]
            username = u_p_info[account][1]
            return [corp_id, account, password, username]
        else:
            raise KeyError('配置文件不存在该用户名，请检查')
    else:
        result = []
        for account in u_p_info:
            result.append([corp_id, account, u_p_info[account][0], u_p_info[account][1]])
        return result


# 用户信息
user_info = get_user_info()
# 超管
admin_info = user_info[0]
admin_name = admin_info[3]
# 建设单位
js_info = user_info[1]
# 监理单位
jl_info = user_info[2]

# 基础数据
d = f['default_basic_data']
default_company = d['company']
default_project = d['project']
default_phase = d['phase']
default_project_phase = default_project + '-' + d['phase']
default_bidsec = d['bidsec']
default_building = d['building']
default_contractor1 = d['contractor1']
default_contractor2 = d['contractor2']

# 数据库查询
admin_id = db.query('select id from t_user where name="%s" and is_deleted=0' % admin_name)

# 质检后台url
zj_url = f['zj_url'][env]

if __name__ == '__main__':
    print(user_info)
    print(admin_info)
