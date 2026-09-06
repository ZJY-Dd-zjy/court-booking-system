@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =========================================
echo   🔄 Git 自动提交脚本
echo   项目：体育馆智能预约系统
echo =========================================
echo.

REM 检查是否在 git 仓库中
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：当前目录不是 Git 仓库！
    pause
    exit /b 1
)

REM 获取当前分支
git branch --show-current > _branch.tmp 2>nul
set /p BRANCH=<_branch.tmp
del _branch.tmp

echo 📍 当前分支：%BRANCH%
echo.

REM 检查是否有改动
git diff --quiet
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo ✅ 没有需要提交的改动，已经是最新状态。
    echo.
    pause
    exit /b 0
)

REM 显示改动摘要
echo 📋 改动的文件：
git status --short
echo.

REM 询问提交信息
set "msg="
set /p msg="📝 输入提交说明（直接回车使用自动生成的）："

if "%msg%"=="" (
    REM 自动生成提交信息
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set mytime=%%a:%%b)
    set "msg=auto: update at %mydate% %mytime%"
    echo 📝 使用自动提交信息：%msg%
)

echo.
echo ⏳ 正在提交...

git add -A
git commit -m "%msg%"

if %errorlevel% neq 0 (
    echo ❌ 提交失败！
    pause
    exit /b 1
)

echo.
echo 🚀 推送到远程仓库 origin/%BRANCH% ...
git push origin %BRANCH%

if %errorlevel% neq 0 (
    echo ❌ 推送失败！请检查网络或远程仓库配置。
    pause
    exit /b 1
)

echo.
echo =========================================
echo   ✅ 提交并推送成功！
echo =========================================
echo.
pause
