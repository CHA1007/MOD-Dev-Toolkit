# MOD开发工具箱 (MOD Dev Toolkit)

一个用于生成、配置、查询我的世界MOD开发相关内容的工具箱

## 功能特性

### 依赖配置生成
- 🔍 **MOD 搜索**：通过 Modrinth API 搜索 MOD
- 📦 **多种配置模式**：支持完整模式、仅 Gradle、仅配置文件等多种输出格式
- 🎯 **版本选择**：支持查看和选择 MOD 的历史版本
- 🔧 **加载器筛选**：根据选择的加载器自动筛选可用版本
- 📝 **多种依赖类型**：支持 implementation、compileOnly、runtimeOnly、api 等

### 界面与体验
- 🎨 **现代化 GUI**：使用 CustomTkinter 构建的美观界面
- 💾 **配置保存**：支持将生成的配置保存到文件
- 📋 **一键复制**：快速复制生成的配置代码

### 未来规划
- 📚 **MOD 信息查询**：查询 MOD 详细信息、更新日志等
- ⚙️ **开发配置管理**：管理 MOD 开发相关的配置文件
- 🔗 **依赖关系分析**：分析 MOD 之间的依赖关系

## 项目结构

```
MOD开发工具箱/
├── models.py            # 数据模型（ModVersion, ModInfo）
├── api.py               # Modrinth API 客户端
├── generator.py         # 依赖配置生成器
├── main.py              # 程序入口（版本号和主函数）
├── gui.py               # GUI 界面
├── requirements.txt     # Python 依赖
├── LICENSE              # MIT 许可证
├── start_gui.bat        # Windows 快速启动脚本
├── check_dependencies.py # 依赖检查工具
├── scripts/             # 构建脚本目录
│   ├── build_exe.py     # Python 构建脚本
│   ├── build_exe.bat    # Windows 构建脚本
│   └── README.md        # 构建说明
└── README.md            # 本文件
```

### 模块说明

- **models.py** - 定义数据模型类（`ModVersion`, `ModInfo`）
- **api.py** - Modrinth API 客户端，负责与 Modrinth API 交互
- **generator.py** - 依赖配置生成器，生成各种格式的依赖配置
- **main.py** - 程序入口，定义版本号并启动 GUI
- **gui.py** - 图形用户界面，使用 CustomTkinter 构建

## 安装和使用

### 环境要求

- Python 3.8 或更高版本
- 已安装所有依赖（见 `requirements.txt`）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

**启动 GUI**
```bash
python gui.py
# Windows 用户可以直接双击 start_gui.bat
```

**查看帮助**
```bash
python main.py --help
```

**查看版本**
```bash
python main.py --version
```

## 构建可执行文件

构建脚本已移至 `scripts/` 目录，与源码分离。

详细说明请查看：[scripts/README.md](scripts/README.md)

快速构建（Windows）：
```bash
scripts\build_exe.bat
```

## 使用说明

1. 启动程序后，在搜索框输入 MOD 名称
2. 选择加载器类型（Forge/Fabric/NeoForge）
3. 点击"搜索"按钮
4. 从搜索结果中选择 MOD
5. 选择 MOD 版本（可选，默认使用最新版本）
6. 选择配置模式和依赖类型
7. 输入 Minecraft 版本（可选）
8. 点击"生成配置"按钮
9. 复制生成的配置代码或保存到文件

## 配置模式说明

- **full** - 完整模式：包含所有配置（Gradle + 配置文件）
- **gradle_only** - 仅 Gradle：只生成 build.gradle 配置
- **config_only** - 仅配置文件：只生成 mods.toml 或 fabric.mod.json
- **fabric_json** - 仅 Fabric JSON：只生成 fabric.mod.json
- **minimal** - 最小模式：只生成依赖代码行

## 依赖类型说明

- **implementation** - 实现依赖（默认）
- **compileOnly** - 仅编译时依赖
- **runtimeOnly** - 仅运行时依赖
- **api** - API 依赖

## 版本信息

当前版本：1.2.0

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [Modrinth 官网](https://modrinth.com/)
- [Modrinth API 文档](https://docs.modrinth.com/)

