#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绘影 AI 控制面板 - EXE 打包脚本
使用 PyInstaller 将 Python 程序打包为独立的 .exe 文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller 已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("📦 正在安装 PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller 安装失败")
        return False

def create_spec_file():
    """创建 PyInstaller 规格文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['panel.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('enhanced_powershell_terminal.py', '.'),
        ('main.py', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='绘影AI控制面板',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('control_panel.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 规格文件已创建: control_panel.spec")

def build_exe():
    """构建 EXE 文件"""
    print("🔨 开始构建 EXE 文件...")
    
    try:
        # 使用规格文件构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "control_panel.spec"]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ EXE 文件构建成功")
            return True
        else:
            print("❌ EXE 文件构建失败")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

def create_distribution():
    """创建分发包"""
    print("📦 创建分发包...")
    
    dist_dir = "绘影AI控制面板_分发包"
    
    # 清理旧的分发目录
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir)
    
    # 复制 EXE 文件
    exe_source = os.path.join("dist", "绘影AI控制面板.exe")
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, dist_dir)
        print(f"✅ 已复制: 绘影AI控制面板.exe")
    else:
        print("❌ 找不到生成的 EXE 文件")
        return False
    
    # 复制必要文件
    files_to_copy = [
        "main.py",
        "enhanced_powershell_terminal.py",
        "README_FINAL.md"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir)
            print(f"✅ 已复制: {file}")
    
    # 创建启动脚本
    create_startup_scripts(dist_dir)
    
    # 创建说明文件
    create_readme(dist_dir)
    
    print(f"✅ 分发包已创建: {dist_dir}")
    return True

def create_startup_scripts(dist_dir):
    """创建启动脚本"""
    # Windows 批处理文件
    bat_content = '''@echo off
title 绘影 AI 控制面板
echo 🎨 绘影 AI 控制面板 - 现代版 v2.0
echo =====================================
echo 正在启动...
echo.

"绘影AI控制面板.exe"

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错
    pause
)
'''
    
    with open(bat_file_path, 'w', encoding='utf-8') as f:  # 显式指定编码
        f.write(bat_content)
    
    print("✅ 已创建: 启动控制面板.bat")

def create_readme(dist_dir):
    """创建说明文件"""
    readme_content = '''# 绘影 AI 控制面板 - 使用说明

## 🚀 快速开始

1. **直接运行**: 双击 `绘影AI控制面板.exe` 启动程序
2. **批处理启动**: 双击 `启动控制面板.bat` 启动（推荐）

## 📁 文件说明

- `绘影AI控制面板.exe` - 主程序（独立可执行文件）
- `main.py` - 您的 AI 服务主程序
- `enhanced_powershell_terminal.py` - 增强版终端模块
- `启动控制面板.bat` - Windows 启动脚本

## ⚠️ 重要提示

1. **确保 main.py 存在**: 控制面板需要调用同目录下的 `main.py` 文件
2. **Python 环境**: 虽然控制面板已打包为 EXE，但 `main.py` 仍需要 Python 环境
3. **文件位置**: 请保持所有文件在同一目录下

## 🎯 主要功能

- ▶️ 启动/停止/重启 AI 服务
- 💻 PowerShell 风格日志终端
- 🌐 一键打开 Web 界面
- 🖼️ 查看输出图片
- 🧹 清除历史图像
- 📝 导出日志文件

## ⌨️ 快捷键

- F1 - 启动服务
- F2 - 停止服务  
- F5 - 重启服务
- Ctrl+L - 清除日志
- Ctrl+S - 导出日志
- Ctrl+Q - 退出程序

## 🔧 故障排除

如果遇到问题，请检查：
1. `main.py` 文件是否存在
2. Python 环境是否正确安装
3. 是否有足够的系统权限

---
绘影 AI 控制面板 v2.0 - 现代化桌面控制体验
'''
    
    with open(os.path.join(dist_dir, "使用说明.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ 已创建: 使用说明.txt")

def cleanup():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    
    cleanup_dirs = ["build", "__pycache__"]
    cleanup_files = ["control_panel.spec"]
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 已删除: {dir_name}")
    
    for file_name in cleanup_files:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"✅ 已删除: {file_name}")

def main():
    """主函数"""
    print("🎨 绘影 AI 控制面板 - EXE 打包工具")
    print("=" * 50)
    
    # 检查必要文件
    required_files = ["panel.py", "enhanced_powershell_terminal.py"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查并安装 PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False
    
    # 创建规格文件
    create_spec_file()
    
    # 构建 EXE
    if not build_exe():
        return False
    
    # 创建分发包
    if not create_distribution():
        return False
    
    # 清理临时文件
    cleanup()
    
    print("\n" + "=" * 50)
    print("🎉 EXE 打包完成！")
    print("📦 分发包位置: 绘影AI控制面板_分发包")
    print("🚀 可以将整个分发包文件夹复制到目标机器上使用")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ 打包失败")
            input("按回车键退出...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 打包被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 打包过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)

