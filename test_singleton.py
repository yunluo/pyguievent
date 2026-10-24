#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的 singleton_window 装饰器
"""

import sys
import time
import threading
from typing import List
import PySimpleGUI as sg
from pyguievent import singleton_window


# 测试1: 基本功能测试
@singleton_window
def create_test_window(title: str, content: str = "默认内容"):
    """创建测试窗口"""
    layout = [
        [sg.Text(f"窗口标题: {title}")],
        [sg.Text(f"内容: {content}")],
        [sg.Text(f"创建时间: {time.strftime('%H:%M:%S')}")],
        [sg.Button("关闭"), sg.Button("测试按钮")]
    ]
    return sg.Window(title, layout, finalize=True, size=(300, 150))


# 测试2: 不同参数的窗口
@singleton_window
def create_counter_window(counter_id: int):
    """创建计数器窗口"""
    layout = [
        [sg.Text(f"计数器 ID: {counter_id}")],
        [sg.Text("0", key="-COUNT-")],
        [sg.Button("增加"), sg.Button("关闭")]
    ]
    return sg.Window(f"计数器 {counter_id}", layout, finalize=True, size=(250, 120))


# 测试3: 线程安全测试
def thread_test(window_id: int, results: List):
    """线程测试函数"""
    try:
        window = create_test_window(f"线程窗口 {window_id}", f"来自线程 {window_id}")
        results.append(f"线程 {window_id} 成功创建窗口")
        window.close()
    except Exception as e:
        results.append(f"线程 {window_id} 失败: {e}")


def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试1: 基本功能 ===")
    
    # 第一次创建
    window1 = create_test_window("测试窗口1", "第一次创建")
    print(f"第一次创建: {window1}")
    print(f"实例数量: {create_test_window.get_instance_count()}")
    
    # 第二次相同参数调用，应该返回同一个窗口
    window2 = create_test_window("测试窗口1", "第一次创建")
    print(f"第二次调用: {window2}")
    print(f"是否为同一实例: {window1 is window2}")
    
    # 不同参数，应该创建新窗口
    window3 = create_test_window("测试窗口2", "第二次创建")
    print(f"不同参数创建: {window3}")
    print(f"实例数量: {create_test_window.get_instance_count()}")
    
    # 清理
    window1.close()
    window2.close()
    window3.close()
    create_test_window.clear_instances()
    print("基本功能测试完成\n")


def test_memory_cleanup():
    """测试内存清理功能"""
    print("=== 测试2: 内存清理 ===")
    
    # 创建窗口
    window = create_test_window("内存测试", "将被关闭")
    print(f"创建窗口后实例数量: {create_test_window.get_instance_count()}")
    
    # 关闭窗口
    window.close()
    time.sleep(0.1)  # 等待关闭完成
    
    # 再次调用，应该创建新窗口（因为旧窗口已关闭）
    new_window = create_test_window("内存测试", "将被关闭")
    print(f"关闭后重新创建实例数量: {create_test_window.get_instance_count()}")
    print(f"是否为新实例: {window is not new_window}")
    
    new_window.close()
    create_test_window.clear_instances()
    print("内存清理测试完成\n")


def test_thread_safety():
    """测试线程安全"""
    print("=== 测试3: 线程安全 ===")
    
    results = []
    threads = []
    
    # 创建多个线程同时调用装饰器函数
    for i in range(5):
        thread = threading.Thread(target=thread_test, args=(i, results))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 输出结果
    for result in results:
        print(result)
    
    create_test_window.clear_instances()
    print("线程安全测试完成\n")


def test_instance_management():
    """测试实例管理功能"""
    print("=== 测试4: 实例管理 ===")
    
    # 创建多个不同参数的窗口
    window1 = create_counter_window(1)
    window2 = create_counter_window(2)
    window3 = create_counter_window(3)
    
    print(f"创建3个窗口后实例数量: {create_counter_window.get_instance_count()}")
    
    # 移除特定实例
    create_counter_window.remove_instance(2)
    print(f"移除一个实例后数量: {create_counter_window.get_instance_count()}")
    
    # 清理所有实例
    create_counter_window.clear_instances()
    print(f"清理所有实例后数量: {create_counter_window.get_instance_count()}")
    
    window1.close()
    window3.close()
    print("实例管理测试完成\n")


def demo_with_gui():
    """GUI演示"""
    print("=== GUI演示 ===")
    print("将创建几个窗口来演示单例模式...")
    
    # 创建第一个窗口
    win1 = create_test_window("演示窗口1", "这是第一个窗口")
    
    # 尝试创建相同参数的窗口（应该返回现有窗口）
    win1_again = create_test_window("演示窗口1", "这是第一个窗口")
    print(f"重复创建相同窗口: {win1 is win1_again}")
    
    # 创建不同参数的窗口
    win2 = create_test_window("演示窗口2", "这是第二个窗口")
    
    # 创建计数器窗口
    counter_win = create_counter_window(1)
    
    print(f"总共创建了 {create_test_window.get_instance_count() + create_counter_window.get_instance_count()} 个窗口实例")
    print("窗口已创建，请查看GUI...")
    
    # 简单的事件循环
    windows = [win1, win2, counter_win]
    
    while True:
        window, event, values = sg.read_all_windows()
        
        if window in (None, sg.WIN_CLOSED):
            break
            
        if event == "关闭":
            window.close()
            windows.remove(window)
            if not windows:
                break
        elif event == "增加" and window == counter_win:
            current = int(window["-COUNT-"].get())
            window["-COUNT-"].update(str(current + 1))
        elif event == "测试按钮":
            sg.popup("测试按钮被点击！", keep_on_top=True)
    
    # 清理
    create_test_window.clear_instances()
    create_counter_window.clear_instances()
    print("GUI演示完成")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_memory_cleanup()
        test_thread_safety()
        test_instance_management()

        # GUI演示需要真实交互，仅在传入 --gui 参数时运行，
        # 避免自动化环境（CI、无标准输入）下被 input() 阻塞
        if "--gui" in sys.argv:
            demo_with_gui()

        print("所有测试完成！")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()