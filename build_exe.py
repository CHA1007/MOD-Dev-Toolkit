#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将项目打包成 exe 文件
使用方法: python build_exe.py
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller  # noqa: F401
        print("✓ PyInstaller 已安装")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")
        return True

def check_dependencies():
    """检查依赖是否已安装"""
    dependencies = ['customtkinter', 'PIL', 'requests']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print("✗ 检测到缺失的依赖:")
        for dep in missing:
            print(f"  - {dep}")
        print("\n正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ 依赖安装完成")
        except Exception as e:
            print(f"✗ 依赖安装失败: {e}")
            print("请手动运行: pip install -r requirements.txt")
            return False
    else:
        print("✓ 所有依赖已安装")
    return True

def build_exe():
    """构建 exe 文件"""
    print("=" * 60)
    print("开始打包程序...")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        return False
    
    # 清理之前的构建文件
    if os.path.exists("build"):
        print("清理旧的 build 目录...")
        shutil.rmtree("build")
    if os.path.exists("dist"):
        print("清理旧的 dist 目录...")
        shutil.rmtree("dist")
    # 清理 spec 文件
    for spec_file in ["main.spec", "gui.spec", "AutoDepen.spec"]:
        if os.path.exists(spec_file):
            print(f"清理旧的 {spec_file} 文件...")
            os.remove(spec_file)
    
    # PyInstaller 命令参数
    cmd = [
        "pyinstaller",
        "--name=AutoDepen",  # 生成的 exe 文件名
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口（GUI 程序）
        "--icon=NONE",  # 如果有图标文件可以指定路径
        "--add-data=requirements.txt;.",  # 包含 requirements.txt（Windows 使用分号）
        # 隐藏导入 - customtkinter 相关
        "--hidden-import=customtkinter",
        "--hidden-import=customtkinter.windows",
        "--hidden-import=customtkinter.windows.widgets",
        "--hidden-import=customtkinter.windows.widgets.core_widget_classes",
        "--hidden-import=customtkinter.windows.ctk_toplevel",
        "--hidden-import=customtkinter.windows.ctk_tk",
        "--hidden-import=customtkinter.windows.widgets.ctk_button",
        "--hidden-import=customtkinter.windows.widgets.ctk_entry",
        "--hidden-import=customtkinter.windows.widgets.ctk_label",
        "--hidden-import=customtkinter.windows.widgets.ctk_textbox",
        "--hidden-import=customtkinter.windows.widgets.ctk_frame",
        "--hidden-import=customtkinter.windows.widgets.ctk_scrollbar",
        # 隐藏导入 - PIL 相关
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        # 隐藏导入 - 其他
        "--hidden-import=requests",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        # 收集所有资源
        "--collect-all=customtkinter",  # 收集 customtkinter 的所有资源
        "--collect-all=PIL",  # 收集 PIL 的所有资源
        "--collect-submodules=customtkinter",  # 收集 customtkinter 的所有子模块
        "--noconfirm",  # 不询问确认，直接覆盖
        "gui.py"  # 直接使用 GUI 作为入口点
    ]
    
    # 如果是 Linux/Mac，使用冒号而不是分号
    if sys.platform != "win32":
        cmd[5] = "--add-data=requirements.txt:."
    
    print("\n执行打包命令...")
    print(" ".join(cmd))
    print("\n")
    
    try:
        # 执行打包
        subprocess.check_call(cmd)
        
        print("\n" + "=" * 60)
        print("✓ 打包完成！")
        print("=" * 60)
        print(f"\n生成的 exe 文件位置: {os.path.abspath('dist/AutoDepen.exe')}")
        print("\n提示:")
        print("  - 如果程序无法运行，可能需要安装 Visual C++ Redistributable")
        print("  - 首次运行可能会被杀毒软件拦截，需要添加信任")
        print("  - 如果遇到问题，可以尝试使用 --console 参数重新打包（显示控制台窗口）")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 打包失败: {e}")
        return False
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)

