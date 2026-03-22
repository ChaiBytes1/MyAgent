"""
屏幕操作模块
实现提示词中定义的所有鼠标、键盘事件，支持窗口激活。
可独立执行示例，也可作为模块被其他程序调用。
"""

import pyautogui
import win32gui
import win32api
import win32con
import win32process
import ctypes
import time
import json
from typing import List, Dict, Any, Optional, Tuple

# ==================== 全局配置 ====================
pyautogui.FAILSAFE = True          # 鼠标移到左上角可紧急停止
pyautogui.PAUSE = 0.1              # 每个操作后暂停0.1秒

# ==================== 窗口激活函数 ====================
def get_window_thread(hwnd: int) -> int:
    """获取窗口所属线程ID"""
    return win32process.GetWindowThreadProcessId(hwnd)[0]

def activate_window_by_title(title: str, timeout: float = 3.0) -> Optional[int]:
    """
    根据窗口标题激活窗口（支持部分匹配）
    :param title: 窗口标题关键字（如"记事本"）
    :param timeout: 最长等待时间（秒）
    :return: 窗口句柄，如果找不到返回None
    """
    start_time = time.time()
    hwnd = None

    def enum_callback(h, _):
        nonlocal hwnd
        if win32gui.IsWindowVisible(h):
            window_title = win32gui.GetWindowText(h)
            if title in window_title:
                hwnd = h
                return False
        return True

    while hwnd is None and time.time() - start_time < timeout:
        win32gui.EnumWindows(enum_callback, None)
        if hwnd is None:
            time.sleep(0.2)

    if hwnd is None:
        print(f"未找到标题包含 '{title}' 的窗口")
        return None

    # 如果窗口最小化，先恢复
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.1)

    # 附加输入线程
    current_thread = win32api.GetCurrentThreadId()
    target_thread = get_window_thread(hwnd)
    if current_thread != target_thread:
        ctypes.windll.user32.AttachThreadInput(current_thread, target_thread, True)

    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.1)
    win32gui.SetFocus(hwnd)

    # 解除线程附加
    if current_thread != target_thread:
        ctypes.windll.user32.AttachThreadInput(current_thread, target_thread, False)

    print(f"已激活窗口: {win32gui.GetWindowText(hwnd)}")
    return hwnd

# ==================== 鼠标操作 ====================
def mouse_click(x: int, y: int, button: str = 'left', clicks: int = 1):
    """
    单击或双击鼠标
    :param x, y: 屏幕坐标
    :param button: 'left', 'right', 'middle'
    :param clicks: 1=单击，2=双击
    """
    pyautogui.click(x, y, button=button, clicks=clicks)

def mouse_double_click(x: int, y: int, button: str = 'left'):
    """双击鼠标（调用mouse_click）"""
    mouse_click(x, y, button=button, clicks=2)

def mouse_long_press(x: int, y: int, length_ms: int, button: str = 'left'):
    """长按鼠标"""
    pyautogui.moveTo(x, y)
    pyautogui.mouseDown(button=button)
    time.sleep(length_ms / 1000.0)
    pyautogui.mouseUp(button=button)

def mouse_drag(start_pos: Tuple[int, int], end_pos: Tuple[int, int],
               length_ms: int = 500, shake: float = 0.0, button: str = 'left'):
    """
    拖动鼠标
    :param start_pos: (x1, y1)
    :param end_pos: (x2, y2)
    :param length_ms: 拖动总时长（毫秒）
    :param shake: 抖动幅度 0~1，0表示直线，1表示最大随机抖动
    :param button: 鼠标按键
    """
    x1, y1 = start_pos
    x2, y2 = end_pos
    pyautogui.moveTo(x1, y1)
    pyautogui.mouseDown(button=button)

    steps = max(10, int(length_ms / 10))
    for i in range(1, steps + 1):
        t = i / steps
        cur_x = int(x1 + (x2 - x1) * t)
        cur_y = int(y1 + (y2 - y1) * t)
        if shake > 0:
            # 基于时间的简单抖动
            import random
            cur_x += int(random.uniform(-shake * 10, shake * 10))
            cur_y += int(random.uniform(-shake * 10, shake * 10))
        pyautogui.moveTo(cur_x, cur_y)
        time.sleep(length_ms / 1000.0 / steps)

    pyautogui.mouseUp(button=button)

def mouse_move(x: int, y: int, duration: float = 0):
    """移动鼠标到指定坐标"""
    pyautogui.moveTo(x, y, duration=duration)

def mouse_scroll(amount: int, x: Optional[int] = None, y: Optional[int] = None):
    """
    滚动滚轮
    :param amount: 正数向上，负数向下，通常120为一个刻度
    :param x, y: 可选，先移动鼠标到该位置再滚动
    """
    if x is not None and y is not None:
        pyautogui.moveTo(x, y)
    pyautogui.scroll(amount)

# ==================== 键盘操作 ====================
def key_press(key: str, modifiers: List[str] = None):
    """
    按下并松开一个按键（支持组合键）
    :param key: 按键名，如 'a', 'enter', 'space'
    :param modifiers: 修饰键列表，如 ['ctrl', 'shift']
    """
    if modifiers:
        # 按下所有修饰键
        for mod in modifiers:
            pyautogui.keyDown(mod)
        # 按主键
        pyautogui.press(key)
        # 释放所有修饰键（逆序）
        for mod in reversed(modifiers):
            pyautogui.keyUp(mod)
    else:
        pyautogui.press(key)

def key_down(key: str, modifiers: List[str] = None):
    """
    按下并保持一个按键（支持组合键）
    :param key: 按键名
    :param modifiers: 修饰键列表
    """
    if modifiers:
        for mod in modifiers:
            pyautogui.keyDown(mod)
    pyautogui.keyDown(key)

def key_up(key: str, modifiers: List[str] = None):
    """
    释放一个按键（支持组合键）
    :param key: 按键名
    :param modifiers: 修饰键列表
    """
    pyautogui.keyUp(key)
    if modifiers:
        for mod in reversed(modifiers):
            pyautogui.keyUp(mod)

# ==================== 执行命令列表 ====================
def execute_commands(commands: List[Dict[str, Any]],
                     target_window_title: Optional[str] = None,
                     activate_timeout: float = 3.0):
    """
    执行命令序列
    :param commands: 命令列表，每个元素格式为 {"action": ..., "args": ...}
    :param target_window_title: 目标窗口标题（可选），如果提供则每次操作前激活该窗口
    :param activate_timeout: 激活窗口的超时时间
    """
    if target_window_title:
        hwnd = activate_window_by_title(target_window_title, timeout=activate_timeout)
        if hwnd is None:
            print(f"警告：无法激活窗口 '{target_window_title}'，操作可能发送到错误窗口")

    for cmd in commands:
        action = cmd.get("action")
        args = cmd.get("args", {})
        if action == "click":
            mouse_click(args["pos"][0], args["pos"][1],
                        button=args.get("button", "left"),
                        clicks=args.get("clicks", 1))
        elif action == "long_press":
            mouse_long_press(args["pos"][0], args["pos"][1],
                             args["length"], button=args.get("button", "left"))
        elif action == "drag":
            mouse_drag(tuple(args["start_pos"]), tuple(args["end_pos"]),
                       args.get("length", 500), args.get("shake", 0.0),
                       button=args.get("button", "left"))
        elif action == "move":
            mouse_move(args["end_pos"][0], args["end_pos"][1],
                       duration=args.get("duration", 0))
        elif action == "scroll":
            mouse_scroll(args["amount"], args.get("x"), args.get("y"))
        elif action == "key_press":
            key_press(args["key"], args.get("modifiers", []))
        elif action == "key_down":
            key_down(args["key"], args.get("modifiers", []))
        elif action == "key_up":
            key_up(args["key"], args.get("modifiers", []))
        elif action == "output":
            print(f"[OUTPUT] {args.get('txt', '')}")
        elif action == "endtask":
            print("任务结束")
            break
        else:
            print(f"未知操作: {action}")
        time.sleep(0.01)  # 避免操作过快

# ==================== 示例：根据JSON命令执行 ====================
def demo_from_json():
    """从JSON字符串读取命令并执行（示例）"""
    # 假设这是从AI返回的JSON
    json_str = '''
    {
        "target_window": "记事本",
        "command": [
            {"action": "move", "args": {"end_pos": [500, 300]}},
            {"action": "click", "args": {"pos": [500, 300], "button": "left"}},
            {"action": "key_press", "args": {"key": "hello world", "modifiers": []}},
            {"action": "key_press", "args": {"key": "enter"}},
            {"action": "scroll", "args": {"amount": 120, "x": 500, "y": 300}},
            {"action": "output", "args": {"txt": "操作完成"}},
            {"action": "endtask", "args": {}}
        ]
    }
    '''
    data = json.loads(json_str)
    target = data.get("target_window")
    commands = data.get("command", [])
    execute_commands(commands, target_window_title=target)

# ==================== 简单手动测试 ====================
def manual_test():
    """手动测试鼠标键盘操作（不依赖JSON）"""
    # 激活记事本
    hwnd = activate_window_by_title("记事本")
    if hwnd is None:
        print("请先打开记事本")
        return

    # 移动鼠标到屏幕中心并单击
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    mouse_move(center_x, center_y, duration=0.5)
    mouse_click(center_x, center_y)

    # 输入文本
    key_press("hello", modifiers=[])
    key_press("enter")

    # 滚动滚轮
    mouse_scroll(120, center_x, center_y)
    time.sleep(1)

    # 拖动鼠标（画一个矩形）
    start = (center_x - 100, center_y - 100)
    end = (center_x + 100, center_y + 100)
    mouse_drag(start, end, length_ms=1000, shake=0.2)
    print("测试完成")

if __name__ == "__main__":
    # 选择运行模式：
    # 1. 从JSON执行（假设AI返回的命令）
     demo_from_json()
    # 2. 手动测试
    #manual_test()
    
