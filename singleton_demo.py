#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化后的 singleton_window 装饰器使用示例
"""

from pyguievent import singleton_window


# 模拟窗口类（如果没有PySimpleGUI）
class MockWindow:
    def __init__(self, title: str, **kwargs):
        self.title = title
        self.kwargs = kwargs
        self._closed = False
    
    def was_closed(self) -> bool:
        return self._closed
    
    def close(self):
        self._closed = True
    
    def bring_to_front(self):
        print(f"窗口 '{self.title}' 已置顶")
    
    def __str__(self):
        return f"MockWindow(title={self.title})"


# 使用优化后的装饰器
@singleton_window
def create_settings_window():
    """创建设置窗口（无参数）"""
    print("创建新的设置窗口")
    return MockWindow("设置")


@singleton_window  
def create_document_window(doc_name: str, readonly: bool = False):
    """创建文档窗口"""
    print(f"创建文档窗口: {doc_name} (只读: {readonly})")
    return MockWindow(f"文档: {doc_name}", readonly=readonly)


def demo_optimized_features():
    """演示优化后的功能"""
    print("=== 优化后的 singleton_window 装饰器演示 ===\n")
    
    # 1. 基本单例功能
    print("1. 基本单例功能:")
    win1 = create_settings_window()
    win2 = create_settings_window()
    print(f"两次调用是否返回同一实例: {win1 is win2}")
    print(f"当前实例数量: {create_settings_window.get_instance_count()}")
    print()
    
    # 2. 参数化单例
    print("2. 参数化单例:")
    doc1 = create_document_window("报告.pdf")
    doc2 = create_document_window("报告.pdf")  # 相同参数，返回同一实例
    doc3 = create_document_window("总结.docx")  # 不同参数，创建新实例
    doc4 = create_document_window("报告.pdf", readonly=True)  # 不同参数，创建新实例
    
    print(f"报告.pdf (两次调用): {doc1 is doc2}")
    print(f"报告.pdf vs 总结.docx: {doc1 is not doc3}")
    print(f"报告.pdf vs 报告.pdf(只读): {doc1 is not doc4}")
    print(f"文档窗口实例数量: {create_document_window.get_instance_count()}")
    print()
    
    # 3. 内存自动清理
    print("3. 内存自动清理:")
    print("关闭设置窗口...")
    win1.close()
    
    # 再次调用应该创建新实例（因为旧的已关闭）
    win5 = create_settings_window()
    print(f"关闭后重新创建是否为新实例: {win1 is not win5}")
    print()
    
    # 4. 实例管理
    print("4. 实例管理:")
    print(f"当前设置窗口实例数量: {create_settings_window.get_instance_count()}")
    print(f"当前文档窗口实例数量: {create_document_window.get_instance_count()}")
    
    # 移除特定实例
    create_document_window.remove_instance("报告.pdf")
    print(f"移除'报告.pdf'后文档窗口实例数量: {create_document_window.get_instance_count()}")
    
    # 清理所有实例
    create_settings_window.clear_instances()
    create_document_window.clear_instances()
    print(f"清理后设置窗口实例数量: {create_settings_window.get_instance_count()}")
    print(f"清理后文档窗口实例数量: {create_document_window.get_instance_count()}")
    print()
    
    # 5. 错误处理
    print("5. 错误处理演示:")
    
    @singleton_window
    def failing_window():
        print("尝试创建窗口...")
        raise ValueError("模拟创建失败")
    
    try:
        failing_window()
    except ValueError as e:
        print(f"捕获到预期异常: {e}")
    
    print("演示完成！")
    
    # 清理
    win5.close()
    doc2.close()
    doc3.close()
    doc4.close()


if __name__ == "__main__":
    demo_optimized_features()