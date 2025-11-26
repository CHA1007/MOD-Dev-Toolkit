#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将项目打包成 exe 文件
使用方法: python scripts/build_exe.py
或: cd scripts && python build_exe.py
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

# 获取项目根目录（脚本所在目录的父目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def get_version():
    """从 main.py 获取版本号"""
    try:
        # 读取 main.py 文件（从项目根目录）
        main_py_path = os.path.join(PROJECT_ROOT, 'main.py')
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找版本号
            for line in content.split('\n'):
                if '__version__' in line and '=' in line:
                    # 提取版本号
                    version = line.split('=')[1].strip().strip('"').strip("'")
                    return version
    except Exception as e:
        print(f"警告: 无法读取版本号: {e}")
    return "1.0.0"

def create_version_file(version, exe_name):
    """创建 PyInstaller 版本信息文件"""
    # 解析版本号（格式：主版本.次版本.修订版本）
    version_parts = version.split('.')
    major = int(version_parts[0]) if len(version_parts) > 0 and version_parts[0].isdigit() else 1
    minor = int(version_parts[1]) if len(version_parts) > 1 and version_parts[1].isdigit() else 0
    patch = int(version_parts[2]) if len(version_parts) > 2 and version_parts[2].isdigit() else 0
    build = int(version_parts[3]) if len(version_parts) > 3 and version_parts[3].isdigit() else 0
    
    # 生成带版本号的文件名
    exe_filename = f"{exe_name}.exe"
    
    # 创建版本信息文件内容
    version_file_content = f"""# UTF-8
#
# 版本信息文件，用于 PyInstaller 打包
#
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, {build}),
    prodvers=({major}, {minor}, {patch}, {build}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Modrinth MOD Dependency Generator'),
        StringStruct(u'FileDescription', u'Modrinth MOD 依赖生成器'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'Auto Depen'),
        StringStruct(u'LegalCopyright', u'Copyright (C) {datetime.now().year}'),
        StringStruct(u'OriginalFilename', u'{exe_filename}'),
        StringStruct(u'ProductName', u'Modrinth MOD Dependency Generator'),
        StringStruct(u'ProductVersion', u'{version}')]
      )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    # 写入版本文件（在项目根目录）
    version_file = os.path.join(PROJECT_ROOT, "version_info.txt")
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_file_content)
    
    print(f"✓ 已创建版本信息文件: {version_file} (版本: {version})")
    return version_file

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
            requirements_path = os.path.join(PROJECT_ROOT, "requirements.txt")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
            print("✓ 依赖安装完成")
        except Exception as e:
            print(f"✗ 依赖安装失败: {e}")
            print(f"请手动运行: pip install -r {requirements_path}")
            return False
    else:
        print("✓ 所有依赖已安装")
    return True

def build_exe():
    """构建 exe 文件"""
    print("=" * 60)
    print("开始打包程序...")
    print("=" * 60)
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"脚本目录: {SCRIPT_DIR}\n")
    
    # 切换到项目根目录
    os.chdir(PROJECT_ROOT)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        return False
    
    # 清理之前的构建文件
    build_dir = os.path.join(PROJECT_ROOT, "build")
    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    if os.path.exists(build_dir):
        print("清理旧的 build 目录...")
        shutil.rmtree(build_dir)
    if os.path.exists(dist_dir):
        print("清理旧的 dist 目录...")
        shutil.rmtree(dist_dir)
    
    # 获取版本号
    version = get_version()
    print(f"当前版本: {version}")
    
    # 生成带版本号的文件名
    exe_name = f"Auto Depen - {version}"
    
    # 清理 spec 文件（包括旧的和新的）
    spec_files_to_clean = ["main.spec", "gui.spec", "AutoDepen.spec"]
    # 添加当前版本的 spec 文件名
    spec_files_to_clean.append(f"{exe_name}.spec")
    for spec_file in spec_files_to_clean:
        spec_path = os.path.join(PROJECT_ROOT, spec_file)
        if os.path.exists(spec_path):
            print(f"清理旧的 {spec_file} 文件...")
            os.remove(spec_path)
    
    # 创建版本信息文件
    version_file = create_version_file(version, exe_name)
    
    # PyInstaller 命令参数
    gui_py_path = os.path.join(PROJECT_ROOT, "gui.py")
    requirements_path = os.path.join(PROJECT_ROOT, "requirements.txt")
    
    cmd = [
        "pyinstaller",
        f"--name={exe_name}",  # 生成的 exe 文件名（包含版本号）
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口（GUI 程序）
        f"--version-file={version_file}",  # 版本信息文件
        "--icon=NONE",  # 如果有图标文件可以指定路径
        f"--add-data={requirements_path};.",  # 包含 requirements.txt（Windows 使用分号）
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
        gui_py_path  # 直接使用 GUI 作为入口点
    ]
    
    # 如果是 Linux/Mac，使用冒号而不是分号
    if sys.platform != "win32":
        cmd[5] = f"--add-data={requirements_path}:."
    
    print("\n执行打包命令...")
    print(" ".join(cmd))
    print("\n")
    
    try:
        # 执行打包
        subprocess.check_call(cmd, cwd=PROJECT_ROOT)
        
        print("\n" + "=" * 60)
        print("✓ 打包完成！")
        print("=" * 60)
        exe_path = os.path.join(PROJECT_ROOT, 'dist', f'{exe_name}.exe')
        print(f"\n生成的 exe 文件位置: {os.path.abspath(exe_path)}")
        print(f"文件名: {exe_name}.exe")
        print(f"版本: {version}")
        print("\n提示:")
        print("  - 如果程序无法运行，可能需要安装 Visual C++ Redistributable")
        print("  - 首次运行可能会被杀毒软件拦截，需要添加信任")
        print("  - 如果遇到问题，可以尝试使用 --console 参数重新打包（显示控制台窗口）")
        print("  - 可以在 exe 文件属性中查看版本信息")
        
        # 清理版本信息文件（可选，保留也可以）
        if os.path.exists(version_file):
            os.remove(version_file)
        
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

