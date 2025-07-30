@echo off
TITLE 一键打包Hueying桌面版

:: 切换到脚本所在目录
cd /d %~dp0

:: 1. 安装依赖
call npm install --prefix electron_app >nul 2>&1

:: 2. 打包 Electron 应用
npx --prefix electron_app electron-packager ./electron_app HueyingDesktop --platform=win32 --arch=x64 --out=dist --overwrite --icon=icon.ico

:: 3. 拷贝 Python 文件及依赖
xcopy main.py dist\HueyingDesktop-win32-x64 /Y
xcopy payload.b64 dist\HueyingDesktop-win32-x64 /Y
xcopy update.py dist\HueyingDesktop-win32-x64 /Y

ECHO 打包完成，文件位于 dist\HueyingDesktop-win32-x64
pause
