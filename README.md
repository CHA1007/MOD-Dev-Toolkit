# MOD开发工具箱 (MOD Dev Toolkit)

基于 WPF + [WPF-UI](https://github.com/lepoco/wpfui)（Win11 Fluent 风格）的 Minecraft MOD 开发辅助工具。

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
