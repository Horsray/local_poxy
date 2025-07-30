@echo off
title 一键打包绘影AI控制面板
echo 🎨 正在激活虚拟环境并执行 build_exe.py ...
echo ==============================================


:: 切换到当前 bat 所在目录
cd /d %~dp0

:: 激活虚拟环境
call E:\HueyingAI_Local\env\Scripts\activate

:: 执行打包脚本
python build_exe.py

:: 判断是否执行成功
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 打包成功！
) else (
    echo.
    echo ❌ 打包失败，请检查错误信息！
)

echo.
pause