#! /usr/bin/python3
# -*- coding: utf-8 -*-
import functools
import logging
from typing import Callable, Union, Dict, Any, Optional, List


try:
    import PySimpleGUI as sg  # noqa
except ImportError:
    sg = None  # type: ignore

try:
    import wx  # noqa
except ImportError:
    wx = None  # type: ignore

__version__ = "0.0.10 "
__author__ = "yunluo"
__license__ = "GPL-3.0-or-later"


__all__ = ['PySimpleEvent', 'PySimpleEventWx', 'singleton_window']

_logger = logging.getLogger(__name__)

def singleton_window(func: Callable):
    """
    窗口单例化装饰器，确保相同参数的窗口函数只创建一个实例。
    如果窗口已关闭，会自动清理并创建新窗口；如果窗口仍存在，会置顶显示。
    
    优化特性：
    - 自动清理已关闭的窗口，防止内存泄漏
    - 线程安全的实例管理
    - 更高效的键生成算法
    - 完整的类型注解
    - 支持手动清理实例
    - 正确处理位置参数和关键字参数的对应关系
    
    Args:
        func: 窗口创建函数
        
    Returns:
        装饰后的窗口函数
        
    Example:
        @singleton_window
        def create_window(title: str):
            return sg.Window(title, [[sg.Text("Hello")]], finalize=True)
    """
    import threading
    import inspect
    
    _instances = {}
    _lock = threading.RLock()
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 使用inspect.signature正确处理参数绑定
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            # 创建规范化的参数字典，确保位置参数和关键字参数的一致性
            normalized_args = tuple(bound_args.arguments.items())
        except Exception:
            # 如果参数绑定失败，回退到简单方式
            normalized_args = (args, frozenset(kwargs.items()))
        
        # 生成键
        key = (func.__name__, normalized_args)
        
        with _lock:
            # 检查现有实例
            if key in _instances:
                window = _instances[key]
                try:
                    # 安全检查窗口是否已关闭
                    if hasattr(window, 'was_closed') and not window.was_closed():
                        # 窗口仍存在，置顶显示
                        if hasattr(window, 'bring_to_front'):
                            window.bring_to_front()
                        return window
                    else:
                        # 窗口已关闭，清理引用
                        del _instances[key]
                except Exception as e:
                    # 窗口对象出现异常，清理引用
                    _logger.warning(f"Error checking window state for {func.__name__}: {e}")
                    if key in _instances:
                        del _instances[key]
        
        # 创建新窗口
        try:
            new_window = func(*args, **kwargs)
            with _lock:
                _instances[key] = new_window
            return new_window
        except Exception as e:
            _logger.error(f"Error creating window for {func.__name__}: {e}")
            raise
    
    # 添加清理方法
    def clear_instances():
        """清理所有窗口实例"""
        with _lock:
            _instances.clear()
    
    def get_instance_count():
        """获取当前实例数量"""
        with _lock:
            return len(_instances)
    
    def remove_instance(*args, **kwargs):
        """移除特定实例"""
        # 使用与wrapper相同的键生成逻辑
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            normalized_args = tuple(bound_args.arguments.items())
        except Exception:
            normalized_args = (args, frozenset(kwargs.items()))
        
        key = (func.__name__, normalized_args)
        with _lock:
            if key in _instances:
                del _instances[key]
    
    # 将辅助方法附加到wrapper函数上
    wrapper.clear_instances = clear_instances
    wrapper.get_instance_count = get_instance_count
    wrapper.remove_instance = remove_instance
    wrapper._instances = _instances  # 用于调试，实际使用中不建议直接访问
    
    return wrapper

 
class PySimpleEvent:
    """
    使用该类创建GUI的事件循环。
    使用方法：
    import PySimpleGUI as sg
    from pyguievent import PySimpleEvent

    app = PySimpleEvent()

    @app.bind_event("_CLICK_")
    def print_when_click(window: Any, values: dict):
        print("click it!")

    @app.bind_event(["_CLICK1_","_CLICK2_"])
    def print_when_more_click(window: Any, values: dict):
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

        if not str(func.__name__).startswith("on_"):
            _logger.error("function {} is not start with on_.".format(func))
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
                raise TypeError("event_names must be a string or a list of strings")  # noqa

            # 预处理函数的参数信息
            func_args = func.__code__.co_varnames  # noqa 类型是tuple
            func_arg_count = func.__code__.co_argcount  # noqa 类型是init
            self._event_handlers[func] = {"args": func_args, "count": func_arg_count}

            return func

        return decorator

    def apply_event(self, window: Any, event: str, values: dict) -> None:
        """
        处理事件,需要注意的时，默认支持以下五种函数，够用
        1.func()，这种无参数函数
        2.func(values=)，这种关键字参数函数，只有一个参数是值
        3.func(window=)，这种关键字参数函数，只有一个参数是窗口
        4.func(event=)，这种关键字参数函数，只有一个参数是事件
        5.参数有window和event,values，顺序无所谓
        回车键的处理规则：只在"当前获得焦点的文本框"上触发该文本框key绑定的事件函数，
        焦点在其他控件（按钮、列表等）上时按回车不会触发任何事件。
        弹窗按钮的回车由PySimpleGUI原生处理（弹窗按钮自带bind_return_key=True，
        回车以按钮key作为事件返回），不经过本方法的回车分支。
        :param window:窗口对象
        :param event:事件名
        :param values:值
        :return:None
        """
        try:
            # 普通事件直接按事件名查找处理函数
            if event not in self._enter_keys:
                handler = self._event_handlers.get(event)
            else:
                # 回车键只对当前获得焦点的文本框生效，且焦点元素必须就是该文本框
                elem = window.find_element_with_focus()
                handler = (
                    self._event_handlers.get(elem.key)
                    if elem is not None and self._is_input_element(elem)
                    else None
                )
            # 如果没有找到处理函数，则直接返回
            if not handler:
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

    @staticmethod
    def _is_input_element(elem: Any) -> bool:
        """
        判断控件是否为文本框（单行输入框），回车键事件只允许在获得焦点的文本框上触发
        :param elem:PySimpleGUI控件对象
        :return:是否为文本框
        """
        if sg is None:
            return True
        return isinstance(elem, (sg.Input, sg.InputText))

    def run_event(
        self,
        main_window: Any,
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
            main_window.disable_debugger()
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
                    self.apply_event(window, event, values)  # type: ignore
        finally:
            if main_window:
                main_window.close()


class PySimpleEventWx:
    """
    使用该类创建wxPython的事件循环。
    使用方法：
    import wx
    from pyguievent import PySimpleEventWx

    app = PySimpleEventWx()

    @app.bind_event(wx.EVT_BUTTON, button_id)
    def on_button_click(event):
        print("Button clicked!") 

    # 也支持绑定到多个组件
    @app.bind_event(wx.EVT_TEXT, [text_id1, text_id2])
    def on_text_change(event):
        print("Text changed!")

    # 然后在wxPython应用中使用
    frame = wx.Frame(None, title="测试窗口")
    app.run_event(frame)
    """

    def __init__(self) -> None:
        """
        初始化事件处理器字典
        """
        if wx is None:
            raise ImportError("wxPython is required for PySimpleEventWx")
            
        self._event_handlers = {} # Dict[int, Dict[Callable, Dict[str, Any]]]
        self._bound_events = {} # Dict[wx.Window, List]
        self._main_window = None # Optional[wx.Window]
    
    @property
    def get_events(self) -> Dict[int, Dict[Callable, Dict[str, Any]]]:
        """
        获取所有已注册的事件
        :return: 事件字典
        """
        return self._event_handlers
    
    def _add_event(self, event_type: int, handler_id: Union[int, str], func: Callable) -> None:
        """
        添加事件处理器
        :param event_type: wxPython事件类型,如wx.EVT_BUTTON
        :param handler_id: 事件处理器ID,可以是组件ID或自定义标识符
        :param func: 事件处理函数
        """
        if not hasattr(handler_id, '__int__'):
            # 对于非整数类型的handler_id，尝试将其转换为字符串的哈希值
            handler_id = hash(str(handler_id))
        else:
            handler_id = int(handler_id)
        
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = {}
        
        # 存储函数及其参数信息
        func_args = func.__code__.co_varnames
        func_arg_count = func.__code__.co_argcount
        
        self._event_handlers[event_type][handler_id] = {
            'func': func,
            'args': func_args,
            'count': func_arg_count
        }
    
    def bind_event(self, event_type: int, handler_ids: Union[int, str, List[Union[int, str]]]):
        """
        事件绑定装饰器
        :param event_type: wxPython事件类型,如wx.EVT_BUTTON
        :param handler_ids: 处理器ID或ID列表
        :return: 装饰器函数
        """
        def decorator(func: Callable):
            if isinstance(handler_ids, (int, str)):
                self._add_event(event_type, handler_ids, func)
            elif isinstance(handler_ids, list):
                for handler_id in handler_ids:
                    self._add_event(event_type, handler_id, func)
            else:
                raise TypeError("handler_ids must be an int, str, or a list of ints or strs")
            
            return func
        
        return decorator
    
    def apply_event(self, event: wx.Event) -> None:
        """
        处理事件
        :param event: wxPython事件对象
        """
        try:
            # 获取事件类型和触发事件的窗口组件
            event_type = event.GetEventType()
            window = event.GetEventObject()
            window_id = window.GetId()
            
            # 查找对应的事件处理器
            if event_type in self._event_handlers:
                handlers = self._event_handlers[event_type]
                
                # 优先查找精确匹配的处理器
                if window_id in handlers:
                    handler_info = handlers[window_id]
                    func = handler_info['func']
                    args = handler_info['args']
                    arg_count = handler_info['count']
                    
                    # 根据函数参数决定如何调用
                    if arg_count == 0:
                        func()
                    elif 'event' in args:
                        func(event)
                    else:
                        # 默认传递event参数
                        func(event)
                else:
                    # 尝试查找是否有使用字符串ID绑定的处理器
                    for handler_id, handler_info in handlers.items():
                        if isinstance(handler_id, int):
                            continue
                        
                        func = handler_info['func']
                        args = handler_info['args']
                        arg_count = handler_info['count']
                        
                        if arg_count == 0:
                            func()
                        elif 'event' in args:
                            func(event)
                        else:
                            func(event)
        except Exception as e:
            _logger.error("An exception occurred during event handling: {}".format(e))
    
    def _wx_event_handler(self, event_type: int):
        """
        创建wxPython事件处理器包装器
        :param event_type: 事件类型
        :return: 事件处理器函数
        """
        def handler(event: wx.Event):
            self.apply_event(event)
            # 允许事件继续传播
            event.Skip()
        
        return handler
    
    def run_event(self, main_window: wx.Window, start_loop: bool = True) -> None:
        """
        绑定所有注册的事件并启动主循环
        :param main_window: 主窗口对象
        :param start_loop: 是否启动事件循环
        """
        self._main_window = main_window
        
        # 为每个注册的事件类型绑定处理器
        for event_type, handlers in self._event_handlers.items():
            # 创建一个通用的事件处理器
            wx_handler = self._wx_event_handler(event_type)
            
            # 绑定到主窗口
            main_window.Bind(event_type, wx_handler)
            
            # 记录已绑定的事件
            if main_window not in self._bound_events:
                self._bound_events[main_window] = []
            self._bound_events[main_window].append((event_type, wx_handler))
        
        # 如果需要，启动应用程序主循环
        if start_loop:
            app = wx.GetApp()
            if app is None:
                app = wx.App()
            main_window.Show()
            app.MainLoop()
    
    def unbind_all(self) -> None:
        """
        解绑所有已绑定的事件
        """
        for window, events in self._bound_events.items():
            for event_type, handler in events:
                window.Unbind(event_type, handler=handler)
        self._bound_events.clear()
