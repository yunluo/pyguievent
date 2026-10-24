![Static Badge](https://img.shields.io/badge/Python-34-1?style=for-the-badge)  ![PyPI - Version](https://img.shields.io/pypi/v/pyguievent?style=for-the-badge&link=https%3A%2F%2Fpypi.org%2Fproject%2Fpyguievent%2F)  ![PyPI - Downloads](https://img.shields.io/pypi/dm/pyguievent?style=for-the-badge&link=https%3A%2F%2Fpypi.org%2Fproject%2Fpyguievent%2F)
# 介绍
基于PySimpleGUI的简单事件循环库，提供装饰器风格的事件绑定功能。本库自身只依赖标准库，兼容 python3.4+。

[PYPI主页地址](https://pypi.org/project/pyguievent/)
# 为什么要用这个库
为啥要搞这玩意,这玩意具体是用来干嘛的？
在GUI开发中肯定会遇到事件以及事件调用的函数,这个在pysimplegui里面使用的并不好,以下是一个例子
~~~python
if event == "btn1":
    do_something()
~~~
以上需要写很多冗长的if else 语句，而本库则提供了一种更简单的方法，只需要编写一个函数，然后在这个函数上使用装饰器,就可以实现事件的函数的绑定

~~~python
@app.bind_event('btn1')
def on_do_something():
    pass
~~~

## 安装
~~~bash
pip install pyguievent
~~~

## 版本兼容性
本库自身兼容 python3.4+，只使用标准库；实际的python版本下限取决于所安装的GUI库。

## 库支持的GUI框架
1. **PySimpleGUI** - 主要支持的框架
2. **FreeSimpleGUI** - 未安装PySimpleGUI时自动回退使用，API兼容

## 特别说明
使用PySimpleEvent类时，事件绑定和事件函数只能接受以下形式：
1. func()，这种无参数函数
2. func(values=)，这种关键字参数函数，只有一个参数是值
3. func(window=)，这种关键字参数函数，只有一个参数是窗口
4. func(event=)，这种关键字参数函数，只有一个参数是事件
5. 参数有window和event,values,顺序无所谓（处理函数以关键字参数方式调用，参数书写顺序不影响取值）
6. sg.Window 窗口对象必须要使用finalize=True
7. 事件处理函数建议以 **on_** 开头（命名约定，非强制）
8. 回车键事件只在"当前获得焦点的文本框"上触发该文本框key绑定的函数，焦点在其他控件上时回车不触发任何事件；窗口需要开启 `return_keyboard_events=True` 才能收到回车事件。弹窗（sg.popup）按钮的回车由PySimpleGUI原生处理，不受影响
9. 一个key只能绑定一个事件函数，同一个key重复绑定时，**最先绑定的生效**；一个事件函数可以被多个key绑定

## 使用方法

~~~python
import PySimpleGUI as sg
from pyguievent import PySimpleEvent

app = PySimpleEvent()


def make_main_window() -> sg.Window:
    task_list = [
        sg.Frame(
            "Tasks",
            [
                [sg.Input(key="lot1", tooltip="此输入栏输入即事件触发", enable_events=True)],
                [sg.Input(key="lot2", tooltip="此输入框输入后使用回车事件触发")],
                [sg.B("win_fun"), sg.B("val_fun")],
                [
                    sg.B("win_val_fun"),
                    sg.B("no_arg_fun"),
                ],
                [sg.Text("", key="lot3")],
                [sg.Text("", key="lot4")],
            ],
            size=(400, 200),
        )
    ]

    status_bar = [
        sg.StatusBar("版本:"),
        sg.StatusBar("状态:"),
    ]

    menu_def = [
        ["&程序", ["关于", "保存配置", "Exit"]],
        ["&帮助", "&使用说明..."],
    ]

    top_menu = [sg.Menu(menu_def)]

    layout = [top_menu, task_list, status_bar]

    # 3.建窗口
    return sg.Window(
        "测试程式窗口",
        layout,
        keep_on_top=True,
        finalize=True,  # 这个属性是必须要的
        return_keyboard_events=True,  # 如果需要回车事件，这个属性是必须要的
    )


@app.bind_event('保存配置')
def on_save_options():
    sg.popup("you click save options")


@app.bind_event('lot1')
def on_input_lot1(window: sg.Window, values: dict):
    window["lot4"].update(values.get("lot1"))


@app.bind_event('lot2')
def on_enter_lot2(window: sg.Window, values: dict):
    new_text = "您输入的是：{}".format(values.get("lot2"))
    window["lot3"].update(new_text)


@app.bind_event(["no_arg_fun", "关于"])
def on_no_arg_fun():
    sg.popup(
        "软件说明：",
        "关于事件，点击菜单关于启动",
        title="关于程序",
        keep_on_top=True,
    )


@app.bind_event("win_fun")
def on_win_fun(window: sg.Window):
    sg.popup(
        "软件说明：",
        "新建任务",
        title="关于程序",
        keep_on_top=True,
    )
    window["lot2"].set_focus(force=True)


@app.bind_event("val_fun")
def on_val_fun(values: dict):
    lot1 = values.get("lot1")
    lot2 = values.get("lot2")
    sg.popup(
        "软件说明：",
        "新建任务",
        lot1,
        lot2,
        title="关于程序",
        keep_on_top=True,
    )


@app.bind_event("win_val_fun")
def on_win_val_fun(window: sg.Window, values: dict):
    sg.popup(
        "软件说明：",
        "新建任务",
        title="关于程序",
        keep_on_top=True,
    )
    lot1 = values.get("lot1")
    window["lot3"].update(lot1)


def main():
    main_window = make_main_window()

    # 增加了一个Exit退出事件
    app.run_event(main_window, "Exit")


if __name__ == '__main__':
    main()

~~~

## 单例窗口 singleton_window

窗口工厂函数使用 `singleton_window` 装饰后，相同参数只创建一个窗口实例：
窗口未关闭时再次调用会置顶显示并返回已有实例，已关闭时自动清理并重建。
相同逻辑参数无论用位置参数还是关键字参数传入，都视为同一实例。

~~~python
import PySimpleGUI as sg
from pyguievent import singleton_window

@singleton_window
def make_settings_window():
    return sg.Window("设置", [[sg.Ok()]], finalize=True)

win1 = make_settings_window()
win2 = make_settings_window()  # 返回同一个窗口并置顶

# 附带的实例管理方法
make_settings_window.get_instance_count()  # 当前实例数量
make_settings_window.remove_instance()     # 移除指定参数对应的实例
make_settings_window.clear_instances()     # 清理所有实例
~~~

完整示例见 `demos/basic_window.py`。
