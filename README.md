# MOD开发工具箱 (MOD Dev Toolkit)

基于 WPF + [WPF-UI](https://github.com/lepoco/wpfui)（Win11 Fluent 风格）的 Minecraft MOD 开发辅助工具。

## 功能特性

### 首页

- 🔍 **MOD 搜索**：通过 Modrinth API 搜索 MOD，支持加载器（Forge/Fabric/NeoForge/Quilt）与游戏版本筛选，回车即可搜索
- 📋 **搜索结果**：列表展示 MOD 图标、分类、**版本数与版本信息**、下载量、更新时间
- 📦 **依赖配置生成**：选择 MOD 版本（含游戏版本标注）/ 配置模式 / 依赖类型，一键生成 Gradle 配置
- 📋 **复制与保存**：生成结果可复制到剪贴板，或保存为 `.txt` / `.gradle` 文件

### 设置

- 🎨 **主题颜色**：默认天蓝色，内置 8 种预设强调色，点选立即生效并记住选择
- 🌐 **API 端点**：可自定义 MOD 搜索 API 端点（需兼容 Modrinth v2 接口），支持连接测试与一键恢复默认
- 🗑️ **缓存清理**：API 响应会缓存到本地（搜索 30 分钟、版本列表 15 分钟），可查看占用并一键清理
- ℹ️ **关于**：版本与项目信息

### 界面

- 🪟 **Win11 Fluent**：Mica 材质背景、圆角窗口、系统级标题栏
- ✨ **页面过渡动画**：侧边导航切换带淡入 + 滑动动画
- 🧭 **侧边导航**：首页 / 设置

## 技术栈

- **.NET 9**（`net9.0-windows`）+ WPF
- [WPF-UI](https://github.com/lepoco/wpfui) 4.3 — Fluent 控件库
- [Modrinth API](https://docs.modrinth.com/) — 数据来源
- Newtonsoft.Json — 设置持久化

## 项目结构

```
MOD-Dev-Toolkit/
├── MODDevToolkit.csproj        # 项目文件（.NET 9 + WPF-UI）
├── App.xaml / App.xaml.cs      # 应用入口，启动时加载设置并应用主题色
├── MainWindow.xaml / .cs       # 主窗口：FluentWindow + 侧边导航
├── Pages/
│   ├── HomePage.xaml / .cs     # 首页：搜索 + 结果列表 + 配置生成入口
│   └── SettingsPage.xaml / .cs # 设置：主题色 / API 端点 / 缓存 / 关于
├── Windows/
│   └── ConfigGeneratorWindow.xaml / .cs  # 配置生成对话框
├── Models/
│   └── ModInfo.cs              # 数据模型（ModInfo / ModVersion / SearchResult）
├── Services/
│   ├── ModrinthApi.cs          # Modrinth API 客户端（可配置端点 + 文件缓存）
│   ├── AppSettings.cs          # 设置模型与持久化
│   └── ThemeService.cs         # 强调色运行时切换
├── Styles/
│   ├── Colors.xaml             # 应用语义色
│   └── Controls.xaml           # 卡片 / 列表项 / 色块等辅助样式
└── assets/icons/
    ├── app_icon.png            # 像素画原图（图标源文件）
    └── app_icon.ico            # 多尺寸图标（exe 文件图标 + 窗口图标）
```

## 构建和运行

### 前置要求

- Windows 10 / 11
- [.NET 9 SDK](https://dotnet.microsoft.com/download) 或更高版本

### 命令行

```bash
# 恢复依赖
dotnet restore

# 构建
dotnet build

# 运行
dotnet run

```

### 发布与分发

WPF 受框架限制**不支持裁剪**，依赖框架模式下单文件也**不能压缩**，故体积下限由 WPF-UI（约 6.3MB）决定。两种模式二选一：

**极致小体积（默认，需目标机装 .NET 9 桌面运行时）**——exe 约 7.2MB，可再压成约 2.8MB 的 zip 分发：

```bash
dotnet publish MODDevToolkit.csproj -c Release -r win-x64 --self-contained false -p:PublishSingleFile=true -o ./publish
```

> 目标机若无运行时，双击会提示安装；下载地址：[.NET 9 桌面运行时](https://dotnet.microsoft.com/download/dotnet/9.0)（选 .NET Desktop Runtime / Windows x64）。

**免安装（自包含 + 单文件压缩，约 68MB）**——拷贝即用，目标机无需任何安装：

```bash
dotnet publish MODDevToolkit.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:PublishReadyToRun=true -p:IncludeNativeLibrariesForSelfExtract=true -p:EnableCompressionInSingleFile=true -o ./publish
```

## 数据存储

| 内容 | 位置 |
|------|------|
| 设置（主题色、API 端点） | `%APPDATA%/MODDevToolkit/settings.json` |
| API 缓存 | `%LOCALAPPDATA%/MODDevToolkit/cache/` |

## 版本信息

当前版本：2.0.0

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 相关链接

- [Modrinth 官网](https://modrinth.com/)
- [Modrinth API 文档](https://docs.modrinth.com/)
- [WPF-UI](https://github.com/lepoco/wpfui)
