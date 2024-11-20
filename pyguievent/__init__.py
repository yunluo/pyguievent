#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from typing import Callable, Union

try:
    import PySimpleGUI as sg
except ImportError:
    # 默认使用PySimpleGUI，但是在版本5后收费
    # 所以这里使用免费版的FreeSimpleGUI
    import FreeSimpleGUI as sg

logger = logging.getLogger(__name__)

__version__ = "0.0.3"
__author__ = "yunluo"


class PySimpleEvent:
    """
    使用该类创建GUI的事件循环。
    使用方法：
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
    """

    def __init__(self) -> None:
        """
        初始化一个事件数据字典
        """
        self._event_handlers = {}
        # 定义回车键和特殊键的集合，用于后续判断特定键盘事件
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
            logger.error("Function {} is not callable.".format(func))
            return

        # 确保事件键的唯一性
        if event not in self._event_handlers:
            self._event_handlers[event] = func

    def bind_event(self, event_names: Union[str, list]):
        """
        一个key只能对应一个事件函数,一个事件函数可以被多个key绑定
        举例：回车和确定按钮可以提交数据，但是按钮提交不可以即提交数据又做其他事
        :param event_names: 事件名，可以是字符串或列表，都是GUI的组件key
        :return: 装饰器函数
        """

        def decorator(func: Callable):
            if isinstance(event_names, str):
                self._add_event(event_names, func)
            elif isinstance(event_names, list):
                for event_name in event_names:
                    self._add_event(event_name, func)
            else:
                logger.warning("Invalid event_names: {}".format(event_names))

            # 预处理函数的参数信息
            func_args = func.__code__.co_varnames  # noqa 类型是tuple
            func_arg_count = func.__code__.co_argcount  # noqa 类型是init
            self._event_handlers[func] = {"args": func_args, "count": func_arg_count}

            return func

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
            # 根据事件类型查找对应的处理函数
            # 如果事件是回车键或特殊键，尝试获取焦点元素对应的处理函数
            elem = window.find_element_with_focus()
            handler = (
                self._event_handlers.get(event)
                if event not in self._enter_keys
                else self._event_handlers.get(elem.key)
                if elem is not None
                else None
            )
            # 如果没有找到处理函数，则直接返回
            if handler is None:
                # 这里不做任何提示，是因为在GUI开发中会有太多事件没有绑定处理函数的情况
                # 典型的就是数据输入情况，会出现每个输入都在这里报错
                return

            handler_info = self._event_handlers.get(handler, {})
            arg_count = handler_info.get("count", 0)

            # 如果处理函数没有参数，则直接调用
            if arg_count == 0:
                handler()
                return

            vars_name = handler_info.get("args", ())
            args = []
            # 根据处理函数的参数名，决定如何调用处理函数
            if "window" in vars_name:
                args.append(window)
            if "event" in vars_name:
                args.append(event)
            if "values" in vars_name:
                args.append(values)

            if len(args) == arg_count:
                handler(*args)
            else:
                logger.warning(
                    "Handler {} expects {} arguments, but {} were provided.".format(
                        handler, arg_count, len(args)
                    )
                )

        except Exception as e:
            logger.error(
                "An exception occurred during event handling for event {}: {}".format(
                    event, e
                )
            )

    def run_event(
        self,
        main_window: sg.Window,
        close_event: str = None,  # type: ignore
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
                    logger.warning("No window_obj found")
                    break

                window, event, values = window_obj

                if window_log:
                    logger.debug("Event: {}, Values: {}".format(event, values))

                if window is None:
                    logger.warning("No window found")
                    break

                if event in (sg.WIN_CLOSED, close_event):
                    window.close()

                    if window == main_window:
                        break

                else:
                    self.apply_event(window, event, values)  # type: ignore
        finally:
            if main_window:
                main_window.close()
