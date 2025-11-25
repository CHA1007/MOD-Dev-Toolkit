#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from main import ModrinthAPI, ForgeDepGenerator
import threading
import requests
from PIL import Image, ImageTk
import io

# 设置 CustomTkinter 外观和主题
ctk.set_appearance_mode("dark")  # 可选: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"


class ModDependencyGUI:
    """MOD 依赖生成器 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Modrinth MOD 依赖生成器")
        # 增加窗口宽度，让右侧配置信息显示更清晰
        self.root.geometry("1400x800")
        # 设置最小窗口大小
        self.root.minsize(1200, 700)
        
        # 初始化 API 和生成器
        self.api = ModrinthAPI()
        self.generator = ForgeDepGenerator(self.api)
        
        # 存储搜索结果
        self.search_results = []
        self.selected_mod = None
        # 存储图片引用，防止被垃圾回收
        self.image_cache = {}
        # 滑动加载相关
        self.current_query = ""
        self.current_loader = "neoforge"
        self.current_offset = 0
        self.is_loading = False
        self.has_more = True
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部框架 - 搜索区域
        search_frame = ctk.CTkFrame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 搜索标题
        title_label = ctk.CTkLabel(search_frame, text="搜索 MOD", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=5, pady=(10, 5))
        
        # 搜索关键词输入
        ctk.CTkLabel(search_frame, text="MOD 名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=300, placeholder_text="输入 MOD 名称...")
        self.search_entry.grid(row=1, column=1, padx=5, pady=5)
        self.search_entry.bind('<Return>', lambda e: self.search_mods())
        
        # 加载器选择
        ctk.CTkLabel(search_frame, text="加载器:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.loader_var = tk.StringVar(value="forge")
        loader_combo = ctk.CTkComboBox(search_frame, 
                                      values=["forge", "fabric", "neoforge"],
                                      variable=self.loader_var,
                                      width=120)
        loader_combo.grid(row=1, column=3, padx=5, pady=5)
        
        # 搜索按钮
        search_btn = ctk.CTkButton(search_frame, text="搜索", command=self.search_mods, width=100)
        search_btn.grid(row=1, column=4, padx=5, pady=5)
        
        # 中间框架 - 搜索结果和配置
        middle_frame = ctk.CTkFrame(self.root)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧 - 搜索结果列表（固定宽度，支持两列显示）
        left_frame = ctk.CTkFrame(middle_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 5))
        left_frame.pack_propagate(False)
        left_frame.configure(width=600)  # 增加宽度以容纳两列
        
        # 搜索结果标题
        results_title = ctk.CTkLabel(left_frame, text="搜索结果", font=ctk.CTkFont(size=14, weight="bold"))
        results_title.pack(pady=5)
        
        # 搜索结果列表（使用 Canvas + Frame 来支持图片显示）
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建 Canvas 和滚动条
        # 获取当前主题的背景色
        try:
            bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1] if ctk.get_appearance_mode() == "dark" else ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0]
        except Exception:
            bg_color = "#212121"  # 默认深色背景
        canvas = tk.Canvas(list_frame, bg=bg_color, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(list_frame, orientation="vertical", command=canvas.yview)
        self.results_container = ctk.CTkFrame(canvas, fg_color="transparent")
        
        # 配置滚动区域 - 使用grid布局时需要更新滚动区域
        def update_scroll_region(event=None):
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
                # 只有在有搜索结果时才检查是否需要加载更多
                if self.current_query and len(self.search_results) > 0:
                    self.root.after(100, self.check_scroll_load_more)
        
        self.results_container.bind("<Configure>", update_scroll_region)
        # 当网格布局变化时也更新滚动区域
        canvas.bind("<Configure>", lambda e: update_scroll_region())
        
        canvas.create_window((0, 0), window=self.results_container, anchor="nw")
        
        # 自定义滚动命令，用于检测滚动到底部
        def on_scroll(*args):
            scrollbar.set(*args)
            # 延迟检查，避免频繁调用
            self.root.after(100, self.check_scroll_load_more)
        
        canvas.configure(yscrollcommand=on_scroll)
        
        # 绑定鼠标滚轮事件（只处理搜索结果列表区域）
        def _on_canvas_mousewheel(event):
            # 检查鼠标是否在搜索结果列表区域内（排除详情和配置文本区域）
            try:
                widget_under_mouse = self.root.winfo_containing(event.x_root, event.y_root)
                if widget_under_mouse:
                    # 排除详情文本和配置文本区域
                    if hasattr(self, 'detail_text') and widget_under_mouse == self.detail_text:
                        return  # 让 CTkTextbox 自己处理
                    if hasattr(self, 'result_text') and widget_under_mouse == self.result_text:
                        return  # 让 CTkTextbox 自己处理
                    
                    # 向上查找父组件，看是否在 Canvas 区域内
                    current = widget_under_mouse
                    while current:
                        if current == canvas or current == list_frame or current == self.results_container:
                            # Windows 和 Mac
                            if hasattr(event, 'delta') and event.delta:
                                if event.delta > 0:
                                    canvas.yview_scroll(-1, "units")
                                else:
                                    canvas.yview_scroll(1, "units")
                            # Linux
                            elif hasattr(event, 'num'):
                                if event.num == 4:
                                    canvas.yview_scroll(-1, "units")
                                elif event.num == 5:
                                    canvas.yview_scroll(1, "units")
                            # 检查是否需要加载更多
                            self.root.after(50, self.check_scroll_load_more)
                            return "break"  # 阻止事件继续传播
                        # 如果遇到详情或配置文本区域，停止查找
                        if hasattr(self, 'detail_text') and current == self.detail_text:
                            return
                        if hasattr(self, 'result_text') and current == self.result_text:
                            return
                        current = current.master if hasattr(current, 'master') else None
            except Exception:
                pass
        
        # 使用 bind_all 但通过位置检查来限制作用范围
        canvas.bind_all("<MouseWheel>", _on_canvas_mousewheel)
        canvas.bind_all("<Button-4>", _on_canvas_mousewheel)  # Linux
        canvas.bind_all("<Button-5>", _on_canvas_mousewheel)  # Linux
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 存储画布引用
        self.results_canvas = canvas
        self.results_scrollbar = scrollbar
        
        # MOD 详情显示区域 - 固定高度，避免布局变化
        detail_frame = ctk.CTkFrame(left_frame)
        detail_frame.pack(fill=tk.X, pady=(5, 0), padx=5)
        detail_frame.configure(height=150)  # 固定高度
        detail_frame.pack_propagate(False)  # 防止内容改变框架大小
        
        # 详情标题
        detail_title = ctk.CTkLabel(detail_frame, text="MOD 详情", font=ctk.CTkFont(size=12, weight="bold"))
        detail_title.pack(pady=5)
        
        # 详情内容容器 - 左右布局
        detail_content = ctk.CTkFrame(detail_frame)
        detail_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧 - 封面图片显示区域（固定尺寸）
        self.detail_image_frame = ctk.CTkFrame(detail_content)
        self.detail_image_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        self.detail_image_frame.configure(width=120)  # 固定宽度
        self.detail_image_frame.pack_propagate(False)
        
        # 图片占位符（固定尺寸）
        self.detail_image_label = ctk.CTkLabel(self.detail_image_frame, 
                                               text="点击MOD\n查看封面图", 
                                               width=120, 
                                               height=120,
                                               font=ctk.CTkFont(size=10))
        self.detail_image_label.pack(pady=5)
        
        # 右侧 - 文字详情区域
        detail_text_frame = ctk.CTkFrame(detail_content)
        detail_text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.detail_text = ctk.CTkTextbox(detail_text_frame, 
                                         font=ctk.CTkFont(size=15),
                                         wrap=tk.WORD,
                                         state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右侧 - 配置区域（占据剩余空间）
        right_frame = ctk.CTkFrame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 配置标题
        config_title = ctk.CTkLabel(right_frame, text="生成的配置", font=ctk.CTkFont(size=14, weight="bold"))
        config_title.pack(pady=5)
        
        # 版本号输入和生成按钮（顶部工具栏）
        version_frame = ctk.CTkFrame(right_frame)
        version_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 第一行：版本号和生成按钮
        row1 = ctk.CTkFrame(version_frame)
        row1.pack(fill=tk.X, pady=2)
        ctk.CTkLabel(row1, text="Minecraft 版本:").pack(side=tk.LEFT, padx=5)
        self.version_entry = ctk.CTkEntry(row1, width=120)
        self.version_entry.pack(side=tk.LEFT, padx=5)
        self.version_entry.insert(0, "1.21.1")
        
        # 生成按钮
        generate_btn = ctk.CTkButton(row1, text="生成配置", command=self.generate_config, width=100)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        # 第二行：配置模式和依赖类型
        row2 = ctk.CTkFrame(version_frame)
        row2.pack(fill=tk.X, pady=2)
        ctk.CTkLabel(row2, text="配置模式:").pack(side=tk.LEFT, padx=5)
        self.config_mode_var = tk.StringVar(value="full")
        config_mode_combo = ctk.CTkComboBox(row2,
                                           values=["full", "gradle_only", "config_only", "fabric_json", "minimal"],
                                           variable=self.config_mode_var,
                                           width=120)
        config_mode_combo.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row2, text="依赖类型:").pack(side=tk.LEFT, padx=5)
        self.dependency_type_var = tk.StringVar(value="implementation")
        dependency_type_combo = ctk.CTkComboBox(row2,
                                               values=["implementation", "compileOnly", "runtimeOnly", "api"],
                                               variable=self.dependency_type_var,
                                               width=120)
        dependency_type_combo.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域（使用等宽字体，不自动换行，方便查看代码）
        self.result_text = ctk.CTkTextbox(right_frame, 
                                         font=ctk.CTkFont(family="Consolas", size=13),
                                         wrap=tk.NONE)  # 不自动换行，保持代码格式
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0), padx=5)
        
        # 底部框架 - 操作按钮
        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 保存按钮
        save_btn = ctk.CTkButton(bottom_frame, text="保存到文件", command=self.save_to_file, width=120)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        clear_btn = ctk.CTkButton(bottom_frame, text="清空结果", command=self.clear_result, width=120)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ctk.CTkLabel(bottom_frame, textvariable=self.status_var, anchor="w")
        status_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
    
    def search_mods(self, load_more=False):
        """搜索 MOD"""
        # 如果是加载更多，使用之前的查询
        if load_more:
            if not self.current_query:
                return  # 没有之前的搜索，不加载更多
            query = self.current_query
            loader = self.current_loader
            # 检查是否正在加载或没有更多结果
            if self.is_loading or not self.has_more:
                return
            self.status_var.set("正在加载更多...")
        else:
            # 新搜索，从输入框获取
            query = self.search_entry.get().strip()
            if not query:
                messagebox.showwarning("警告", "请输入 MOD 名称！")
                return
            loader = self.loader_var.get()
            # 重置状态
            self.current_query = query
            self.current_loader = loader
            self.current_offset = 0
            self.has_more = True
            self.search_results = []
            # 清空现有结果
            for widget in self.results_container.winfo_children():
                widget.destroy()
            self.image_cache.clear()
            self.status_var.set(f"正在搜索 '{query}' (加载器: {loader})...")
        
        self.is_loading = True
        
        # 在新线程中执行搜索，避免界面卡顿
        def do_search():
            try:
                result_data = self.api.search_projects(
                    self.current_query, 
                    self.current_loader, 
                    limit=20,  # 每次加载20个
                    offset=self.current_offset
                )
                hits = result_data.get('hits', [])
                total = result_data.get('total', 0)
                
                # 检查是否还有更多结果
                has_more = self.current_offset + len(hits) < total
                
                self.root.after(0, self.append_search_results, hits, has_more)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("错误", f"搜索失败: {msg}"))
                self.root.after(0, lambda: self.status_var.set("搜索失败"))
                self.root.after(0, lambda: setattr(self, 'is_loading', False))
        
        threading.Thread(target=do_search, daemon=True).start()
    
    def load_image_from_url(self, url, size=(64, 64), retries=3):
        """从 URL 加载图片并调整大小"""
        if not url:
            return None
        
        # 重试机制
        for attempt in range(retries):
            try:
                # 增加超时时间，添加重试
                response = requests.get(url, timeout=10, stream=True)
                if response.status_code == 200:
                    # 使用 stream 模式，避免一次性加载大文件
                    content = response.content
                    image = Image.open(io.BytesIO(content))
                    image = image.resize(size, Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(image)
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    continue
                print(f"加载图片超时 {url} (尝试 {attempt + 1}/{retries})")
            except requests.exceptions.SSLError as e:
                if attempt < retries - 1:
                    continue
                print(f"加载图片SSL错误 {url}: {e}")
            except Exception as e:
                if attempt < retries - 1:
                    continue
                print(f"加载图片失败 {url}: {e}")
        
        return None
    
    def append_search_results(self, results, has_more):
        """追加搜索结果（用于滑动加载）"""
        if not results and len(self.search_results) == 0:
            # 首次搜索没有结果
            self.status_var.set("未找到相关 MOD")
            # 检查是否包含中文字符
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in self.current_query)
            if has_chinese:
                messagebox.showinfo(
                    "提示", 
                    f"未找到与 '{self.current_query}' 相关的 MOD (加载器: {self.current_loader})\n\n"
                    "提示：Modrinth 主要支持英文搜索。\n"
                    "如果这是中文 MOD 名称，请尝试：\n"
                    "1. 使用 MOD 的英文名称或 Slug\n"
                    "2. 使用拼音搜索\n"
                    "3. 直接在 Modrinth 网站搜索后使用项目 Slug"
                )
            else:
                messagebox.showinfo("提示", f"未找到与 '{self.current_query}' 相关的 MOD (加载器: {self.current_loader})")
            self.is_loading = False
            return
        
        # 追加新结果
        start_index = len(self.search_results)
        self.search_results.extend(results)
        self.current_offset += len(results)
        self.has_more = has_more
        self.is_loading = False
        
        # 重新配置网格列（两列布局）
        self.results_container.grid_columnconfigure(0, weight=1, uniform="mod_col")
        self.results_container.grid_columnconfigure(1, weight=1, uniform="mod_col")
        
        # 创建新结果的列表项
        for idx, mod in enumerate(results):
            self.create_mod_item(mod, start_index + idx)
        
        # 更新状态
        if has_more:
            self.status_var.set(f"已加载 {len(self.search_results)} 个结果（滚动到底部加载更多）")
        else:
            self.status_var.set("已加载全部 {} 个结果".format(len(self.search_results)))
        
        # 更新滚动区域
        if hasattr(self, 'results_canvas'):
            self.results_canvas.update_idletasks()
            bbox = self.results_canvas.bbox("all")
            if bbox:
                self.results_canvas.configure(scrollregion=bbox)
    
    def get_mod_icon_url(self, mod):
        """获取 MOD 的封面图片 URL"""
        # Modrinth API 搜索结果中，icon_url 字段通常包含完整的 CDN URL
        icon_url = mod.get('icon_url')
        
        # 如果 icon_url 存在，直接使用（通常是完整 URL）
        if icon_url:
            # 确保是完整的 URL
            if icon_url.startswith('http://') or icon_url.startswith('https://'):
                return icon_url
            # 如果是相对路径，拼接 CDN 基础 URL
            elif icon_url.startswith('/'):
                return f"https://cdn.modrinth.com{icon_url}"
            else:
                return f"https://cdn.modrinth.com/{icon_url}"
        
        # 如果没有 icon_url，尝试从项目详细信息获取
        project_id = mod.get('slug') or mod.get('project_id') or mod.get('id')
        return project_id  # 返回项目ID，后续异步获取
    
    def create_mod_item(self, mod, index):
        """创建单个 MOD 列表项（包含封面图片）"""
        # 创建项目框架 - 两列布局，固定宽度和高度
        item_frame = ctk.CTkFrame(self.results_container, corner_radius=5)
        # 计算列位置：偶数索引在左列，奇数索引在右列
        row = index // 2
        col = index % 2
        # 固定每个选项的尺寸：宽度约290px，高度约80px
        item_frame.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
        item_frame.configure(width=290, height=80)
        item_frame.pack_propagate(False)  # 防止内容改变框架大小
        
        # 配置列权重，让两列等宽
        self.results_container.grid_columnconfigure(0, weight=1, uniform="mod_col")
        self.results_container.grid_columnconfigure(1, weight=1, uniform="mod_col")
        
        # 获取封面图片 URL
        icon_url_or_id = self.get_mod_icon_url(mod)
        
        # 占位图片（加载中）- 固定尺寸，避免加载时改变大小
        img_label = ctk.CTkLabel(item_frame, text="", 
                                width=64, height=64,
                                fg_color=("gray80", "gray30"))  # 使用主题颜色
        img_label.pack(side=tk.LEFT, padx=5, pady=5)
        # 立即存储引用，确保后续能访问
        item_frame.img_label = img_label
        # 标记初始状态
        item_frame._image_set = False
        item_frame._is_placeholder = False
        
        # 创建图片标签
        def load_image():
            icon_url = icon_url_or_id
            # 如果是项目ID（字符串且不是URL），需要从项目详细信息获取
            if icon_url and not (icon_url.startswith('http://') or icon_url.startswith('https://')):
                try:
                    project = self.api.get_project(icon_url)
                    if project:
                        icon = project.get('icon_url')
                        if icon:
                            if icon.startswith('http://') or icon.startswith('https://'):
                                icon_url = icon
                            elif icon.startswith('/'):
                                icon_url = f"https://cdn.modrinth.com{icon}"
                            else:
                                icon_url = f"https://cdn.modrinth.com/{icon}"
                        else:
                            icon_url = None
                    else:
                        icon_url = None
                except Exception:
                    icon_url = None
            
            # 检查 item_frame 是否仍然存在（防止在加载过程中被销毁）
            if not hasattr(item_frame, 'img_label'):
                return
            
            if icon_url:
                photo = self.load_image_from_url(icon_url, size=(64, 64))
                if photo:
                    # 再次检查 item_frame 是否仍然存在
                    if hasattr(item_frame, 'img_label'):
                        # 使用 after(0) 立即在主线程中执行
                        # 使用默认参数捕获变量，避免闭包问题
                        def set_image(p=photo, f=item_frame):
                            self.set_item_image(f, p)
                        self.root.after(0, set_image)
                else:
                    # 加载失败，显示占位符（但只在还没有设置图片的情况下）
                    if hasattr(item_frame, 'img_label') and not (hasattr(item_frame, '_image_set') and item_frame._image_set):
                        def set_failed(f=item_frame):
                            self.set_item_image_failed(f)
                        self.root.after(0, set_failed)
            else:
                # 没有图片URL，显示占位符（但只在还没有设置图片的情况下）
                if hasattr(item_frame, 'img_label') and not (hasattr(item_frame, '_image_set') and item_frame._image_set):
                    def set_failed(f=item_frame):
                        self.set_item_image_failed(f)
                    self.root.after(0, set_failed)
        
        if icon_url_or_id:
            threading.Thread(target=load_image, daemon=True).start()
        else:
            # 没有图片URL，直接显示占位符
            self.set_item_image_failed(item_frame)
        
        # 文本信息
        text_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        title_label = ctk.CTkLabel(text_frame, text=mod['title'], 
                                  font=ctk.CTkFont(size=12, weight="bold"),
                                  anchor="w")
        title_label.pack(fill=tk.X)
        
        slug_label = ctk.CTkLabel(text_frame, text=f"Slug: {mod['slug']}", 
                                 font=ctk.CTkFont(size=10),
                                 anchor="w",
                                 text_color=("gray50", "gray70"))
        slug_label.pack(fill=tk.X)
        
        # 绑定点击事件 - 整个item_frame都可以点击
        def on_item_click(event=None):
            self.selected_mod = mod
            self.on_mod_select_manual(mod)
            # 高亮选中的项目 - CustomTkinter 使用边框颜色来高亮
            for widget in self.results_container.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.configure(border_width=0)
            item_frame.configure(border_width=2, border_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])
        
        # 让整个item_frame可点击，并添加鼠标悬停效果
        item_frame.bind("<Button-1>", lambda e: on_item_click())
        item_frame.configure(cursor="hand2")
        
        # 让所有子组件也触发父组件的点击事件
        for widget in [img_label, text_frame, title_label, slug_label]:
            widget.bind("<Button-1>", lambda e: on_item_click())
            widget.configure(cursor="hand2")
    
    def set_item_image(self, item_frame, photo):
        """设置列表项的图片"""
        if not hasattr(item_frame, 'img_label'):
            return
        
        # 检查是否已经设置了真实图片（不是占位符）
        # 但允许覆盖占位图片
        if hasattr(item_frame, '_image_set') and item_frame._image_set:
            # 检查当前显示的是否是占位图片
            if hasattr(item_frame, '_is_placeholder') and item_frame._is_placeholder:
                # 是占位图片，允许覆盖
                pass
            else:
                # 已经有真实图片了，不覆盖（防止图片被重复设置导致尺寸变化）
                return
        
        try:
            # 确保图片引用被保存，防止被垃圾回收
            # 先保存引用，再设置图片，防止图片被垃圾回收
            item_frame._photo_ref = photo
            item_frame.img_label.image = photo  # 保存引用
            # 设置图片，保持固定尺寸（64x64）
            item_frame.img_label.configure(image=photo, text="", width=64, height=64)
            # 标记已经设置了图片，且不是占位符
            item_frame._image_set = True
            item_frame._is_placeholder = False
            # 在缓存中保存
            self.image_cache[id(item_frame)] = photo
        except Exception:
            # 如果设置失败，尝试显示占位符
            self.set_item_image_failed(item_frame)
    
    def set_item_image_failed(self, item_frame):
        """设置列表项图片加载失败"""
        if not hasattr(item_frame, 'img_label'):
            return
        
        # 检查是否已经设置了真实图片（防止覆盖已加载的图片）
        if hasattr(item_frame, '_image_set') and item_frame._image_set:
            return
        
        # 创建一个简单的占位图片
        placeholder = Image.new('RGB', (64, 64), color='lightgray')
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(placeholder)
            # 尝试使用默认字体
            try:
                font = ImageFont.truetype("arial.ttf", 10)
            except (OSError, IOError):
                font = ImageFont.load_default()
            draw.text((10, 25), "无图片", fill='gray', font=font)
        except Exception:
            pass
        photo = ImageTk.PhotoImage(placeholder)
        # 先保存引用，再设置图片
        item_frame._photo_ref = photo
        item_frame.img_label.image = photo  # 保持引用
        # 设置图片，保持固定尺寸（64x64）
        item_frame.img_label.configure(image=photo, text="", width=64, height=64)
        # 标记这是占位图片，允许后续真实图片覆盖
        item_frame._image_set = True
        item_frame._is_placeholder = True
        self.image_cache[id(item_frame)] = photo
    
    def on_mod_select_manual(self, mod):
        """手动选择 MOD 时调用"""
        self.selected_mod = mod
        self.status_var.set(f"已选择: {mod['title']}")
        
        # 显示 MOD 详情（包含封面）
        self.detail_text.configure(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        
        detail_info = f"""名称: {mod['title']}
Slug: {mod['slug']}
描述: {mod.get('description', '无描述')[:200]}...
下载量: {mod.get('downloads', 0):,}
"""
        self.detail_text.insert("1.0", detail_info)
        self.detail_text.configure(state=tk.DISABLED)
        
        # 重置图片显示为加载中
        if hasattr(self, 'detail_image_label'):
            self.detail_image_label.configure(image="", text="加载中...")
        
        # 在详情区域显示封面图片
        icon_url_or_id = self.get_mod_icon_url(mod)
        
        def load_detail_image():
            icon_url = icon_url_or_id
            # 如果是项目ID（字符串且不是URL），需要从项目详细信息获取
            if icon_url and not (icon_url.startswith('http://') or icon_url.startswith('https://')):
                try:
                    project = self.api.get_project(icon_url)
                    if project:
                        icon = project.get('icon_url')
                        if icon:
                            if icon.startswith('http://') or icon.startswith('https://'):
                                icon_url = icon
                            elif icon.startswith('/'):
                                icon_url = f"https://cdn.modrinth.com{icon}"
                            else:
                                icon_url = f"https://cdn.modrinth.com/{icon}"
                        else:
                            icon_url = None
                    else:
                        icon_url = None
                except Exception:
                    icon_url = None
            
            if icon_url:
                photo = self.load_image_from_url(icon_url, size=(120, 120))
                if photo:
                    self.root.after(0, lambda p=photo: self.set_detail_image(p))
            else:
                # 没有图片，显示占位符
                self.root.after(0, lambda: self.set_detail_image_failed())
        
        if icon_url_or_id:
            threading.Thread(target=load_detail_image, daemon=True).start()
        else:
            self.set_detail_image_failed()
    
    def set_detail_image(self, photo):
        """在详情区域设置封面图片"""
        if hasattr(self, 'detail_image_label'):
            # 保存图片引用，防止被垃圾回收
            self.detail_image_label.image = photo
            # 设置图片，保持固定尺寸（120x120）
            self.detail_image_label.configure(image=photo, text="", width=120, height=120)
    
    def set_detail_image_failed(self):
        """设置详情区域图片加载失败"""
        if hasattr(self, 'detail_image_label'):
            # 创建占位图片
            placeholder = Image.new('RGB', (120, 120), color='lightgray')
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(placeholder)
                try:
                    font = ImageFont.truetype("arial.ttf", 12)
                except (OSError, IOError):
                    font = ImageFont.load_default()
                draw.text((30, 50), "无图片", fill='gray', font=font)
            except Exception:
                pass
            photo = ImageTk.PhotoImage(placeholder)
            self.detail_image_label.image = photo  # 保持引用
            self.detail_image_label.configure(image=photo, text="", width=120, height=120)
    
    def generate_config(self):
        """生成依赖配置"""
        if not self.selected_mod:
            messagebox.showwarning("警告", "请先选择一个 MOD！")
            return
        
        game_version = self.version_entry.get().strip() or None
        loader = self.loader_var.get()
        config_mode = self.config_mode_var.get()
        dependency_type = self.dependency_type_var.get()
        
        self.status_var.set("正在生成配置...")
        
        # 在新线程中执行生成，避免界面卡顿
        def do_generate():
            try:
                config = self.generator.generate_full_dependency_info(
                    self.selected_mod['slug'], 
                    game_version, 
                    loader,
                    config_mode=config_mode,
                    dependency_type=dependency_type
                )
                self.root.after(0, self.update_result, config)
                self.root.after(0, lambda: self.status_var.set("配置生成完成"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("错误", f"生成配置失败: {msg}"))
                self.root.after(0, lambda: self.status_var.set("生成失败"))
        
        threading.Thread(target=do_generate, daemon=True).start()
    
    def update_result(self, config):
        """更新结果显示"""
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", config)
    
    def save_to_file(self):
        """保存配置到文件"""
        content = self.result_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有可保存的内容！")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile="dependency_output.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"已保存到: {filename}")
                self.status_var.set(f"已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {e}")
    
    def clear_result(self):
        """清空结果"""
        self.result_text.delete("1.0", tk.END)
        self.status_var.set("已清空结果")
    
    def check_scroll_load_more(self):
        """检查滚动位置，如果接近底部则加载更多"""
        if not hasattr(self, 'results_canvas'):
            return
        # 如果没有搜索过，不检查
        if not self.current_query:
            return
        if not self.has_more or self.is_loading:
            return
        
        try:
            canvas = self.results_canvas
            # 获取滚动位置（0.0 到 1.0）
            top, bottom = canvas.yview()
            
            # 如果滚动到距离底部10%以内，加载更多
            if bottom >= 0.9:
                self.search_mods(load_more=True)
        except Exception:
            pass


def main():
    """主函数"""
    root = ctk.CTk()  # 使用 CustomTkinter 的窗口
    ModDependencyGUI(root)  # 创建GUI实例
    root.mainloop()


if __name__ == '__main__':
    main()

