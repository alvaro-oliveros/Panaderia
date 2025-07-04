from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes import productos, sedes, movimientos, usuarios, sensores, temperatura, humedad, ai_analytics

app = FastAPI()

# ✅ CORS Middleware para permitir peticiones desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O mejor: ["http://127.0.0.1:5500"] si usas Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✔ Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

# ✔ Rutas
app.include_router(productos.router)
app.include_router(sedes.router)
app.include_router(movimientos.router)
app.include_router(usuarios.router)
app.include_router(sensores.router)
app.include_router(temperatura.router)
app.include_router(humedad.router)
app.include_router(ai_analytics.router)
