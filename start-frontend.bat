@echo off
echo ========================================
echo   寺庙修缮募捐功德纪要系统 - 前端启动
echo ========================================
echo.

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo [INFO] 正在安装依赖...
    npm install
)

echo [INFO] 启动前端服务...
echo [INFO] 服务地址: http://localhost:5173
echo.

npm run dev

pause
