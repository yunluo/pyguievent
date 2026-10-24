#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的 singleton_window 装饰器核心功能（不依赖PySimpleGUI）
"""

import time
import threading
from typing import List, Any
from pyguievent import singleton_window


# 模拟窗口类
class MockWindow:
    def __init__(self, title: str, content: str = "默认内容"):
        self.title = title
        self.content = content
        self.created_time = time.time()
        self._closed = False
        self.id = id(self)
    
    def was_closed(self) -> bool:
        return self._closed
    
    def close(self):
        self._closed = True
    
    def bring_to_front(self):
        """模拟置顶操作"""
        pass
    
    def __str__(self):
        return f"MockWindow(title={self.title}, id={self.id})"
    
    def __repr__(self):
        return self.__str__()


# 测试1: 基本功能测试
@singleton_window
def create_test_window(title: str, content: str = "默认内容"):
    """创建测试窗口"""
    return MockWindow(title, content)


# 测试2: 不同参数的窗口
@singleton_window
def create_counter_window(counter_id: int):
    """创建计数器窗口"""
    return MockWindow(f"计数器 {counter_id}", f"ID: {counter_id}")


# 测试3: 线程安全测试
def thread_test(window_id: int, results: List):
    """线程测试函数"""
    try:
        window = create_test_window(f"线程窗口 {window_id}", f"来自线程 {window_id}")
        results.append(f"线程 {window_id} 成功创建窗口: {window.id}")
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
    assert window1 is window2, "相同参数应该返回同一实例"
    
    # 不同参数，应该创建新窗口
    window3 = create_test_window("测试窗口2", "第二次创建")
    print(f"不同参数创建: {window3}")
    print(f"实例数量: {create_test_window.get_instance_count()}")
    assert window1 is not window3, "不同参数应该创建不同实例"
    
    # 清理
    window1.close()
    window2.close()
    window3.close()
    create_test_window.clear_instances()
    print("[OK] 基本功能测试通过\n")


def test_memory_cleanup():
    """测试内存清理功能"""
    print("=== 测试2: 内存清理 ===")
    
    # 创建窗口
    window = create_test_window("内存测试", "将被关闭")
    print(f"创建窗口后实例数量: {create_test_window.get_instance_count()}")
    assert create_test_window.get_instance_count() == 1
    
    # 关闭窗口
    window.close()
    time.sleep(0.1)  # 等待关闭完成
    
    # 再次调用，应该创建新窗口（因为旧窗口已关闭）
    new_window = create_test_window("内存测试", "将被关闭")
    print(f"关闭后重新创建实例数量: {create_test_window.get_instance_count()}")
    print(f"是否为新实例: {window is not new_window}")
    assert window is not new_window, "关闭的窗口应该被清理并创建新实例"
    
    new_window.close()
    create_test_window.clear_instances()
    print("[OK] 内存清理测试通过\n")


def test_thread_safety():
    """测试线程安全"""
    print("=== 测试3: 线程安全 ===")
    
    results = []
    threads = []
    
    # 创建多个线程同时调用装饰器函数
    for i in range(10):
        thread = threading.Thread(target=thread_test, args=(i, results))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 检查结果
    success_count = len([r for r in results if "成功" in r])
    print(f"成功创建的线程数: {success_count}/{len(threads)}")
    
    for result in results:
        print(f"  {result}")
    
    create_test_window.clear_instances()
    assert success_count == len(threads), "所有线程都应该成功"
    print("[OK] 线程安全测试通过\n")


def test_instance_management():
    """测试实例管理功能"""
    print("=== 测试4: 实例管理 ===")
    
    # 创建多个不同参数的窗口
    window1 = create_counter_window(1)
    window2 = create_counter_window(2)
    window3 = create_counter_window(3)
    
    print(f"创建3个窗口后实例数量: {create_counter_window.get_instance_count()}")
    assert create_counter_window.get_instance_count() == 3
    
    # 移除特定实例
    create_counter_window.remove_instance(2)
    print(f"移除一个实例后数量: {create_counter_window.get_instance_count()}")
    assert create_counter_window.get_instance_count() == 2
    
    # 清理所有实例
    create_counter_window.clear_instances()
    print(f"清理所有实例后数量: {create_counter_window.get_instance_count()}")
    assert create_counter_window.get_instance_count() == 0
    
    window1.close()
    window3.close()
    print("[OK] 实例管理测试通过\n")


def test_key_generation():
    """测试键生成的正确性"""
    print("=== 测试5: 键生成 ===")
    
    # 测试相同参数生成相同键
    w1 = create_test_window("key_test", "content")
    w2 = create_test_window("key_test", "content")
    assert w1 is w2, "相同参数应该生成相同键"
    
    # 测试参数顺序不同但内容相同
    w3 = create_test_window(title="key_test", content="content")
    assert w1 is w3, "关键字参数应该与位置参数一致"
    
    # 测试不同参数生成不同键
    w4 = create_test_window("key_test", "different_content")
    assert w1 is not w4, "不同内容应该生成不同键"
    
    # 测试空参数
    @singleton_window
    def no_params_window():
        return MockWindow("no_params")
    
    w5 = no_params_window()
    w6 = no_params_window()
    assert w5 is w6, "无参数函数应该返回同一实例"
    
    # 清理
    w1.close()
    w4.close()
    w5.close()
    create_test_window.clear_instances()
    no_params_window.clear_instances()
    print("[OK] 键生成测试通过\n")


def test_error_handling():
    """测试错误处理"""
    print("=== 测试6: 错误处理 ===")
    
    # 测试创建窗口时的异常处理
    failing_call_count = 0
    
    @singleton_window
    def failing_window():
        nonlocal failing_call_count
        failing_call_count += 1
        if failing_call_count < 3:
            raise ValueError("模拟创建失败")
        return MockWindow("最终成功")
    
    # 前两次应该失败
    for i in range(2):
        try:
            failing_window()
            assert False, f"第{i+1}次调用应该失败"
        except ValueError:
            pass
    
    # 第三次应该成功
    w = failing_window()
    assert w is not None, "第三次调用应该成功"
    
    print(f"失败次数: {failing_call_count-1}, 成功创建: {w}")
    w.close()
    failing_window.clear_instances()
    print("[OK] 错误处理测试通过\n")


def run_performance_test():
    """性能测试"""
    print("=== 测试7: 性能测试 ===")
    
    # 测试大量实例创建和清理的性能
    start_time = time.time()
    
    for i in range(100):
        window = create_counter_window(i % 10)  # 创建10种不同的窗口，每种10次
        if i % 20 == 0:  # 偶尔关闭一些窗口
            window.close()
    
    end_time = time.time()
    print(f"创建100个窗口耗时: {end_time - start_time:.4f}秒")
    print(f"最终实例数量: {create_counter_window.get_instance_count()}")
    
    create_counter_window.clear_instances()
    print("[OK] 性能测试通过\n")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_memory_cleanup()
        test_thread_safety()
        test_instance_management()
        test_key_generation()
        test_error_handling()
        run_performance_test()
        
        print("[SUCCESS] 所有测试通过！优化后的 singleton_window 装饰器功能正常。")
        
    except Exception as e:
        print(f"[FAILED] 测试失败: {e}")
        import traceback
        traceback.print_exc()