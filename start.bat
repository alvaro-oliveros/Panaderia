@echo off
title Sistema de Gestión de Panadería

echo 🍞 Iniciando Sistema de Gestión de Panadería...
echo ================================================

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    pause
    exit /b 1
)

REM Verificar estructura de directorios
if not exist "backend" (
    echo ❌ Carpeta backend no encontrada
    echo Ejecutar desde la carpeta raíz del proyecto
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Carpeta frontend no encontrada
    echo Ejecutar desde la carpeta raíz del proyecto
    pause
    exit /b 1
)

echo 🚀 Iniciando servidor backend (puerto 8000)...
cd backend

REM Verificar entorno virtual
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📦 Verificando dependencias...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependencias...
    pip install fastapi uvicorn sqlalchemy
)

REM Iniciar backend
start "Backend Server" cmd /c "uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

cd ..

echo 🌐 Iniciando servidor frontend (puerto 3000)...
REM Iniciar frontend
start "Frontend Server" cmd /c "python -m http.server 3000 --directory frontend"

echo.
echo ✅ ¡Sistema iniciado correctamente!
echo ================================================
echo 🌐 Frontend: http://localhost:3000/login.html
echo 🔧 Backend API: http://localhost:8000
echo 📚 Documentación API: http://localhost:8000/docs
echo.
echo 👥 Credenciales de prueba:
echo    Admin: admin / admin123
echo    Usuario: usuario1 / user123
echo.
echo Presiona cualquier tecla para cerrar los servidores...
echo ================================================

pause

REM Cerrar servidores
taskkill /f /im python.exe /t >nul 2>&1
taskkill /f /im uvicorn.exe /t >nul 2>&1