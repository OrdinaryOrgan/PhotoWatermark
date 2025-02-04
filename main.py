import os

from tqdm import tqdm

from config import Layout, input_dir, config, font, bold_font, get_logo, white_margin_width, \
    output_dir, quality, logo_enable, save_config, load_config
from image_container import ImageContainer
from image_processor import ImageProcessor, padding_image
from utils import get_file_list, copy_exif_data

id_to_name = {'Model': '相机机型', 'Make': '相机厂商', 'LensModel': '镜头型号', 'Param': '拍摄参数', 'Date': '拍摄时间',
              'None': '无'}
s_line = '+' + '-' * 15 + '+' + '-' * 15 + '+'
id_to_loc = {'left_top': '左上文字', 'right_top': '右上文字', 'left_bottom': '左下文字', 'right_bottom': '右下文字'}


def parse_elem_value(element):
    if element['name'] == 'Custom':
        return '自定义字段 (' + (element['value'] if 'value' in element else '') + ')'
    else:
        return id_to_name.setdefault(element['name'], '值错误')


def print_current_setting():
    """
    状态1：开始菜单
    :return:
    """
    global state

    print(s_line)
    print(' ' * 8 + '当前设置')
    print(s_line)
    print(' 【1】: 布局：{}'.format(config['layout']['type']))
    print(' 【2】: Logo：{}'.format("显示" if config['logo']['enable'] else "不显示"))
    print(' 【3】: 左上文字：{}'.format(parse_elem_value(config['layout']['elements']['left_top'])))
    print(' 【4】: 左下文字：{}'.format(parse_elem_value(config['layout']['elements']['left_bottom'])))
    print(' 【5】: 右上文字：{}'.format(parse_elem_value(config['layout']['elements']['right_top'])))
    print(' 【6】: 右下文字：{}'.format(parse_elem_value(config['layout']['elements']['right_bottom'])))
    print(' 【7】: 白色边框：{}'.format("显示" if config['layout']['white_margin']['enable'] else "不显示"))
    print(' 【8】: 等效焦距：{}'.format("使用" if config['param']['focal_length']['use_equivalent_focal_length'] else "不使用"))
    print(s_line)
    user_input = input('输入【y 或回车】按照当前设置开始处理图片，输入【数字】修改设置，输入【x】退出程序\n')
    if user_input == 'y' or user_input == '':
        state = 100
    elif user_input == 'x' or user_input == 'X':
        exit(0)
    elif user_input.isdigit():
        state = int(user_input)


def processing():
    """
    状态1：处理图片
    :return:
    """
    global state

    file_list = get_file_list(input_dir)
    layout = Layout(config['layout'])
    print('当前共有 {} 张图片待处理'.format(len(file_list)))
    processor = ImageProcessor(font, bold_font)
    for file in tqdm(file_list):
        source_path = os.path.join(input_dir, file)
        # 打开图片
        container = ImageContainer(source_path)

        # 添加logo
        if logo_enable:
            container.set_logo(get_logo(container.make))
        else:
            container.set_logo(None)

        # 使用等效焦距
        container.is_use_equivalent_focal_length(config['param']['focal_length']['use_equivalent_focal_length'])

        # 添加水印
        if 'normal_with_right_logo' == layout.type:
            watermark = processor.normal_watermark(container, layout, is_logo_left=False)
        elif 'square' == layout.type:
            watermark = processor.square_watermark(container)
        else:
            watermark = processor.normal_watermark(container, layout)

        # 添加白框
        if config['layout']['white_margin']['enable']:
            watermark = padding_image(watermark, int(white_margin_width * min(container.width, container.height) / 100),
                                      'tlr')

        # 保存图片
        target_path = os.path.join(output_dir, file)
        watermark.save(target_path, quality=quality)
        container.close()
        watermark.close()
        copy_exif_data(source_path, target_path)
    print('处理完成，文件已输出至 output 文件夹中，请点击任意键退出或直接关闭'.format(len(file_list)))
    input()
    state = -1

def modify_focal_length():
    global state

    while True:
        print('输入【数字】选择是否使用等效焦距：')
        print('    【1】: 使用等效焦距')
        print('    【2】: 不使用等效焦距')
        print('输入【0】返回主菜单')
        print('输入【x】退出程序')
        user_input = input()
        if user_input == 'x' or user_input == 'X':
            exit(0)
        if user_input.isdigit():
            if user_input == '0':
                return
            elif user_input == '1':
                config['param']['focal_length']['use_equivalent_focal_length'] = True
                return
            elif user_input == '2':
                config['param']['focal_length']['use_equivalent_focal_length'] = False
                return
            else:
                print('输入错误，请重新输入')
        else:
            print('输入错误，请重新输入')

def modify_layout():
    """
    状态2：修改布局
    :return:
    """
    global state

    while True:
        print('输入【数字】选择布局类型：')
        print('    【1】: normal')
        print('    【2】: normal_with_right_logo')
        print('    【3】: square')
        print('输入【0】返回主菜单')
        print('输入【x】退出程序')
        user_input = input()
        if user_input == 'x' or user_input == 'X':
            exit(0)
        if user_input.isdigit():
            if user_input == '0':
                return
            elif user_input == '1':
                config['layout']['type'] = 'normal'
                return
            elif user_input == '2':
                config['layout']['type'] = 'normal_with_right_logo'
                return
            elif user_input == '3':
                config['layout']['type'] = 'square'
                return
            else:
                print('输入错误，请重新输入')
        else:
            print('输入错误，请重新输入')


def modify_logo():
    """
    状态3：修改 logo
    :return:
    """
    global state

    while True:
        print('输入【数字】选择是否显示 logo：')
        print('    【1】: 显示 logo')
        print('    【2】: 不显示 logo')
        print('输入【0】返回主菜单')
        print('输入【x】退出程序')
        user_input = input()
        if user_input == 'x' or user_input == 'X':
            exit(0)
        if user_input.isdigit():
            if user_input == '0':
                return
            elif user_input == '1':
                config['logo']['enable'] = True
                return
            elif user_input == '2':
                config['logo']['enable'] = False
                return
            else:
                print('输入错误，请重新输入')
        else:
            print('输入错误，请重新输入')


def modify_white_margin():
    """
    状态4：修改 margin
    :return:
    """
    global state

    while True:
        print('输入【数字】选择是否显示白色边框：')
        print('    【1】: 显示白色边框')
        print('    【2】: 不显示白色边框')
        print('输入【0】返回主菜单')
        print('输入【x】退出程序')
        user_input = input()
        if user_input == 'x' or user_input == 'X':
            exit(0)
        if user_input.isdigit():
            if user_input == '0':
                return
            elif user_input == '1':
                config['layout']['white_margin']['enable'] = True
                return
            elif user_input == '2':
                config['layout']['white_margin']['enable'] = False
                return
            else:
                print('输入错误，请重新输入')
        else:
            print('输入错误，请重新输入')


def modify_element(key):
    """
    状态4-7：修改 logo
    :return:
    """
    global state

    while True:
        print('输入【数字】选择【{}】显示内容：'.format(id_to_loc[key]))
        print('    【1】：相机型号')
        print('    【2】：相机厂商')
        print('    【3】：镜头型号')
        print('    【4】：拍摄参数')
        print('    【5】：拍摄日期')
        print('    【6】：自定义字段')
        print('    【7】：无')
        print('输入【0】返回主菜单')
        print('输入【x】退出程序')
        user_input = input()
        if user_input == 'x' or user_input == 'X':
            exit(0)
        if user_input.isdigit():
            number = int(user_input)
            if number == 0:
                return
            elif number == 1:
                config['layout']['elements'][key]['name'] = 'Model'
                return
            elif number == 2:
                config['layout']['elements'][key]['name'] = 'Make'
                return
            elif number == 3:
                config['layout']['elements'][key]['name'] = 'LensModel'
                return
            elif number == 4:
                config['layout']['elements'][key]['name'] = 'Param'
                return
            elif number == 5:
                config['layout']['elements'][key]['name'] = 'Date'
                return
            elif number == 6:
                config['layout']['elements'][key]['name'] = 'Custom'
                user_input = input('输入自定义字段的值：\n')
                config['layout']['elements'][key]['value'] = user_input
                return
            elif number == 7:
                config['layout']['elements'][key]['name'] = 'None'
                return
            else:
                print('输入错误，请重新输入')
        else:
            print('输入错误，请重新输入')


state = 0

if __name__ == '__main__':

    while True:
        if state == 0:
            print_current_setting()
        elif state == 100:
            # 处理数据的代码
            print(s_line)
            load_config()
            processing()
        elif state == 1:
            modify_layout()
            # 修改布局类型的代码
            state = 0
        elif state == 2:
            modify_logo()
            # 修改logo的代码
            state = 0
        elif state == 3:
            modify_element('left_top')
            # 修改左上文字的代码
            state = 0
        elif state == 4:
            modify_element('left_bottom')
            # 修改左下文字的代码
            state = 0
        elif state == 5:
            modify_element('right_top')
            # 修改右上文字的代码
            state = 0
        elif state == 6:
            modify_element('right_bottom')
            # 修改右下文字的代码
            state = 0
        elif state == 7:
            modify_white_margin()
            # 修改右下文字的代码
            state = 0
        elif state == 8:
            modify_focal_length()
            state = 0
        elif state == -1:
            exit(0)
        else:
            print("输入错误，请重新输入")
            state = 0
        save_config()
