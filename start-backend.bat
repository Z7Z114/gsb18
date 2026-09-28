@echo off
echo ========================================
echo   寺庙修缮募捐功德纪要系统 - 后端启动
echo ========================================
echo.

cd /d "%~dp0"

if not exist "backend\venv" (
    echo [INFO] 正在创建虚拟环境...
    python -m venv backend\venv
    call backend\venv\Scripts\activate.bat
    echo [INFO] 正在安装依赖...
    pip install -r requirements.txt
) else (
    call backend\venv\Scripts\activate.bat
)

echo [INFO] 启动后端服务...
echo [INFO] 服务地址: http://localhost:8000
echo [INFO] API文档: http://localhost:8000/docs
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
