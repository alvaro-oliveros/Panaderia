from pydantic import BaseModel
from typing import Optional

class SedeCreate(BaseModel):
    Nombre: str
    Direccion: str
    Usuario_id: int

class ProductoCreate(BaseModel):
    Nombre: str
    Descripcion: str
    Precio: float
    Stock: float
    Unidad: str
    Categoria: str
    Sede_id: int

class MovimientoCreate(BaseModel):
    producto_id: int
    Cantidad: float
    Precio: float
    tipo: str
    Usuario_id: int
    sede_id: int

class UsuarioCreate(BaseModel):
    username: str
    password: str
    rol: str
    sede_ids: Optional[list[int]] = []

class UsuarioUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    sede_ids: Optional[list[int]] = None

class UsuarioLogin(BaseModel):
    username: str
    password: str

class SensorCreate(BaseModel):
    nombre: str
    descripcion: str
    sede_id: int

class SensorUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    sede_id: Optional[int] = None

class TemperaturaCreate(BaseModel):
    Temperatura: float
    Sensor_id: int

class TemperaturaUpdate(BaseModel):
    Temperatura: Optional[float] = None
    Sensor_id: Optional[int] = None

class HumedadCreate(BaseModel):
    Humedad: float
    Sensor_id: int

class HumedadUpdate(BaseModel):
    Humedad: Optional[float] = None
    Sensor_id: Optional[int] = None
