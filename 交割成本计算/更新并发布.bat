@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 交割成本计算器 - 更新并发布
echo ====================================
echo 正在运行，请稍候...
echo.
python publish.py
echo.
pause
