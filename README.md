![Static Badge](https://img.shields.io/badge/Python-34-1?style=for-the-badge)  ![PyPI - Version](https://img.shields.io/pypi/v/pyguievent?style=for-the-badge&link=https%3A%2F%2Fpypi.org%2Fproject%2Fpyguievent%2F)  ![PyPI - Downloads](https://img.shields.io/pypi/dm/pyguievent?style=for-the-badge&link=https%3A%2F%2Fpypi.org%2Fproject%2Fpyguievent%2F)
# 介绍
基于PySimpleGUI和wxPython的简单事件循环库，提供装饰器风格的事件绑定功能。

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
python3.4以上,WindowsXP 以上的Windows系统都可以用，其他系统未测试

## 库支持的GUI框架
本库支持两个主要的GUI框架：

1. **PySimpleGUI** - 原始支持的框架
2. **wxPython** - 新增支持的功能完善的GUI框架

## 特别说明（PySimpleGUI）
使用PySimpleEvent类时，事件绑定和事件函数只能接受以下形式：
1. func()，这种无参数函数
2. func(values=)，这种关键字参数函数，只有一个参数是值
3. func(window=)，这种关键字参数函数，只有一个参数是窗口
4. func(event=)，这种关键字参数函数，只有一个参数是事件
5. 参数有window和event,values,顺序无所谓
6. sg.Window 窗口对象必须要使用finalize=True
7. 强制约束事件函数以 **on_** 开头

## 特别说明（wxPython）
使用PySimpleEventWx类时，请注意以下几点：
1. 需要安装wxPython：`pip install wxPython`
2. 事件处理器通常接收一个wx.Event参数
3. 事件绑定使用wxPython的事件类型常量（如wx.EVT_BUTTON）
4. 组件ID可以是整数ID或字符串标识符


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

## 使用方法（wxPython）

```python
import wx
from pyguievent import PySimpleEventWx

# 创建事件管理器实例
app = PySimpleEventWx()

# 创建窗口
frame = wx.Frame(None, title="wxPython示例", size=(400, 300))
panel = wx.Panel(frame)

# 创建组件
button = wx.Button(panel, label="点击我", pos=(50, 50))
text_ctrl = wx.TextCtrl(panel, pos=(50, 100), size=(200, -1))
result_text = wx.StaticText(panel, label="结果将显示在这里", pos=(50, 150))

# 绑定事件 - 按钮点击
@app.bind_event(wx.EVT_BUTTON, button.GetId())
def on_button_click(event):
    result_text.SetLabel("按钮被点击了！")

# 绑定事件 - 文本输入
@app.bind_event(wx.EVT_TEXT, text_ctrl.GetId())
def on_text_change(event):
    text = event.GetString()
    result_text.SetLabel(f"输入的文本: {text}")

# 绑定事件 - 多个组件
# 假设有另一个文本框text_ctrl2
# @app.bind_event(wx.EVT_TEXT, [text_ctrl.GetId(), text_ctrl2.GetId()])
# def on_text_change_multiple(event):
#     # 处理事件

# 运行事件循环
app.run_event(frame)
```

## 在类中使用PySimpleEventWx

```python
import wx
from pyguievent import PySimpleEventWx

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="类中的使用示例", size=(400, 300))
        
        # 创建事件管理器实例
        self.event_manager = PySimpleEventWx()
        
        # 创建UI
        panel = wx.Panel(self)
        self.button = wx.Button(panel, label="类中的按钮", pos=(50, 50))
        
        # 绑定事件
        self._bind_events()
    
    def _bind_events(self):
        # 在类方法中绑定事件
        @self.event_manager.bind_event(wx.EVT_BUTTON, self.button.GetId())
        def on_button_click(event):
            wx.MessageBox("按钮被点击了！", "消息", wx.OK)
    
    def run(self):
        # 运行事件循环
        self.event_manager.run_event(self)

# 创建并运行应用
if __name__ == "__main__":
    frame = MyFrame()
    frame.run()
```

## 查看完整示例

更详细的wxPython示例可以在`examples/wxpython_example.py`文件中找到。


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


@app.bind_event(["win_val_fun", "lot2"])
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
