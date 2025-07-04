# 🍞 Sistema de Gestión de Panadería

Un sistema completo de gestión para múltiples panaderías con autenticación basada en roles, IoT sensor integration, AI-powered analytics, y control de acceso por sede.

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.8+
- SQLite3
- Navegador web moderno

### Configuración de Variables de Entorno (Opcional)

Para funciones AI, configurar la API key de Claude:
```bash
# Opción 1: Variable de entorno
export CLAUDE_API_KEY="your-claude-api-key-here"

# Opción 2: Archivo .env
echo "CLAUDE_API_KEY=your-api-key" > .env
```

### Opción 1: Inicio Automático (Recomendado)

**Linux/Mac:**
```bash
cd Panaderia
./start.sh
```

**Windows:**
```cmd
cd Panaderia
start.bat
```

El script automáticamente:
- ✅ Crea el entorno virtual
- ✅ Instala las dependencias
- ✅ Inicia ambos servidores
- ✅ Muestra las URLs de acceso

### Opción 2: Inicio Manual

1. **Configurar el backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install fastapi uvicorn sqlalchemy
   ```

2. **Terminal 1 - Servidor backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Terminal 2 - Servidor frontend**
   ```bash
   cd Panaderia
   python3 -m http.server 3000 --directory frontend
   ```

### Acceso a la Aplicación
- **Frontend**: http://localhost:3000/login.html
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000/index.html (después del login)
- **Sensores**: http://localhost:3000/sensores.html
- **Temperatura**: http://localhost:3000/temperatura.html
- **Humedad**: http://localhost:3000/humedad.html

## 👥 Acceso al Sistema

### Administrador
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Tipo:** Seleccionar "Administrador"

**Permisos del administrador:**
- Ver y gestionar todas las sedes
- Ver todos los productos y movimientos de todas las sedes
- Crear, editar y eliminar usuarios
- Asignar usuarios a múltiples sedes
- Acceso completo a todas las funcionalidades

### Usuario Regular
- **Usuario:** `user2`
- **Contraseña:** `user2`
- **Tipo:** Seleccionar "Panadería Centro"

**Permisos del usuario regular:**
- Solo ve productos y movimientos de sus sedes asignadas
- No puede gestionar sedes ni usuarios
- Puede agregar productos y movimientos solo a sus sedes asignadas

## 🏗️ Estructura del Sistema

### Backend (FastAPI)
```
backend/
├── app/
│   ├── models.py       # Modelos de base de datos
│   ├── schemas.py      # Esquemas de validación
│   ├── database.py     # Configuración de BD
│   ├── main.py         # Aplicación principal
│   └── routes/         # Endpoints de la API
│       ├── productos.py
│       ├── sedes.py
│       ├── movimientos.py
│       └── usuarios.py
└── panaderia.db        # Base de datos SQLite
```

### Frontend (HTML/CSS/JS)
```
frontend/
├── login.html          # Página de inicio de sesión
├── index.html          # Dashboard principal
├── productos.html      # Gestión de productos
├── sedes.html          # Gestión de sedes (solo admin)
├── movimientos.html    # Gestión de movimientos
├── usuarios.html       # Gestión de usuarios (solo admin)
├── css/style.css       # Estilos del sistema
└── js/
    ├── api.js          # Configuración de API
    ├── login.js        # Lógica de autenticación
    └── dashboard.js    # Lógica del dashboard
```

## 📊 Funcionalidades Principales

### 1. **Gestión de Productos**
- ✅ Crear nuevos productos con información completa
- ✅ Ver lista de productos con **paginación** (50 productos por página)
- ✅ Editar y eliminar productos
- ✅ Categorización por tipo (pan, pasteles, galletas, bebidas, otros)
- ✅ Control de stock e inventario
- ✅ Asignación por sede
- ✅ **Alertas de stock bajo** automáticas

### 2. **Gestión de Movimientos**
- ✅ Registrar entradas y salidas de productos
- ✅ Seguimiento de inventario en tiempo real
- ✅ Filtrado por sede del usuario
- ✅ Historial completo de transacciones
- ✅ Vinculación automática con productos y sedes

### 3. **Gestión de Sedes** (Solo Administradores)
- ✅ Crear y gestionar múltiples panaderías
- ✅ Información completa de ubicación
- ✅ Asignación de usuarios a sedes específicas

### 4. **Gestión de Usuarios** (Solo Administradores)
- ✅ Crear usuarios con roles específicos
- ✅ Asignación múltiple de sedes por usuario
- ✅ Control de acceso basado en roles
- ✅ Gestión de contraseñas
- ✅ Interface de checkbox para asignación de sedes

### 5. **Dashboard Interactivo**
- ✅ Vista tabular organizada con navegación por pestañas
- ✅ Una tabla visible a la vez para mejor usabilidad
- ✅ Datos filtrados según permisos del usuario
- ✅ Navegación intuitiva entre módulos (Sedes, Productos, Movimientos)
- ✅ Información de sesión y usuario activo
- ✅ Ocultación automática de pestañas según rol de usuario
- ✅ **Analytics en tiempo real** (ventas hoy, productos vendidos, etc.)

### 6. **🤖 AI Analytics (Claude-powered)**
- ✅ **Insights inteligentes** sobre patrones de venta
- ✅ **Recomendaciones automáticas** para optimización
- ✅ **Análisis de performance** por sede
- ✅ **Modo mock** para testing sin consumir créditos
- ✅ **Dashboard en tiempo real** con métricas AI

### 7. **🌡️ IoT Sensor Integration**
- ✅ **Monitoreo de temperatura y humedad** en tiempo real
- ✅ **ESP32 support** con código Arduino incluido
- ✅ **Sistema de alertas** visual y sonoro
- ✅ **Dashboard de sensores** con histórico
- ✅ **Alertas automáticas** para condiciones críticas

## 🔐 Sistema de Autenticación

### Tipos de Usuario

1. **Administrador (`admin`)**
   - Acceso completo al sistema
   - Ve todos los datos de todas las sedes
   - Puede gestionar usuarios y sedes
   - Sin restricciones de acceso

2. **Usuario Regular (`usuario`)**
   - Acceso limitado a sedes asignadas
   - Solo ve productos y movimientos de sus sedes
   - No puede gestionar usuarios ni crear sedes
   - Interface adaptada según permisos

### Control de Acceso por Sede
- Los usuarios regulares pueden ser asignados a múltiples sedes
- El sistema filtra automáticamente la información mostrada
- Los formularios solo muestran opciones disponibles para el usuario
- Validación tanto en frontend como backend

## 🗄️ Base de Datos

### Tablas Principales
- **Usuarios**: Información de usuarios y roles
- **Sedes**: Datos de las panaderías
- **Productos**: Inventario de productos
- **Movimientos**: Historial de entradas/salidas
- **UsuarioSedes**: Relación muchos-a-muchos entre usuarios y sedes

## 🛠️ API Endpoints

### Productos
- `GET /productos/` - Listar productos (con filtro opcional por user_id)
- `POST /productos/` - Crear producto
- `PUT /productos/{id}` - Actualizar producto
- `DELETE /productos/{id}` - Eliminar producto

### Movimientos
- `GET /movimientos/` - Listar movimientos (con filtro opcional por user_id)
- `POST /movimientos/` - Crear movimiento
- `PUT /movimientos/{id}` - Actualizar movimiento
- `DELETE /movimientos/{id}` - Eliminar movimiento

### Sedes
- `GET /sedes/` - Listar sedes
- `POST /sedes/` - Crear sede
- `PUT /sedes/{id}` - Actualizar sede
- `DELETE /sedes/{id}` - Eliminar sede

### Usuarios
- `GET /usuarios/` - Listar usuarios
- `POST /usuarios/` - Crear usuario
- `POST /usuarios/login` - Autenticación
- `PUT /usuarios/{id}` - Actualizar usuario
- `DELETE /usuarios/{id}` - Eliminar usuario

## 🎯 Casos de Uso

### Escenario 1: Administrador
1. Inicia sesión como admin
2. Ve dashboard con todos los datos del sistema
3. Gestiona usuarios asignándolos a sedes específicas
4. Supervisa operaciones de todas las panaderías

### Escenario 2: Usuario de Panadería
1. Inicia sesión como usuario regular
2. Ve solo productos y movimientos de sus sedes asignadas
3. Registra nuevos productos para sus sedes
4. Controla entradas y salidas de inventario

## 🔧 Personalización

### Agregar Nuevas Categorías
Editar `productos.html` líneas 58-65 para agregar categorías:
```html
<option value="nueva_categoria">Nueva Categoría</option>
```

### Modificar Unidades de Medida
Editar `productos.html` líneas 46-53 para agregar unidades:
```html
<option value="nueva_unidad">Nueva Unidad</option>
```

## 📝 Datos de Prueba

El sistema incluye datos de ejemplo:
- 3 sedes: Centro, Norte, Sur
- 5 productos variados
- 5 movimientos de prueba
- Usuarios de ejemplo configurados

## 🐛 Resolución de Problemas

### Error de Conexión Backend
```bash
# Verificar que el servidor esté ejecutándose
curl http://127.0.0.1:8000/sedes/
```

### Base de Datos Corrupta
```bash
# Eliminar y recrear la base de datos
rm backend/panaderia.db
# Reiniciar el servidor para recrear las tablas
```

### Problemas de CORS
- Asegurar que el frontend se sirva desde `http://127.0.0.1` o `localhost`
- Verificar configuración CORS en `backend/app/main.py`

## 🛡️ Seguridad y Preparación para GitHub

### Variables de Entorno Sensibles
✅ **API keys**: Configuradas via variables de entorno, no en código
✅ **Base de datos**: Excluida de git via .gitignore
✅ **Archivos de configuración**: .env y logs excluidos

### Archivo .gitignore Incluido
El proyecto incluye un `.gitignore` comprehensivo que excluye:
- Variables de entorno (.env)
- Base de datos (*.db)
- Entorno virtual de Python (venv/)
- Archivos de log y temporales
- API keys y secretos

### 🔐 Antes de Subir a GitHub:
1. ✅ **API keys removed**: No hay keys hardcoded en el código
2. ✅ **.gitignore created**: Archivos sensibles excluidos
3. ✅ **Environment setup**: Documentación de variables de entorno
4. ✅ **Sample data**: Solo datos de prueba, no información real

### 🌟 Características para GitHub:
- **README comprehensivo** con instrucciones de setup
- **Código limpio** sin información sensible
- **Documentación completa** de API endpoints
- **Instrucciones de IoT setup** incluidas
- **Guías de troubleshooting**

## 🚀 Próximas Funcionalidades

- [ ] Reportes y análisis de ventas avanzados
- [ ] Integración con sistemas de punto de venta
- [ ] ✅ ~~Notificaciones de stock bajo~~ (Implementado)
- [ ] Backup automático de datos
- [ ] API móvil para empleados
- [ ] ✅ ~~Paginación de productos~~ (Implementado)
- [ ] ✅ ~~AI Analytics~~ (Implementado)
- [ ] ✅ ~~IoT Sensor Integration~~ (Implementado)

## 📞 Contribuir

1. Fork el repositorio
2. Crear feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

---

**🔧 Stack Técnico:**
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **AI**: Claude (Anthropic) API integration
- **IoT**: ESP32 + Arduino + DHT22 sensors
- **Analytics**: Real-time dashboard with AI insights

**Para soporte técnico, revisar los logs del servidor backend y la consola del navegador para errores de frontend.**