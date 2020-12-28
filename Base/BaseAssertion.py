from Base.utils import to_html


def text_in_page(text, page):
    """判断文本在页面中存在，支持多个文本"""
    if not isinstance(text, list):
        text = [text]
    for i in text:
        assert i in to_html(page, to_string=True)


def text_not_in_page(text, page):
    """判断文本在页面中不存在，支持多个文本"""
    if not isinstance(text, list):
        text = [text]
    for i in text:
        assert i not in to_html(page, to_string=True)


def text_in_elem(text, elem, mode='part'):
    """
    判断元素包含文本，支持多个文本，支持模糊/精确匹配
    :param text: 待校验文本
    :param elem: 待校验元素
    :param mode: 校验模式，只支持part/all
    :return:
    """
    if not text:
        pass
    if mode not in ('part', 'all'):
        raise Exception('mode: 校验模式，只支持part/all')
    if not isinstance(text, list):
        text = [text]
    if mode == 'part':
        for i in text:
            assert i in elem.text
    else:
        assert text[0] == elem.text


def text_not_in_elem(text, elem, mode='part'):
    """
    判断元素不包含文本，支持多个文本，支持模糊/精确匹配
    :param text: 待校验文本
    :param elem: 待校验元素
    :param mode: 校验模式，只支持part/all
    :return:
    """
    if not text:
        pass
    if mode not in ('part', 'all'):
        raise Exception('mode: 校验模式，只支持part/all')
    if not isinstance(text, list):
        text = [text]
    if mode == 'part':
        for i in text:
            assert i not in elem.text
    else:
        assert text[0] != elem.text


def multi_assert(expect_list, actual_list):
    """
    多值校验
    :param expect_list: 预期值列表，
    :param actual_list:
    :return:
    """
    if not isinstance(expect_list, list):
        expect_list = [expect_list]
    for i in expect_list:
        if i not in actual_list:
            raise AssertionError('%s不存在于%s' % (i, str(actual_list)))
