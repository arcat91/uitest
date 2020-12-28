import os

cur_dir = os.path.dirname(__file__)
file_name = os.path.basename(__file__)

old_product = 'sample_app'
new_product = os.path.basename(cur_dir)
black_list = [file_name, '.log', 'config.yaml', 'testsuite.yaml']


def change_product(file):
    with open(file, encoding='utf-8') as f:
        # print(file)
        content = f.read().replace(old_product, new_product)
        print('导入路径由%s修改为%s' % (old_product, new_product))
    with open(file, mode='w', encoding='utf-8') as w:
        w.write(content)
        print('已修改文件【%s】' % file)


def loop_change(dir_name):
    for i in os.listdir(dir_name):
        os.chdir(dir_name)
        abs_path = os.path.abspath(i)
        # print(abs_path)
        if os.path.isdir(abs_path):

            loop_change(abs_path)
        else:
            if os.path.basename(abs_path) not in black_list:
                change_product(abs_path)


if __name__ == '__main__':
    print('当前工程路径为【%s】' % cur_dir)
    loop_change(cur_dir)
