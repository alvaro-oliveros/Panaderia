#!/bin/bash

# Script para iniciar el sistema de panadería

echo "🍞 Iniciando Sistema de Gestión de Panadería..."
echo "================================================"

# Verificar si Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar estructura de directorios
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Estructura de directorios incorrecta"
    echo "Ejecutar desde la carpeta raíz del proyecto"
    exit 1
fi

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidores..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturar Ctrl+C para limpiar procesos
trap cleanup SIGINT

echo "🚀 Iniciando servidor backend (puerto 8000)..."
cd backend

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias si no existen
if [ ! -f "venv/pyvenv.cfg" ] || ! pip show fastapi &> /dev/null; then
    echo "📦 Instalando dependencias..."
    pip install fastapi uvicorn sqlalchemy
fi

# Iniciar backend en segundo plano usando configuración
uvicorn app.main:app --reload --host ${HOST:-127.0.0.1} --port ${PORT:-8000} &
BACKEND_PID=$!

cd ..

echo "🌐 Iniciando servidor frontend (puerto 3000)..."
# Iniciar frontend en segundo plano
python3 -m http.server 3000 --directory frontend &
FRONTEND_PID=$!

echo ""
echo "✅ ¡Sistema iniciado correctamente!"
echo "================================================"
echo "🌐 Frontend: http://localhost:3000/login.html"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 Documentación API: http://localhost:8000/docs"
echo ""
echo "👥 Credenciales de prueba:"
echo "   Admin: admin / admin123"
echo "   Usuario: usuario1 / user123"
echo ""
echo "Presiona Ctrl+C para detener los servidores"
echo "================================================"

# Esperar a que los procesos terminen
wait $BACKEND_PID $FRONTEND_PID