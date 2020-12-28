from Base.BaseYaml import get_yaml
from Base.BaseConfig import ConfigInfo
from Base.BaseMysql import DbConn
import os

dir_name = os.path.dirname(__file__)
f = get_yaml(dir_name + '/config.yaml')
product = f['product']
env = f['env']
config_info = ConfigInfo(product, env)
product_path = config_info.product_path
db = DbConn(product, env)


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
admin_info = user_info[0]
admin_name = admin_info[3]
# 建设
js1_info = user_info[1]
js1_name = js1_info[3]
js2_info = user_info[2]
js2_name = js2_info[3]
# 监理
jl1_info = user_info[3]
jl1_name = jl1_info[3]
jl2_info = user_info[4]
jl2_name = jl2_info[3]
# 施工
sg1_info = user_info[5]
sg1_name = sg1_info[3]
sg2_info = user_info[6]
sg2_name = sg2_info[3]

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
proj_id = db.query("select id from t_project where name = '%s' and is_deleted=0;" % default_project_phase)
bidsec_id = db.query(
    'select id from q_bidsection where proj_id="%s" and name="%s" and is_deleted=0' % (proj_id, default_bidsec))
admin_id = db.query('select id from t_user where name="%s" and is_deleted=0' % admin_name)
js1_id = db.query('select id from t_user where name="%s" and is_deleted=0' % js1_name)
js2_id = db.query('select id from t_user where name="%s" and is_deleted=0' % js2_name)
jl1_id = db.query('select id from t_user where name="%s" and is_deleted=0' % jl1_name)
jl2_id = db.query('select id from t_user where name="%s" and is_deleted=0' % jl2_name)
sg1_id = db.query('select id from t_user where name="%s" and is_deleted=0' % sg1_name)
sg2_id = db.query('select id from t_user where name="%s" and is_deleted=0' % sg2_name)

# app是否重置
app_reset = bool(f['app_reset'])
# 质检后台url
zj_url = f['zj_url'][env]

if __name__ == '__main__':
    print(user_info)
    print(admin_info)
    print(config_info.all['device_alias'])
    print(type(app_reset), app_reset)
