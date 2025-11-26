# 构建脚本说明

此目录包含用于构建可执行文件的脚本。

## 文件说明

- `build_exe.py` - Python 构建脚本
- `build_exe.bat` - Windows 批处理脚本

## 使用方法

### Windows

**方法 1：使用批处理脚本**
```bash
scripts\build_exe.bat
```

**方法 2：使用 Python 脚本**
```bash
# 在项目根目录运行
python scripts\build_exe.py

# 或进入 scripts 目录运行
cd scripts
python build_exe.py
```

### Linux/Mac

```bash
# 在项目根目录运行
python3 scripts/build_exe.py

# 或进入 scripts 目录运行
cd scripts
python3 build_exe.py
```

## 构建要求

1. **Python 环境**
   - Python 3.8 或更高版本
   - 已安装所有依赖（运行 `pip install -r requirements.txt`）

2. **PyInstaller**
   - 构建脚本会自动安装 PyInstaller
   - 或手动安装: `pip install pyinstaller`

## 构建输出

构建完成后，生成的 exe 文件位于项目根目录的 `dist/` 目录中。

文件名格式：`MOD开发工具箱 - 版本号.exe`

例如：`MOD开发工具箱 - 1.2.0.exe`

## 注意事项

1. 构建脚本会自动从 `main.py` 读取版本号
2. 构建产物（`build/` 和 `dist/` 目录）会被 `.gitignore` 忽略
3. 构建过程中生成的临时文件（如 `version_info.txt` 和 `.spec` 文件）会在构建完成后自动清理

