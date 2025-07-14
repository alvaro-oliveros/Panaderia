from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from . import models  # Import models to ensure they are registered with Base
from .routes import productos, sedes, movimientos, usuarios, sensores, temperatura, humedad, ai_analytics, voice_chat
from .config import Config

app = FastAPI()

# CORS Middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
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
app.include_router(voice_chat.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Bakery API is running"}
