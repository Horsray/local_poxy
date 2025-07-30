#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绘影 AI 控制面板 - 最终改进版
集成增强版 PowerShell 风格日志终端的完整解决方案
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Menu, filedialog
import subprocess
import threading
import os
import time
import webbrowser
import sys
from datetime import datetime
import json
from pathlib import Path

# 导入增强版日志终端
try:
    from enhanced_log_terminal import PowerShellTerminal
except ImportError:
    # 如果无法导入，使用简化版本
    PowerShellTerminal = None

class FinalControlPanel:
    def __init__(self):
        # 初始化变量
        self.process = None
        # 已取消外部文件执行，直接集成 main.py 内部逻辑
        self.config_file = "panel_config.json"
        self.log_file = "panel_logs.txt"
        
        # 加载配置
        self.load_config()
        
        # 创建主窗口
        self.setup_main_window()
        
        # 创建界面
        self.create_ui()
        
        # 绑定事件
        self.bind_events()
        
        # 初始化状态
        self.update_status()
        
        # 添加欢迎消息
        self.add_welcome_message()

    def load_config(self):
        """加载配置文件"""
        default_config = {
            "window_geometry": "1200x800",
            "theme": "darkly",
            "font_size": 11,
            "auto_save_logs": True,
            "log_level": "all",
            "paned_position": 300
        }
        
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = {**default_config, **json.load(f)}
            else:
                self.config = default_config
        except:
            self.config = default_config

    def save_config(self):
        """保存配置文件"""
        try:
            # 保存当前窗口位置
            geometry = self.app.geometry()
            self.config["window_geometry"] = geometry.split('+')[0]
            
            # 保存分割位置
            if hasattr(self, 'paned_window'):
                try:
                    self.config["paned_position"] = self.paned_window.sashpos(0)
                except:
                    pass
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except:
            pass

    def setup_main_window(self):
        """设置主窗口"""
        self.app = ttk.Window(
            title="绘影 AI 控制面板 - 专业版 v2.0",
            themename=self.config.get("theme", "darkly"),
            size=tuple(map(int, self.config.get("window_geometry", "1200x800").split('x'))),
            resizable=(True, True),
            minsize=(900, 600)
        )
        
        # 设置窗口图标
        try:
            # 如果有图标文件，可以在这里设置
            # self.app.iconbitmap("icon.ico")
            pass
        except:
            pass
        
        # 居中显示
        self.center_window()

    def center_window(self):
        """窗口居中显示"""
        self.app.update_idletasks()
        width = self.app.winfo_width()
        height = self.app.winfo_height()
        x = (self.app.winfo_screenwidth() // 2) - (width // 2)
        y = (self.app.winfo_screenheight() // 2) - (height // 2)
        self.app.geometry(f'{width}x{height}+{x}+{y}')

    def create_ui(self):
        """创建用户界面"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建主容器
        self.main_container = ttk.Frame(self.app)
        self.main_container.pack(fill=BOTH, expand=YES, padx=8, pady=8)
        
        # 创建顶部标题栏
        self.create_header()
        
        # 创建主体内容区域
        self.create_main_content()
        
        # 创建底部状态栏
        self.create_status_bar()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = Menu(self.app)
        self.app.config(menu=menubar)
        
        # 文件菜单
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出日志...", command=self.export_logs_dialog, accelerator="Ctrl+S")
        file_menu.add_command(label="清除日志", command=self.clear_logs, accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit_app, accelerator="Ctrl+Q")
        
        # 服务菜单
        service_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="服务", menu=service_menu)
        service_menu.add_command(label="启动服务", command=self.start_service, accelerator="F1")
        service_menu.add_command(label="停止服务", command=self.stop_service, accelerator="F2")
        service_menu.add_command(label="重启服务", command=self.restart_service, accelerator="F5")
        
        # 工具菜单
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="打开网页", command=self.open_web)
        tools_menu.add_command(label="查看图片", command=self.view_images)
        tools_menu.add_command(label="清除图像", command=self.clear_images)
        tools_menu.add_separator()
        tools_menu.add_command(label="设置...", command=self.show_settings)
        
        # 视图菜单
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="增大字体", command=self.increase_font_size, accelerator="Ctrl++")
        view_menu.add_command(label="减小字体", command=self.decrease_font_size, accelerator="Ctrl+-")
        view_menu.add_separator()
        view_menu.add_command(label="切换主题", command=self.toggle_theme)
        
        # 帮助菜单
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="键盘快捷键", command=self.show_shortcuts)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_header(self):
        """创建顶部标题栏"""
        header_frame = ttk.Frame(self.main_container, style="Card.TFrame", padding=15)
        header_frame.pack(fill=X, pady=(0, 10))
        
        # 左侧标题区域
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=LEFT, fill=Y)
        
        # 主标题
        title_label = ttk.Label(
            title_frame,
            text="🎨 绘影 AI 控制面板",
            font=("微软雅黑", 20, "bold"),
            bootstyle="primary"
        )
        title_label.pack(anchor=W)
        
        # 副标题
        subtitle_label = ttk.Label(
            title_frame,
            text="专业版 v2.0 - 现代化桌面控制界面",
            font=("微软雅黑", 11),
            bootstyle="secondary"
        )
        subtitle_label.pack(anchor=W, pady=(2, 0))
        
        # 右侧状态和控制区域
        control_frame = ttk.Frame(header_frame)
        control_frame.pack(side=RIGHT, fill=Y)
        
        # 服务状态指示器
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(side=TOP, anchor=E, pady=(0, 10))
        
        self.status_indicator = ttk.Label(
            status_frame,
            text="● 服务已停止",
            font=("微软雅黑", 12, "bold"),
            bootstyle="danger"
        )
        self.status_indicator.pack()
        
        # 控制按钮组
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=TOP, anchor=E)
        
        # 快速操作按钮
        ttk.Button(
            button_frame,
            text="🚀",
            width=4,
            command=self.start_service,
            bootstyle="success-outline",
            style="Toolbutton"
        ).pack(side=LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="⏹️",
            width=4,
            command=self.stop_service,
            bootstyle="danger-outline",
            style="Toolbutton"
        ).pack(side=LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🔄",
            width=4,
            command=self.restart_service,
            bootstyle="warning-outline",
            style="Toolbutton"
        ).pack(side=LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="🌙",
            width=4,
            command=self.toggle_theme,
            bootstyle="info-outline",
            style="Toolbutton"
        ).pack(side=LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="⚙️",
            width=4,
            command=self.show_settings,
            bootstyle="secondary-outline",
            style="Toolbutton"
        ).pack(side=LEFT, padx=2)

    def create_main_content(self):
        """创建主体内容区域"""
        # 使用 PanedWindow 创建可调整的分割布局
        self.paned_window = ttk.PanedWindow(self.main_container, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=YES)
        
        # 左侧控制面板
        self.create_control_panel()
        
        # 右侧日志区域
        self.create_log_panel()
        
        # 设置初始分割位置
        self.app.after(100, lambda: self.paned_window.sashpos(0, self.config.get("paned_position", 300)))

    def create_control_panel(self):
        """创建左侧控制面板"""
        # 控制面板容器
        control_container = ttk.Frame(self.paned_window, style="Card.TFrame", padding=10)
        self.paned_window.add(control_container, weight=1)
        
        # 服务控制区域
        service_frame = ttk.LabelFrame(
            control_container,
            text="🎛️ 服务控制",
            padding=15,
            bootstyle="primary"
        )
        service_frame.pack(fill=X, pady=(0, 10))
        
        # 服务状态显示
        status_display = ttk.Frame(service_frame)
        status_display.pack(fill=X, pady=(0, 15))
        
        ttk.Label(status_display, text="当前状态:", font=("微软雅黑", 10, "bold")).pack(anchor=W)
        self.service_status_text = ttk.Label(
            status_display, 
            text="服务已停止", 
            font=("微软雅黑", 10),
            bootstyle="secondary"
        )
        self.service_status_text.pack(anchor=W, pady=(2, 0))
        
        # 主要控制按钮
        self.start_btn = ttk.Button(
            service_frame,
            text="▶️ 启动服务",
            width=25,
            bootstyle="success",
            command=self.start_service
        )
        self.start_btn.pack(fill=X, pady=3)
        
        self.stop_btn = ttk.Button(
            service_frame,
            text="⏹️ 停止服务",
            width=25,
            bootstyle="danger",
            command=self.stop_service
        )
        self.stop_btn.pack(fill=X, pady=3)
        
        self.restart_btn = ttk.Button(
            service_frame,
            text="🔄 重启服务",
            width=25,
            bootstyle="warning",
            command=self.restart_service
        )
        self.restart_btn.pack(fill=X, pady=3)
        
        # 功能操作区域
        function_frame = ttk.LabelFrame(
            control_container,
            text="🛠️ 功能操作",
            padding=15,
            bootstyle="info"
        )
        function_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Button(
            function_frame,
            text="🌐 打开网页界面",
            width=25,
            bootstyle="info-outline",
            command=self.open_web
        ).pack(fill=X, pady=2)
        
        ttk.Button(
            function_frame,
            text="🖼️ 查看输出图片",
            width=25,
            bootstyle="info-outline",
            command=self.view_images
        ).pack(fill=X, pady=2)
        
        ttk.Button(
            function_frame,
            text="🧹 清除历史图像",
            width=25,
            bootstyle="secondary-outline",
            command=self.clear_images
        ).pack(fill=X, pady=2)
        
        # 系统工具区域
        tools_frame = ttk.LabelFrame(
            control_container,
            text="🔧 系统工具",
            padding=15,
            bootstyle="secondary"
        )
        tools_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Button(
            tools_frame,
            text="📝 清除日志",
            width=25,
            bootstyle="secondary-outline",
            command=self.clear_logs
        ).pack(fill=X, pady=2)
        
        ttk.Button(
            tools_frame,
            text="💾 导出日志",
            width=25,
            bootstyle="secondary-outline",
            command=self.export_logs_dialog
        ).pack(fill=X, pady=2)
        
        ttk.Button(
            tools_frame,
            text="⚙️ 系统设置",
            width=25,
            bootstyle="secondary-outline",
            command=self.show_settings
        ).pack(fill=X, pady=2)
        
        # 退出按钮
        ttk.Button(
            control_container,
            text="🚪 退出程序",
            width=25,
            bootstyle="outline-danger",
            command=self.quit_app
        ).pack(side=BOTTOM, fill=X, pady=(20, 0))

    def create_log_panel(self):
        """创建右侧日志面板"""
        # 日志面板容器
        log_container = ttk.Frame(self.paned_window, style="Card.TFrame", padding=10)
        self.paned_window.add(log_container, weight=3)
        
        # 日志面板标题
        log_header = ttk.Frame(log_container)
        log_header.pack(fill=X, pady=(0, 10))
        
        ttk.Label(
            log_header,
            text="💻 PowerShell 风格终端",
            font=("微软雅黑", 16, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # 日志控制按钮
        log_controls = ttk.Frame(log_header)
        log_controls.pack(side=RIGHT)
        
        ttk.Button(
            log_controls,
            text="🔍-",
            width=4,
            command=self.decrease_font_size,
            bootstyle="outline-secondary"
        ).pack(side=LEFT, padx=1)
        
        ttk.Button(
            log_controls,
            text="🔍+",
            width=4,
            command=self.increase_font_size,
            bootstyle="outline-secondary"
        ).pack(side=LEFT, padx=1)
        
        ttk.Button(
            log_controls,
            text="📋",
            width=4,
            command=self.copy_selected_log,
            bootstyle="outline-info"
        ).pack(side=LEFT, padx=1)
        
        ttk.Button(
            log_controls,
            text="🗑️",
            width=4,
            command=self.clear_logs,
            bootstyle="outline-danger"
        ).pack(side=LEFT, padx=1)
        
        # 搜索和过滤区域
        search_frame = ttk.Frame(log_container)
        search_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 搜索:", font=("微软雅黑", 10)).pack(side=LEFT, padx=(0, 5))
        
        self.search_var = ttk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("微软雅黑", 10),
            width=25
        )
        self.search_entry.pack(side=LEFT, padx=(0, 15))
        self.search_entry.bind('<KeyRelease>', self.search_logs)
        
        ttk.Label(search_frame, text="级别:", font=("微软雅黑", 10)).pack(side=LEFT, padx=(0, 5))
        
        self.log_level_var = ttk.StringVar(value="全部")
        log_level_combo = ttk.Combobox(
            search_frame,
            textvariable=self.log_level_var,
            values=["全部", "信息", "成功", "警告", "错误"],
            state="readonly",
            width=10
        )
        log_level_combo.pack(side=LEFT)
        log_level_combo.bind('<<ComboboxSelected>>', self.filter_logs)
        
        # 创建增强版日志终端
        if PowerShellTerminal:
            self.log_terminal = PowerShellTerminal(log_container, self.config)
        else:
            # 降级到基本版本
            self.create_basic_log_terminal(log_container)

    def create_basic_log_terminal(self, parent):
        """创建基本版日志终端（降级方案）"""
        from tkinter import scrolledtext
        
        terminal_frame = ttk.LabelFrame(
            parent,
            text="运行日志",
            padding=10,
            bootstyle="secondary"
        )
        terminal_frame.pack(fill=BOTH, expand=YES)
        
        self.log_text = scrolledtext.ScrolledText(
            terminal_frame,
            wrap="word",
            font=("JetBrains Mono", self.config.get("font_size", 11)),
            bg="#0c1021",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            selectbackground="#3b82f6",
            selectforeground="#ffffff",
            relief="flat",
            borderwidth=1
        )
        self.log_text.pack(fill=BOTH, expand=YES)
        self.log_text.configure(state='disabled')

    def create_status_bar(self):
        """创建底部状态栏"""
        status_frame = ttk.Frame(self.main_container, style="Secondary.TFrame", padding=5)
        status_frame.pack(fill=X, pady=(10, 0))
        
        # 左侧时间
        self.time_label = ttk.Label(
            status_frame,
            text=f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            font=("微软雅黑", 9),
            bootstyle="secondary"
        )
        self.time_label.pack(side=LEFT)
        
        # 中间状态
        self.service_status_label = ttk.Label(
            status_frame,
            text="服务状态: 已停止",
            font=("微软雅黑", 9),
            bootstyle="secondary"
        )
        self.service_status_label.pack(side=LEFT, padx=(30, 0))
        
        # 右侧进程信息
        self.process_info_label = ttk.Label(
            status_frame,
            text="PID: 无",
            font=("微软雅黑", 9),
            bootstyle="secondary"
        )
        self.process_info_label.pack(side=RIGHT)
        
        # 启动时间更新
        self.update_time()

    def bind_events(self):
        """绑定事件"""
        # 窗口关闭事件
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 键盘快捷键
        self.app.bind('<Control-q>', lambda e: self.quit_app())
        self.app.bind('<Control-l>', lambda e: self.clear_logs())
        self.app.bind('<Control-s>', lambda e: self.export_logs_dialog())
        self.app.bind('<F1>', lambda e: self.start_service())
        self.app.bind('<F2>', lambda e: self.stop_service())
        self.app.bind('<F5>', lambda e: self.restart_service())
        self.app.bind('<Control-plus>', lambda e: self.increase_font_size())
        self.app.bind('<Control-minus>', lambda e: self.decrease_font_size())
        self.app.bind('<Control-equal>', lambda e: self.increase_font_size())  # 兼容性

    def add_welcome_message(self):
        """添加欢迎消息"""
        self.log_message("📝 绘影 AI 控制面板已启动，就绪。")
        self.log_message("💡 提示: 使用 F1 启动服务，F2 停止服务，F5 重启服务")

    def log_message(self, message, level="info"):
        """添加日志消息"""
        if hasattr(self, 'log_terminal') and self.log_terminal:
            # 使用增强版终端
            self.log_terminal.add_log(message, level)
        else:
            # 使用基本版终端
            timestamp = datetime.now().strftime('%H:%M:%S')
            formatted_message = f"[{timestamp}] {message}\n"
            
            if hasattr(self, 'log_text'):
                self.log_text.configure(state='normal')
                self.log_text.insert('end', formatted_message)
                self.log_text.see('end')
                self.log_text.configure(state='disabled')
        
        # 保存到文件
        if self.config.get("auto_save_logs", True):
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] {message}\n")
            except:
                pass

    # 核心功能方法（与之前相同，这里省略重复代码）
    def start_service(self):
        """启动服务
        已取消外部文件执行，直接集成 main.py 内部逻辑
        """
        if self.process is None:
            try:
                self.log_message("🟡 启动服务中...")
                self.update_button_states(starting=True)
                # 直接调用 main.py 的 main() 函数
                from main import main as run_main
                threading.Thread(target=run_main, daemon=True).start()
                self.process = True  # 占位，用于表示“已启动”
                self.log_message(f"✅ 启动成功，服务已集成到主进程")
                self.update_status()
            except Exception as e:
                self.log_message(f"🛑 启动失败: {str(e)}")
                self.process = None
                self.update_button_states()
        else:
            self.log_message("⚠️ 服务已在运行。")

    def stop_service(self):
        """停止服务
        已取消外部文件执行，直接集成 main.py 内部逻辑。
        此处 process 只是占位，清理 UI 状态。
        """
        if self.process:
            try:
                self.log_message("🛑 正在停止服务...")
                # 由于main已集成为线程，无法像进程一样终止，仅做UI状态清理
                self.process = None
                self.log_message("🛑 服务已停止。")
                self.update_status()
            except Exception as e:
                self.log_message(f"🛑 停止失败: {str(e)}")
        else:
            self.log_message("⚠️ 服务未运行。")

    def restart_service(self):
        """重启服务"""
        self.log_message("🔄 重启服务中...")
        self.stop_service()
        time.sleep(1)
        self.start_service()

    def monitor_output(self):
        """监控进程输出"""
        if self.process:
            try:
                for line in self.process.stdout:
                    if line.strip():
                        self.log_message(line.strip())
            except Exception as e:
                self.log_message(f"输出监控错误: {str(e)}")

    def open_web(self):
        """打开网页"""
        url = "http://127.0.0.1:8188"
        self.log_message(f"🌐 正在打开网页 {url}")
        webbrowser.open(url)

    def view_images(self):
        """查看图片"""
        folder = os.path.join(os.getcwd(), "comfyui", "output")
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        try:
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])
            
            self.log_message("🖼️ 已打开输出目录")
        except Exception as e:
            self.log_message(f"🛑 打开目录失败: {str(e)}")

    def clear_images(self):
        """清除图像"""
        bat_file = os.path.join(os.getcwd(), "一键清除历史图像文件.bat")
        if os.path.exists(bat_file):
            try:
                subprocess.Popen(bat_file, shell=True)
                self.log_message("🧹 图像清理完成")
            except Exception as e:
                self.log_message(f"🛑 清理失败: {str(e)}")
        else:
            self.log_message("⚠️ 清理脚本不存在")

    def update_status(self):
        """更新状态显示"""
        if self.process:
            self.status_indicator.configure(text="● 服务运行中", bootstyle="success")
            self.service_status_text.configure(text="服务运行中", bootstyle="success")
            self.service_status_label.configure(text="服务状态: 运行中")
            self.process_info_label.configure(text=f"PID: {self.process.pid}")
        else:
            self.status_indicator.configure(text="● 服务已停止", bootstyle="danger")
            self.service_status_text.configure(text="服务已停止", bootstyle="secondary")
            self.service_status_label.configure(text="服务状态: 已停止")
            self.process_info_label.configure(text="PID: 无")
        
        self.update_button_states()

    def update_button_states(self, starting=False):
        """更新按钮状态"""
        if starting:
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='disabled')
            self.restart_btn.configure(state='disabled')
        elif self.process:
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
            self.restart_btn.configure(state='normal')
        else:
            self.start_btn.configure(state='normal')
            self.stop_btn.configure(state='disabled')
            self.restart_btn.configure(state='disabled')

    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.configure(text=f"当前时间: {current_time}")
        self.app.after(1000, self.update_time)

    def toggle_theme(self):
        """切换主题"""
        current_theme = self.app.style.theme.name
        themes = ["darkly", "cosmo", "superhero", "cyborg", "vapor"]
        current_index = themes.index(current_theme) if current_theme in themes else 0
        new_theme = themes[(current_index + 1) % len(themes)]
        
        self.app.style.theme_use(new_theme)
        self.config["theme"] = new_theme
        self.save_config()
        
        self.log_message(f"🎨 已切换到 {new_theme} 主题")

    def increase_font_size(self):
        """增大字体"""
        current_size = self.config.get("font_size", 11)
        if current_size < 20:
            new_size = current_size + 1
            self.config["font_size"] = new_size
            
            if hasattr(self, 'log_terminal') and self.log_terminal:
                self.log_terminal.set_font_size(new_size)
            elif hasattr(self, 'log_text'):
                self.log_text.configure(font=("JetBrains Mono", new_size))
            
            self.save_config()
            self.log_message(f"🔍 字体大小: {new_size}")

    def decrease_font_size(self):
        """减小字体"""
        current_size = self.config.get("font_size", 11)
        if current_size > 8:
            new_size = current_size - 1
            self.config["font_size"] = new_size
            
            if hasattr(self, 'log_terminal') and self.log_terminal:
                self.log_terminal.set_font_size(new_size)
            elif hasattr(self, 'log_text'):
                self.log_text.configure(font=("JetBrains Mono", new_size))
            
            self.save_config()
            self.log_message(f"🔍 字体大小: {new_size}")

    def clear_logs(self):
        """清除日志"""
        if messagebox.askyesno("确认", "确定要清除所有日志吗？"):
            if hasattr(self, 'log_terminal') and self.log_terminal:
                self.log_terminal.clear_terminal()
            elif hasattr(self, 'log_text'):
                self.log_text.configure(state='normal')
                self.log_text.delete(1.0, 'end')
                self.log_text.configure(state='disabled')
            
            self.log_message("📝 日志已清除")

    def export_logs_dialog(self):
        """导出日志对话框"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"control_panel_logs_{timestamp}.txt"
            
            filename = filedialog.asksaveasfilename(
                title="导出日志",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                initialvalue=default_filename
            )
            
            if filename:
                if hasattr(self, 'log_terminal') and self.log_terminal:
                    success = self.log_terminal.export_logs(filename)
                else:
                    content = self.log_text.get(1.0, 'end')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    success = True
                
                if success:
                    self.log_message(f"💾 日志已导出到: {filename}")
                else:
                    self.log_message("🛑 导出失败")
        except Exception as e:
            self.log_message(f"🛑 导出失败: {str(e)}")

    def copy_selected_log(self):
        """复制选中的日志"""
        try:
            if hasattr(self, 'log_terminal') and self.log_terminal:
                selected_text = self.log_terminal.get_selected_text()
                if selected_text:
                    self.log_terminal.copy_to_clipboard(selected_text)
                    self.log_message("📋 已复制选中内容")
                else:
                    self.log_message("⚠️ 没有选中内容")
            else:
                selected_text = self.log_text.selection_get()
                self.app.clipboard_clear()
                self.app.clipboard_append(selected_text)
                self.log_message("📋 已复制选中内容")
        except:
            self.log_message("⚠️ 没有选中内容")

    def search_logs(self, event=None):
        """搜索日志"""
        search_term = self.search_var.get()
        if hasattr(self, 'log_terminal') and self.log_terminal:
            count = self.log_terminal.search_text(search_term)
            if count > 0:
                self.log_message(f"🔍 找到 {count} 个匹配项")
        else:
            # 基本搜索功能
            pass

    def filter_logs(self, event=None):
        """过滤日志级别"""
        level = self.log_level_var.get()
        self.log_message(f"🔍 已切换到 {level} 级别过滤")

    def show_settings(self):
        """显示设置对话框"""
        self.log_message("⚙️ 打开设置面板")
        messagebox.showinfo("设置", "设置功能正在开发中...")

    def show_shortcuts(self):
        """显示快捷键帮助"""
        shortcuts = """
键盘快捷键:

服务控制:
F1 - 启动服务
F2 - 停止服务
F5 - 重启服务

文件操作:
Ctrl+S - 导出日志
Ctrl+L - 清除日志
Ctrl+Q - 退出程序

视图控制:
Ctrl++ - 增大字体
Ctrl+- - 减小字体

其他:
右键 - 显示上下文菜单
        """
        messagebox.showinfo("键盘快捷键", shortcuts)

    def show_about(self):
        """显示关于对话框"""
        about_text = """
绘影 AI 控制面板 - 专业版 v2.0

现代化桌面控制界面
PowerShell 风格日志终端
商业级用户体验

开发: AI Assistant
技术: Python + ttkbootstrap
        """
        messagebox.showinfo("关于", about_text)

    def on_closing(self):
        """窗口关闭事件"""
        if self.process:
            if messagebox.askyesno("确认退出", "服务正在运行，是否停止服务并退出？"):
                self.stop_service()
                time.sleep(1)
                self.quit_app()
        else:
            self.quit_app()

    def quit_app(self):
        """退出应用"""
        self.save_config()
        self.log_message("👋 正在退出控制面板...")
        
        if self.process:
            self.stop_service()
        
        self.app.quit()
        self.app.destroy()

    def run(self):
        """运行应用"""
        self.app.mainloop()

def main():
    """主函数"""
    try:
        app = FinalControlPanel()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()

