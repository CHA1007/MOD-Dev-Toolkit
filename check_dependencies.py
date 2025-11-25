#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查依赖是否已安装
"""

import sys

def check_dependencies():
    """检查所有必需的依赖"""
    dependencies = {
        'customtkinter': 'customtkinter',
        'PIL': 'Pillow',
        'requests': 'requests',
    }
    
    missing = []
    installed = []
    
    for module_name, package_name in dependencies.items():
        try:
            __import__(module_name)
            installed.append(f"✓ {package_name}")
        except ImportError:
            missing.append(f"✗ {package_name}")
    
    print("=" * 60)
    print("依赖检查结果")
    print("=" * 60)
    
    if installed:
        print("\n已安装的依赖:")
        for item in installed:
            print(f"  {item}")
    
    if missing:
        print("\n缺失的依赖:")
        for item in missing:
            print(f"  {item}")
        print("\n请运行以下命令安装缺失的依赖:")
        print(f"  pip install -r requirements.txt")
        return False
    else:
        print("\n✓ 所有依赖已安装！")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)

