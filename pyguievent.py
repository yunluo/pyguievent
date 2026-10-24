#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import functools
from typing import Callable, Union

try:
    import PySimpleGUI as sg  # noqa
except ImportError:
    import FreeSimpleGUI as sg  # noqa

_logger = logging.getLogger(__name__)

__version__ = "0.0.11"
__author__ = "yunluo"


def singleton_window(func: Callable):
    """
    窗口单例化装饰器
    :param func:
    :return:
    """
    _instances = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = "{}_{}_{}".format(func.__name__, str(args), str(kwargs))

        if key in _instances:
            window = _instances[key]
            if not window.was_closed():
                window.bring_to_front()
                return window

        new_window = func(*args, **kwargs)
        _instances[key] = new_window
        return new_window

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
    """

    def __init__(self) -> None:
        """
        初始化一个事件数据字典
        """
        self._event_handlers = {}
        self._enter_keys = ("special 16777220", "special 16777221", "\r")
        self._wrapper_to_func = {}

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

    def bind_event(self, event_names: Union[str, list]):
        """
        一个key只能对应一个事件函数,一个事件函数可以被多个key绑定
        举例：回车和确定按钮可以提交数据，但是按钮提交不可以即提交数据又做其他事
        支持装饰器链叠加：多个职责装饰器按从内到外顺序生效
        :param event_names: 事件名，可以是字符串或列表，都是GUI的组件key
        :return: 装饰器函数
        """

        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            self._wrapper_to_func[wrapper] = func

            original_func = func
            while hasattr(original_func, "__wrapped__"):
                original_func = original_func.__wrapped__

            func_args = original_func.__code__.co_varnames
            func_arg_count = original_func.__code__.co_argcount
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

    def apply_event(self, window: sg.Window, event: str, values: dict) -> None:
        """
        处理事件,需要注意的时，默认支持以下五种函数，够用
        1.func()，这种无参数函数
        2.func(values=)，这种关键字参数函数，只有一个参数是值
        3.func(window=)，这种关键字参数函数，只有一个参数是窗口
        4.func(event=)，这种关键字参数函数，只有一个参数是事件
        5.参数有window和event,values，顺序无所谓
        :param window:窗口对象
        :param event:事件名
        :param values:值
        :return:None
        """
        try:
            if event in self._enter_keys:
                elem = window.find_element_with_focus() if window else None
                handler = (
                    self._event_handlers.get(elem.key) if elem is not None else None
                )
            else:
                handler = self._event_handlers.get(event)

            if not handler:
                return

            handler_info = self._get_handler_info(handler)
            arg_count = handler_info.get("count", 0)

            if arg_count == 0:
                handler()
                return

            vars_name = handler_info.get("args", ())
            args = []
            if "window" in vars_name:
                args.append(window)
            if "event" in vars_name:
                args.append(event)
            if "values" in vars_name:
                args.append(values)

            if len(args) == arg_count:
                handler(*args)
            else:
                _logger.warning(
                    "Handler {} expects {} arguments, but {} were provided.".format(
                        handler, arg_count, len(args)
                    )
                )

        except Exception as e:
            _logger.error(
                "An exception occurred during event handling for event {}: {}".format(
                    event, e
                )
            )

    def run_event(
        self,
        main_window: sg.Window,
        close_event: str = None,
        window_log: bool = False,
    ) -> None:
        """
        界面主循环
        :param main_window: 主窗口对象
        :param window_log: 是否开启窗口对象，默认是不开的
        :param close_event:关闭窗口的key，可以是退出，Exit 等等
        :return: None
        """
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
