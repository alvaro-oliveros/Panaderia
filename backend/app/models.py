from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime
import pytz

def get_lima_time():
    """Get current time in Lima, Peru timezone"""
    lima_tz = pytz.timezone('America/Lima')
    return datetime.now(lima_tz)

class Sede(Base):
    __tablename__ = "Sedes"
    idSedes = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(45))
    Direccion = Column(String(45))
    Usuario_id = Column(Integer)

class Producto(Base):
    __tablename__ = "Productos"
    idProductos = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(50))
    Descripcion = Column(String(50))
    Precio = Column(Float)
    Stock = Column(Float)
    Unidad = Column(String(45))
    Categoria = Column(String(100))
    Fecha_Creacion = Column(DateTime, default=func.now())
    Fecha_Actualiazacion = Column(DateTime, default=func.now(), onupdate=func.now())
    Sede_id = Column(Integer, ForeignKey("Sedes.idSedes"))

class Movimiento(Base):
    __tablename__ = "Movimientos"
    idMovimientos = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("Productos.idProductos"))
    Cantidad = Column(Float)
    Precio = Column(Float)
    tipo = Column(Enum("venta", "reabastecimiento", "ajuste", "agregado", "entrada", name="tipo_movimiento"))
    fecha = Column(DateTime, default=get_lima_time)
    Usuario_id = Column(Integer, ForeignKey("Usuarios.idUsuarios"))
    sede_id = Column(Integer, ForeignKey("Sedes.idSedes"))

class Usuario(Base):
    __tablename__ = "Usuarios"
    idUsuarios = Column(Integer, primary_key=True, index=True)
    username = Column(String(45))
    password = Column(String(45))
    rol = Column(Enum("admin", "usuario", name="rol_usuario"))

class UsuarioSede(Base):
    __tablename__ = "UsuarioSedes"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("Usuarios.idUsuarios"))
    sede_id = Column(Integer, ForeignKey("Sedes.idSedes"))

class Sensor(Base):
    __tablename__ = "Sensores"
    idSensores = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(45))
    descripcion = Column(String(45))
    sede_id = Column(Integer, ForeignKey("Sedes.idSedes"))

class Temperatura(Base):
    __tablename__ = "Temperatura"
    idTemperatura = Column(Integer, primary_key=True, index=True)
    Temperatura = Column(Float)  # DECIMAL(10,2) equivalent
    Sensor_id = Column(Integer, ForeignKey("Sensores.idSensores"))
    fecha = Column(DateTime, default=get_lima_time)

class Humedad(Base):
    __tablename__ = "Humedad"
    idHumedad = Column(Integer, primary_key=True, index=True)
    Humedad = Column(Float)  # Humidity percentage 0-100
    Sensor_id = Column(Integer, ForeignKey("Sensores.idSensores"))
    fecha = Column(DateTime, default=get_lima_time)

class ChatSession(Base):
    __tablename__ = "ChatSessions"
    idChatSession = Column(Integer, primary_key=True, index=True)
    Usuario_id = Column(Integer, ForeignKey("Usuarios.idUsuarios"))
    session_start = Column(DateTime, default=get_lima_time)
    session_end = Column(DateTime, nullable=True)
    total_queries = Column(Integer, default=0)
    session_active = Column(Boolean, default=True)

class VoiceQuery(Base):
    __tablename__ = "VoiceQueries"
    idVoiceQuery = Column(Integer, primary_key=True, index=True)
    ChatSession_id = Column(Integer, ForeignKey("ChatSessions.idChatSession"))
    Usuario_id = Column(Integer, ForeignKey("Usuarios.idUsuarios"))
    audio_transcription = Column(String(1000))  # Transcribed text from Whisper
    user_query = Column(String(1000))  # Processed/cleaned query
    ai_response = Column(String(2000))  # AI-generated response
    query_type = Column(String(50))  # e.g., "inventory", "sales", "environmental", "general"
    execution_time_ms = Column(Integer)  # Response time in milliseconds
    success = Column(Boolean, default=True)
    error_message = Column(String(500), nullable=True)
    fecha = Column(DateTime, default=get_lima_time)
