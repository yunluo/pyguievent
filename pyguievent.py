#! /usr/bin/python3
# -*- coding: utf-8 -*-
import functools
import inspect
import logging
import threading

try:
    from typing import Callable, Union  # noqa
except ImportError:
    # Python 3.4 没有 typing 模块，用占位对象保证注解表达式可正常求值
    class _AnnotationStub(object):
        def __getitem__(self, item):
            return None

    Callable = _AnnotationStub()  # type: ignore
    Union = _AnnotationStub()  # type: ignore

try:
    import PySimpleGUI as sg  # noqa
except ImportError:
    try:
        import FreeSimpleGUI as sg  # noqa
    except ImportError:
        sg = None  # type: ignore

_logger = logging.getLogger(__name__)

__version__ = "0.0.11"
__author__ = "yunluo"

__all__ = ["PySimpleEvent", "singleton_window"]


def singleton_window(func: Callable):
    """
    窗口单例化装饰器，确保相同参数的窗口只创建一个实例。
    窗口未关闭时再次调用会置顶显示并返回已有实例，窗口已关闭时自动清理并重建。
    相同的逻辑参数无论用位置参数还是关键字参数传入，都视为同一实例。

    :param func: 窗口创建函数，返回的对象建议支持 was_closed() 和 bring_to_front() 方法
                 （PySimpleGUI的Window对象原生支持），不支持时按"未关闭、不置顶"处理，不会报错
    :return: 装饰后的窗口函数，附带 clear_instances()、get_instance_count()、remove_instance() 管理方法
    """
    _instances = {}
    _lock = threading.RLock()

    def _make_key(args, kwargs):
        # 规范化参数：绑定到函数签名后生成键，
        # 位置参数和关键字参数两种传参方式会得到同一个键
        try:
            bound = inspect.signature(func).bind(*args, **kwargs)
            try:
                bound.apply_defaults()
            except AttributeError:
                pass  # Python 3.4 没有 apply_defaults
            return "{}_{}".format(func.__name__, str(bound.arguments.items()))
        except TypeError:
            # 参数无法绑定时退回原始字符串，参数不可哈希也不会报错
            return "{}_{}_{}".format(func.__name__, str(args), str(kwargs))

    def _is_closed(window):
        try:
            return bool(window.was_closed())
        except AttributeError:
            # 对象不支持was_closed时，视为未关闭
            return False

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = _make_key(args, kwargs)

        with _lock:
            window = _instances.get(key)
            if window is not None:
                if not _is_closed(window):
                    try:
                        window.bring_to_front()
                    except AttributeError:
                        pass
                    return window
                del _instances[key]

        new_window = func(*args, **kwargs)
        with _lock:
            _instances[key] = new_window
        return new_window

    def clear_instances():
        """清理所有窗口实例"""
        with _lock:
            _instances.clear()

    def get_instance_count():
        """获取当前实例数量"""
        with _lock:
            return len(_instances)

    def remove_instance(*args, **kwargs):
        """移除指定参数对应的实例"""
        key = _make_key(args, kwargs)
        with _lock:
            if key in _instances:
                del _instances[key]

    wrapper.clear_instances = clear_instances
    wrapper.get_instance_count = get_instance_count
    wrapper.remove_instance = remove_instance
    return wrapper


class PySimpleEvent:
    """
    使用该类创建GUI的事件循环。
    使用方法：
    import PySimpleGUI as sg
    from pyguievent import PySimpleEvent

    app = PySimpleEvent()

    @app.bind_event("_CLICK_")
    def print_when_click(window: sg.Window, values: dict):
        print("click it!")

    @app.bind_event(["_CLICK1_","_CLICK2_"])
    def print_when_more_click(window: sg.Window, values: dict):
        print('click it!')

    window = sg.Window("测试窗口",layout = [],
                        keep_on_top=True, # 窗口置顶需要的
                        finalize=True, # 这个很重要，多窗口模式才需要这个参数
                        return_keyboard_events=True # 窗口如果需要输入栏回车事件需要这个
                        )

    app.run_event(window)

    回车键的处理规则：只在"当前获得焦点的文本框"上触发该文本框key绑定的事件函数，
    焦点在其他控件（按钮、列表等）上时按回车不会触发任何事件。
    弹窗按钮的回车由PySimpleGUI原生处理（弹窗按钮自带bind_return_key=True，
    回车以按钮key作为事件返回），不经过本类的回车分支。
    """

    def __init__(self) -> None:
        """
        初始化一个事件数据字典
        """
        self._event_handlers = {}
        # 回车键和特殊键的事件名集合
        self._enter_keys = ("special 16777220", "special 16777221", "\r")

    @property
    def get_events(self) -> dict:
        """
        获取所有已注册的事件
        :return:事件字典
        """
        return self._event_handlers

    def _add_event(self, event: str, func: Callable) -> None:
        """
        增加事件，把函数和事件做绑定，但是这里基本不用，实际是被下面的 bind_event调用
        :param event:事件名，是GUI组件的key
        :param func:函数名，注意，这里只写函数名，不带括号
        :return:
        """
        if not callable(func):
            _logger.error("Function {} is not callable.".format(func))
            return

        # 同一个key重复绑定时只生效最先绑定的函数
        if event not in self._event_handlers:
            self._event_handlers[event] = func

    def _get_handler_info(self, handler: Callable) -> dict:
        """
        获取处理函数的元数据
        支持装饰器链：追溯 __wrapped__ 链查找元数据
        """
        if handler in self._event_handlers:
            return self._event_handlers[handler]

        original = handler
        while hasattr(original, "__wrapped__"):
            original = original.__wrapped__
            if original in self._event_handlers:
                return self._event_handlers[original]

        return {}

    @staticmethod
    def _probe_arg_names(handler: Callable) -> tuple:
        """
        探测未经bind_event登记元数据的处理函数的参数名
        用于直接调用 _add_event 注册的函数
        """
        try:
            return tuple(inspect.signature(handler).parameters)
        except (TypeError, ValueError):
            # 部分内置函数或C扩展函数无法获取签名
            return ()

    @staticmethod
    def _is_input_element(elem) -> bool:
        """
        判断控件是否为文本框（单行输入框），回车键事件只允许在获得焦点的文本框上触发
        :param elem:PySimpleGUI控件对象
        :return:是否为文本框
        """
        if sg is None:
            return True
        return isinstance(elem, (sg.Input, sg.InputText))

    def bind_event(self, event_names: Union[str, list]):
        """
        一个key只能对应一个事件函数,一个事件函数可以被多个key绑定
        举例：回车和确定按钮可以提交数据，但是按钮提交不可以即提交数据又做其他事
        同一个key重复绑定时只生效最先绑定的函数
        支持装饰器链叠加：多个职责装饰器按从内到外顺序生效
        :param event_names: 事件名，可以是字符串或列表，都是GUI的组件key
        :return: 装饰器函数
        """

        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            # 追溯 __wrapped__ 链找到最原始的函数，取参数信息
            original_func = func
            while hasattr(original_func, "__wrapped__"):
                original_func = original_func.__wrapped__

            func_arg_count = original_func.__code__.co_argcount
            # 只取参数部分的变量名，避免函数体内的局部变量被误判为参数
            func_args = original_func.__code__.co_varnames[:func_arg_count]
            if inspect.ismethod(original_func):
                # 绑定方法的第一个参数self已经由绑定传入，不计入
                func_args = func_args[1:]
                func_arg_count = max(func_arg_count - 1, 0)

            self._event_handlers[wrapper] = {
                "args": func_args,
                "count": func_arg_count,
                "original": original_func,
            }

            if isinstance(event_names, str):
                self._add_event(event_names, wrapper)
            elif isinstance(event_names, list):
                for event_name in event_names:
                    self._add_event(event_name, wrapper)
            else:
                _logger.warning("Invalid event_names: {}".format(event_names))

            return wrapper

        return decorator

    def apply_event(self, window, event: str, values: dict) -> None:
        """
        处理事件,需要注意的时，默认支持以下五种函数，够用
        1.func()，这种无参数函数
        2.func(values=)，这种关键字参数函数，只有一个参数是值
        3.func(window=)，这种关键字参数函数，只有一个参数是窗口
        4.func(event=)，这种关键字参数函数，只有一个参数是事件
        5.参数有window和event,values，顺序无所谓
        处理函数以关键字参数方式调用，参数书写顺序不影响取值。
        :param window:窗口对象（sg.Window）
        :param event:事件名
        :param values:值
        :return:None
        """
        try:
            if event in self._enter_keys:
                # 回车键只对当前获得焦点的文本框生效，
                # 焦点在按钮、列表等其他控件上时直接忽略
                elem = window.find_element_with_focus() if window is not None else None
                if elem is not None and self._is_input_element(elem):
                    handler = self._event_handlers.get(elem.key)
                else:
                    handler = None
            else:
                handler = self._event_handlers.get(event)

            if not handler:
                return

            handler_info = self._get_handler_info(handler)
            if handler_info:
                vars_name = handler_info.get("args", ())
            else:
                vars_name = self._probe_arg_names(handler)

            # 按参数名装配关键字参数，处理函数参数书写顺序不影响取值
            call_kwargs = {}
            if "window" in vars_name:
                call_kwargs["window"] = window
            if "event" in vars_name:
                call_kwargs["event"] = event
            if "values" in vars_name:
                call_kwargs["values"] = values

            if call_kwargs:
                handler(**call_kwargs)
            else:
                handler()

        except Exception as e:
            _logger.error(
                "An exception occurred during event handling for event {}: {}".format(
                    event, e
                )
            )

    def run_event(
        self,
        main_window,
        close_event: str = None,
        window_log: bool = False,
    ) -> None:
        """
        界面主循环
        :param main_window: 主窗口对象（sg.Window）
        :param window_log: 是否输出事件日志，默认是不输出的
        :param close_event:关闭窗口的key，可以是退出，Exit 等等
        :return: None
        """
        if sg is None:
            raise ImportError(
                "pyguievent requires PySimpleGUI or FreeSimpleGUI, "
                "install one of them first: pip install PySimpleGUI"
            )
        try:
            main_window.finalize()
            while True:
                window_obj = sg.read_all_windows()
                if window_obj is None:
                    _logger.warning("No window_obj found")
                    break

                window, event, values = window_obj

                if window_log:
                    _logger.debug("Event: {}, Values: {}".format(event, values))

                if window is None:
                    break

                if event in (sg.WIN_CLOSED, close_event):
                    window.close()

                    if window == main_window:
                        break

                else:
                    self.apply_event(window, event, values)
        finally:
            if main_window:
                main_window.close()
