# 打包说明

## 快速打包

### Windows
直接运行 `build_exe.bat` 即可自动打包。

### 手动打包
```bash
python build_exe.py
```

## 打包要求

1. **Python 环境**
   - Python 3.8 或更高版本
   - 已安装所有依赖（运行 `pip install -r requirements.txt`）

2. **PyInstaller**
   - 打包脚本会自动安装 PyInstaller
   - 或手动安装: `pip install pyinstaller`

## 打包选项说明

当前打包配置：
- `--onefile`: 打包成单个 exe 文件
- `--windowed`: 不显示控制台窗口（GUI 程序）
- `--name=AutoDepen`: 生成的 exe 文件名为 `AutoDepen.exe`

## 自定义打包

如果需要修改打包选项，可以编辑 `build_exe.py` 文件中的 `cmd` 变量。

### 常用选项

- `--console`: 显示控制台窗口（用于调试）
- `--icon=icon.ico`: 指定图标文件
- `--add-data`: 添加额外文件
- `--hidden-import`: 添加隐藏导入的模块

### 示例：带控制台的打包

修改 `build_exe.py` 中的 `cmd` 变量，将 `--windowed` 改为 `--console`：

```python
"--console",  # 显示控制台窗口（用于调试）
```

## 打包后的文件

打包完成后，exe 文件位于 `dist/AutoDepen.exe`

## 注意事项

1. **首次运行**
   - 首次运行可能会被杀毒软件拦截，需要添加信任
   - 可能需要安装 Visual C++ Redistributable

2. **文件大小**
   - 打包后的 exe 文件可能较大（通常 50-100MB），这是正常的
   - 因为包含了 Python 解释器和所有依赖库

3. **运行环境**
   - 打包后的 exe 可以在没有安装 Python 的 Windows 系统上运行
   - 不需要安装任何依赖

4. **错误排查**
   - 如果程序无法运行，尝试使用 `--console` 参数重新打包查看错误信息
   - 检查是否缺少某些隐藏导入的模块

## 高级配置

如果需要更精细的控制，可以生成 spec 文件：

```bash
pyinstaller --name=AutoDepen main.py
```

然后编辑生成的 `AutoDepen.spec` 文件，最后运行：

```bash
pyinstaller AutoDepen.spec
```

