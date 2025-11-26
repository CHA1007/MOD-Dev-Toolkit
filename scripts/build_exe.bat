@echo off
chcp 65001 >nul
echo ========================================
echo Auto Depen 打包脚本
echo ========================================
echo.

cd /d "%~dp0\.."
python scripts\build_exe.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 打包成功！
    echo 生成的 exe 文件在 dist 目录中
    pause
) else (
    echo.
    echo 打包失败，请检查错误信息
    pause
)

