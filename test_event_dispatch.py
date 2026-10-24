#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试事件分发与 singleton_window 的稳定性（不依赖真实GUI窗口）
覆盖：参数顺序无关、装饰器链、绑定方法、重复绑定、签名探测、
     不可哈希参数、缺少was_closed/bring_to_front的对象
"""

from pyguievent import PySimpleEvent, singleton_window


# 模拟窗口，只实现 apply_event 需要用到的方法
class MockWindow:
    def __init__(self, focused_elem=None):
        self._focused_elem = focused_elem

    def find_element_with_focus(self):
        return self._focused_elem


app = PySimpleEvent()
received = {}


@app.bind_event("btn_order")
def on_order(values, window):
    # 故意把 values 写在 window 前面，验证参数顺序无关
    received["order"] = (window is not None, values == {"k": "v"})


def my_decorator(func):
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)

    wrapped.__wrapped__ = func
    return wrapped


@my_decorator
@app.bind_event("btn_decorated")
def on_decorated(window, values):
    received["decorated"] = (window is not None, values == {"k": "v"})


class Handler(object):
    def __init__(self):
        self.called_with = None

    def on_method(self, window, values):
        # 绑定方法：self 由绑定传入，不应计入分发参数
        self.called_with = (window is not None, values == {"k": "v"})


handler_obj = Handler()
# 绑定方法需在实例化后注册（类体里装饰拿到的是未绑定函数，无法确定实例）
app.bind_event("btn_method")(handler_obj.on_method)

# 模拟重复绑定：同key第二个函数不应生效
@app.bind_event("btn_dup")
def on_dup_first(values):
    received["dup"] = "first"


@app.bind_event("btn_dup")
def on_dup_second(values):
    received["dup"] = "second"


# 直接用 _add_event 注册（没有元数据，需动态探测签名）
def probe_handler(window, values):
    received["probe"] = (window is not None, values == {"k": "v"})


app._add_event("btn_probe", probe_handler)


# 文档声明的其余处理函数形式
@app.bind_event("btn_noarg")
def on_no_arg():
    received["noarg"] = True


@app.bind_event("btn_event_only")
def on_event_only(event):
    received["event_only"] = event


@app.bind_event("btn_all")
def on_all(window, event, values):
    received["all"] = (window is not None, event == "btn_all", values == {"k": "v"})


def test_no_arg_handler():
    """形式1：无参数处理函数"""
    received.clear()
    app.apply_event(MockWindow(None), "btn_noarg", {"k": "v"})
    assert received.get("noarg") is True, "无参数处理函数未触发: {}".format(received)
    print("[OK] 无参数处理函数正常分发")


def test_event_only_handler():
    """形式4：只有event参数的处理函数，收到事件名字符串"""
    received.clear()
    app.apply_event(MockWindow(None), "btn_event_only", {"k": "v"})
    assert received.get("event_only") == "btn_event_only", "event参数未收到事件名: {}".format(
        received
    )
    print("[OK] 仅event参数的处理函数收到事件名")


def test_all_params_handler():
    """形式5：window/event/values 三参数全带"""
    received.clear()
    app.apply_event(MockWindow(None), "btn_all", {"k": "v"})
    assert received.get("all") == (True, True, True), "三参数分发失败: {}".format(received)
    print("[OK] window/event/values 三参数全带正常分发")


def test_get_events_registry():
    """get_events 应包含已注册的key"""
    for key in ("btn_order", "btn_decorated", "btn_method", "btn_dup", "btn_probe"):
        assert key in app.get_events, "get_events缺少key: {}".format(key)
    print("[OK] get_events 注册表完整")


def test_argument_order_independent():
    """处理函数参数书写顺序不影响取值"""
    received.clear()
    app.apply_event(MockWindow(None), "btn_order", {"k": "v"})
    assert received.get("order") == (True, True), "参数顺序无关性失败: {}".format(received)
    print("[OK] 处理函数参数顺序无关")


def test_decorator_chain():
    """叠加自定义装饰器后元数据仍能正确获取"""
    received.clear()
    app.apply_event(MockWindow(None), "btn_decorated", {"k": "v"})
    assert received.get("decorated") == (True, True), "装饰器链分发失败: {}".format(received)
    print("[OK] 装饰器链叠加后正常分发")


def test_bound_method():
    """类绑定方法作为处理函数，self 不占用分发参数"""
    received.clear()
    handler_obj.called_with = None
    app.apply_event(MockWindow(None), "btn_method", {"k": "v"})
    assert handler_obj.called_with == (True, True), "绑定方法分发失败: {}".format(
        handler_obj.called_with
    )
    print("[OK] 绑定方法正常分发（self不计入）")


def test_duplicate_binding_first_wins():
    """同一个key重复绑定只生效最先绑定的函数"""
    received.clear()
    app.apply_event(MockWindow(None), "btn_dup", {"k": "v"})
    assert received.get("dup") == "first", "重复绑定应最先绑定的生效: {}".format(received)
    print("[OK] 重复绑定最先绑定的生效")


def test_probe_signature():
    """直接 _add_event 注册的函数能通过签名探测正确分发"""
    received.clear()
    app.apply_event(MockWindow(None), "btn_probe", {"k": "v"})
    assert received.get("probe") == (True, True), "签名探测分发失败: {}".format(received)
    print("[OK] 未登记元数据的函数通过签名探测正常分发")


def test_handler_exception_isolated():
    """处理函数抛异常不影响主循环，只记录日志"""
    app2 = PySimpleEvent()

    @app2.bind_event("btn_bad")
    def on_bad(window, values):
        raise RuntimeError("boom")

    # 不应向外抛异常
    app2.apply_event(MockWindow(None), "btn_bad", {"k": "v"})
    print("[OK] 处理函数异常被隔离")


# ---------------- singleton_window 稳定性 ----------------

@singleton_window
def make_plain_window(title, tags=None):
    """返回不支持 was_closed/bring_to_front 的普通对象"""
    return {"title": title, "tags": tags}


@singleton_window
def make_closable_window(title):
    """返回带 was_closed/bring_to_front 的模拟对象"""
    class ClosableWindow(object):
        def __init__(self, t):
            self.title = t
            self._closed = False

        def was_closed(self):
            return self._closed

        def bring_to_front(self):
            self.bring_to_front_called = True

    return ClosableWindow(title)


def test_singleton_unhashable_args():
    """参数包含不可哈希对象（列表）时不报错，且相同参数返回同一实例"""
    w1 = make_plain_window("文档", tags=["a", "b"])
    w2 = make_plain_window("文档", tags=["a", "b"])
    assert w1 is w2, "列表参数应命中同一实例"
    assert make_plain_window.get_instance_count() == 1
    make_plain_window.clear_instances()
    print("[OK] 不可哈希参数不报错")


def test_singleton_plain_object():
    """窗口对象不支持 was_closed/bring_to_front 时不报错，仍保持单例"""
    w1 = make_plain_window("plain")
    w2 = make_plain_window("plain")
    assert w1 is w2, "普通对象也应命中同一实例"
    make_plain_window.clear_instances()
    print("[OK] 缺少was_closed/bring_to_front的对象不报错")


def test_singleton_closed_rebuild():
    """窗口关闭后再次调用创建新实例"""
    w1 = make_closable_window("closable")
    w2 = make_closable_window("closable")
    assert w1 is w2, "未关闭时应返回同一实例"
    assert getattr(w2, "bring_to_front_called", False), "未关闭时应置顶"
    w2._closed = True
    w3 = make_closable_window("closable")
    assert w1 is not w3, "关闭后应创建新实例"
    assert w3.was_closed() is False
    make_closable_window.clear_instances()
    print("[OK] 关闭后自动清理并重建")


def test_singleton_remove_instance():
    """remove_instance 能精确移除对应实例"""
    make_closable_window("r1")
    make_closable_window("r2")
    assert make_closable_window.get_instance_count() == 2
    make_closable_window.remove_instance("r1")
    assert make_closable_window.get_instance_count() == 1
    make_closable_window.clear_instances()
    assert make_closable_window.get_instance_count() == 0
    print("[OK] remove_instance/clear_instances 正常")


if __name__ == "__main__":
    try:
        test_argument_order_independent()
        test_decorator_chain()
        test_bound_method()
        test_duplicate_binding_first_wins()
        test_probe_signature()
        test_no_arg_handler()
        test_event_only_handler()
        test_all_params_handler()
        test_get_events_registry()
        test_handler_exception_isolated()
        test_singleton_unhashable_args()
        test_singleton_plain_object()
        test_singleton_closed_rebuild()
        test_singleton_remove_instance()

        print("[SUCCESS] 所有事件分发与singleton稳定性测试通过！")
    except AssertionError as e:
        print("[FAILED] 测试失败: {}".format(e))
        raise
