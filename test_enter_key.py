#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 apply_event 的回车键处理逻辑（不依赖真实GUI窗口）
规则：回车键只对"当前获得焦点的文本框"生效，
     焦点在其他控件上时回车不触发任何事件，
     弹窗按钮的回车由PySimpleGUI原生处理，走普通事件路径。
"""

import PySimpleGUI as sg

from pyguievent import PySimpleEvent


# 模拟窗口，只实现 apply_event 需要用到的方法
class MockWindow:
    def __init__(self, focused_elem=None):
        self._focused_elem = focused_elem

    def find_element_with_focus(self):
        return self._focused_elem


fired = []
app = PySimpleEvent()


@app.bind_event("input_name")
def on_input_name(window, values):
    fired.append("input_name")


@app.bind_event(["btn_ok", "popup_ok"])
def on_ok(window, values):
    fired.append("ok")


def test_enter_on_focused_input():
    """回车 + 焦点在已绑定函数的文本框上 -> 触发"""
    for enter_key in ("\r", "special 16777220", "special 16777221"):
        fired.clear()
        inp = sg.Input("文本", key="input_name")
        app.apply_event(MockWindow(inp), enter_key, {})
        assert fired == ["input_name"], f"回车键 {enter_key!r} 未触发文本框事件, fired={fired}"
    print("[OK] 回车在获得焦点的文本框上正常触发（含小键盘回车）")


def test_enter_on_button_blocked():
    """回车 + 焦点在按钮上 -> 不触发（即使按钮key绑定了函数）"""
    fired.clear()
    btn = sg.Button("确定", key="btn_ok")
    app.apply_event(MockWindow(btn), "\r", {})
    assert fired == [], f"按钮获得焦点时回车不应触发事件, fired={fired}"
    print("[OK] 焦点在按钮上时回车不再触发事件")


def test_enter_on_other_controls_blocked():
    """回车 + 焦点在其他控件（Text/Listbox等）上 -> 不触发"""
    fired.clear()
    text = sg.Text("纯文本", key="a_text")
    app.apply_event(MockWindow(text), "\r", {})
    assert fired == [], f"Text控件获得焦点时回车不应触发事件, fired={fired}"
    print("[OK] 焦点在其他控件上时回车不触发事件")


def test_enter_without_focus():
    """回车 + 无焦点元素 -> 不触发"""
    fired.clear()
    app.apply_event(MockWindow(None), "\r", {})
    assert fired == [], f"无焦点元素时回车不应触发事件, fired={fired}"
    print("[OK] 无焦点元素时回车不触发事件")


def test_enter_on_unbound_input():
    """回车 + 焦点在未绑定函数的文本框上 -> 不触发"""
    fired.clear()
    inp = sg.Input("文本", key="no_bind_input")
    app.apply_event(MockWindow(inp), "\r", {})
    assert fired == [], f"未绑定key的文本框回车不应触发事件, fired={fired}"
    print("[OK] 未绑定函数的文本框回车不触发事件")


def test_normal_event_still_works():
    """普通事件（按钮点击等）不受影响，按事件名触发"""
    fired.clear()
    app.apply_event(MockWindow(None), "btn_ok", {})
    assert fired == ["ok"], f"普通事件路径被影响, fired={fired}"
    print("[OK] 普通事件路径不受影响")


def test_popup_button_event_normal_path():
    """弹窗按钮回车时PySimpleGUI以按钮key作为事件返回，走普通事件路径正常触发"""
    fired.clear()
    app.apply_event(MockWindow(None), "popup_ok", {})
    assert fired == ["ok"], f"弹窗按钮事件路径异常, fired={fired}"
    print("[OK] 弹窗按钮（以按钮key返回的事件）正常触发")


if __name__ == "__main__":
    try:
        test_enter_on_focused_input()
        test_enter_on_button_blocked()
        test_enter_on_other_controls_blocked()
        test_enter_without_focus()
        test_enter_on_unbound_input()
        test_normal_event_still_works()
        test_popup_button_event_normal_path()

        print("[SUCCESS] 所有回车键处理测试通过！")
    except AssertionError as e:
        print(f"[FAILED] 测试失败: {e}")
        raise
