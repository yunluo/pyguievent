# pyguievent
基于PySimpleGUI的一个简单的事件循环库

## 使用方法

~~~python
import PySimpleGUI as sg
from pyguievent import PySimpleEvent

app = PySimpleEvent()

@app.bind_event("_CLICK_")
def print_when_click(window: sg.Window, values: dict):
    print('click it!')

@app.bind_event(["_CLICK1_","_CLICK2_"])
def print_when_more_click(window: sg.Window, values: dict):
    print('click it!')

window = sg.Window("测试窗口",layout = [],
                    keep_on_top=True, # 窗口置顶需要的
                    finalize=True, # 这个很重要，多窗口模式才需要这个参数
                    return_keyboard_events=True # 窗口如果需要输入栏回车事件需要这个
                    )

app.run_event(window)
~~~
