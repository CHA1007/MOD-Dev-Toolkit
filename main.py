#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modrinth MOD 依赖生成器
版本: 1.2.0
"""

__version__ = "1.2.0"
VERSION = __version__

# 导入模块（向后兼容）
# 注意：导入放在版本号定义之后，以保持向后兼容性
from api import ModrinthAPI  # noqa: E402
from generator import ForgeDepGenerator  # noqa: E402
from models import ModVersion, ModInfo  # noqa: E402

# 导出所有公共接口（向后兼容）
__all__ = [
    "ModrinthAPI",
    "ForgeDepGenerator",
    "ModVersion",
    "ModInfo",
    "__version__",
    "VERSION",
]


def main():
    """主函数 - 启动 GUI 模式"""
    import sys

    # 检查命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["--version", "-v"]:
            print(f"Modrinth MOD 依赖生成器 v{VERSION}")
            return
        elif arg in ["--help", "-h"]:
            print(f"Modrinth MOD 依赖生成器 v{VERSION}")
            print("\n用法:")
            print("  python main.py              # 启动 GUI 模式（默认）")
            print("  python gui.py               # 直接启动 GUI 模式")
            print("  python main.py --version    # 显示版本号")
            print("  python main.py -v           # 显示版本号（简写）")
            print("  python main.py --help       # 显示帮助信息")
            return
        else:
            print(f"未知参数: {arg}")
            print("使用 'python main.py --help' 查看帮助信息")
            return

    # 默认启动 GUI 模式
    try:
        from gui import main as gui_main

        gui_main()
    except ImportError as e:
        print(f"无法启动 GUI 模式: {e}")
        print("请确保已安装以下依赖:")
        print("  - customtkinter")
        print("  - PIL (Pillow)")
        print("  - requests")
        print("\n安装命令: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
