# 介绍
基于PySimpleGUI的一个简单的事件循环库

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
def do_something():
    pass
~~~

## 安装
~~~bash
pip install pyguievent
~~~

## 版本兼容性
python3.4以上,WindowsXP 以上的Windows系统都可以用，其他系统未测试

## 特别说明
事件绑定和事件函数的有点问题，只能接受以下四种形式
1. func()，这种无参数函数
2. func(values=)，这种关键字参数函数，只有一个参数是值
3. func(window=)，这种关键字参数函数，只有一个参数是窗口
4. func(event=)，这种关键字参数函数，只有一个参数是事件
5. 参数有window和event,values,顺序无所谓
6. sg.Window 窗口对象必须要使用finalize=True


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
        finalize=True,# 这个属性是必须要的
        return_keyboard_events=True,
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
def on_val_fun(values):
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


@app.bind_event(["win_val_fun", "lot2"])
def on_win_val_fun(window, values):
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
