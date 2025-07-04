# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Start the Application
- **Linux/Mac**: `./start.sh` - Automated startup script that handles venv, dependencies, and both servers
- **Windows**: `start.bat` - Windows equivalent of the startup script
- **Manual backend**: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- **Manual frontend**: `python3 -m http.server 3000 --directory frontend`

### Python Environment Management
- Virtual environment is located at `backend/venv/`
- Dependencies are managed via pip, not poetry/pipenv
- Required packages: `fastapi uvicorn sqlalchemy requests`
- Install: `cd backend && source venv/bin/activate && pip install fastapi uvicorn sqlalchemy requests`

### Sensor Testing (Temperature/Humidity)
- **Start test data generation**: `cd backend && source venv/bin/activate && cd .. && python test_humidity_data.py`
- **Stop test script**: Find process with `ps aux | grep test_humidity_data`, then `kill <process_id>`
- **What it does**: Generates realistic temperature (16-32°C) and humidity (30-80%) data every 15 seconds
- **View data**: http://localhost:3000/temperatura.html or http://localhost:3000/humedad.html

### Business Data Generation
- **Generate realistic business data**: `cd backend && source venv/bin/activate && cd .. && python generate_business_data.py`
- **What it creates**: 5 bakery locations, 185+ products, 6 months of historical sales data (19,000+ movements)
- **Includes**: Realistic patterns (weekends, holidays, seasonal items), different sede characteristics
- **Perfect for**: AI analytics, dashboard demonstrations, class projects

### Database Operations
- SQLite database at `backend/panaderia.db`
- No migrations system - tables auto-created via SQLAlchemy models
- To reset database: `rm backend/panaderia.db` and restart server
- Test database connectivity: `curl http://127.0.0.1:8000/sedes/`

## Architecture Overview

### Backend (FastAPI + SQLAlchemy + SQLite)
- **Entry point**: `backend/app/main.py` - FastAPI application with CORS middleware
- **Models**: `backend/app/models.py` - SQLAlchemy ORM models for all entities
- **Database**: `backend/app/database.py` - SQLite connection and session management
- **API Routes**: `backend/app/routes/` - Modular route handlers by entity
  - `productos.py` - Product CRUD operations
  - `sedes.py` - Bakery location management
  - `movimientos.py` - Inventory movement tracking  
  - `usuarios.py` - User authentication and management
- **Schemas**: `backend/app/schemas.py` - Pydantic models for request/response validation

### Frontend (Vanilla HTML/CSS/JavaScript)
- **Authentication**: `frontend/js/api.js` - Session management, auth checking
- **Entry point**: `frontend/login.html` - Authentication interface
- **Main dashboard**: `frontend/index.html` - Admin/user role-based interface
- **Module pages**: Products, sedes, movements, users - each with dedicated HTML/JS
- **Styling**: `frontend/css/style.css` - Single CSS file for all styling
- **API integration**: JavaScript fetch API, no framework dependencies

### Database Schema
- **Multi-tenant**: Users can be assigned to multiple bakery locations (sedes)
- **Role-based access**: `admin` users see all data, `usuario` users see only assigned locations
- **Key relationships**: 
  - Products belong to specific sedes
  - Movements track product inventory changes per sede
  - UsuarioSedes junction table for many-to-many user-sede assignments

## Authentication & Authorization

### Test Credentials
- **Admin**: username=`admin`, password=`admin123`
- **Regular user**: username=`user2`, password=`user2`

### Access Control
- Admin users: Full system access, can manage all sedes, users, products
- Regular users: Limited to assigned sedes only, filtered data access
- Frontend role checking: `isAdmin()` function in `api.js`
- Backend filtering: API endpoints accept `user_id` parameter for data filtering

## Key Application URLs
- **Frontend**: http://localhost:3000/login.html
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Test API**: `curl http://127.0.0.1:8000/sedes/`

## Development Notes

### Code Patterns
- No TypeScript - pure JavaScript with DOM manipulation
- No modern frameworks - vanilla HTML/CSS/JS approach
- FastAPI follows standard patterns with dependency injection for database sessions
- SQLAlchemy models use descriptive Spanish field names matching business domain
- Frontend uses sessionStorage for auth state, not localStorage or cookies

### Common Tasks
- **Add new entity**: Create model in `models.py`, add route file, update main.py includes
- **Modify database**: Edit models and restart server (no migrations needed)
- **Add frontend page**: Create HTML file, corresponding JS file, update navigation
- **Debug API**: Use FastAPI's built-in Swagger docs at `/docs` endpoint
- **Test auth**: Check sessionStorage in browser dev tools for userData

### System Constraints
- Single SQLite database file - not suitable for concurrent high-load scenarios
- No real authentication tokens - uses simple session storage
- CORS configured for wildcard origins (`allow_origins=["*"]`)
- Backend runs on 127.0.0.1:8000, frontend on localhost:3000
- No automated testing framework present