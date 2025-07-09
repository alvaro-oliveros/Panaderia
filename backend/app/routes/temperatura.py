from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas
from datetime import datetime

router = APIRouter(prefix="/temperatura", tags=["Temperatura"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def crear_lectura_temperatura(temperatura: schemas.TemperaturaCreate, db: Session = Depends(get_db)):
    # Create temperature record
    data = temperatura.dict()
    
    # If ESP32 sends fecha, parse it and use it
    if data.get('fecha'):
        try:
            # Parse ESP32 timestamp (assume it's already in Lima time)
            fecha_esp32 = datetime.fromisoformat(data['fecha'])
            data['fecha'] = fecha_esp32
        except ValueError:
            # If parsing fails, remove fecha and let model use default
            data.pop('fecha', None)
    
    nueva = models.Temperatura(**data)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/")
def obtener_temperaturas(
    user_id: int = None, 
    sensor_id: int = None, 
    limit: int = 50, 
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.Temperatura)
    
    if sensor_id:
        query = query.filter(models.Temperatura.Sensor_id == sensor_id)
    
    if user_id:
        # Filtrar por sensores de sedes del usuario
        user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == user_id).all()
        sede_ids = [us.sede_id for us in user_sedes]
        
        if sede_ids:
            sensores_usuario = db.query(models.Sensor).filter(models.Sensor.sede_id.in_(sede_ids)).all()
            sensor_ids = [s.idSensores for s in sensores_usuario]
            query = query.filter(models.Temperatura.Sensor_id.in_(sensor_ids))
        else:
            # User has no assigned sedes, return empty list
            return {"temperatures": [], "total": 0, "has_more": False}
    
    # Count total for pagination info
    total_count = query.count()
    
    # Order by most recent first and apply pagination
    temperaturas = query.order_by(models.Temperatura.fecha.desc()).offset(offset).limit(limit).all()
    
    # Return paginated response
    return {
        "temperatures": temperaturas,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }

@router.get("/{temperatura_id}")
def obtener_temperatura(temperatura_id: int, db: Session = Depends(get_db)):
    temperatura = db.query(models.Temperatura).filter(models.Temperatura.idTemperatura == temperatura_id).first()
    if not temperatura:
        raise HTTPException(status_code=404, detail="Lectura de temperatura no encontrada")
    return temperatura

@router.put("/{temperatura_id}")
def actualizar_temperatura(temperatura_id: int, temperatura: schemas.TemperaturaUpdate, db: Session = Depends(get_db)):
    db_temperatura = db.query(models.Temperatura).filter(models.Temperatura.idTemperatura == temperatura_id).first()
    if not db_temperatura:
        raise HTTPException(status_code=404, detail="Lectura de temperatura no encontrada")
    
    for key, value in temperatura.dict(exclude_unset=True).items():
        setattr(db_temperatura, key, value)
    
    db.commit()
    db.refresh(db_temperatura)
    return db_temperatura

@router.delete("/{temperatura_id}")
def eliminar_temperatura(temperatura_id: int, db: Session = Depends(get_db)):
    temperatura = db.query(models.Temperatura).filter(models.Temperatura.idTemperatura == temperatura_id).first()
    if not temperatura:
        raise HTTPException(status_code=404, detail="Lectura de temperatura no encontrada")
    
    db.delete(temperatura)
    db.commit()
    return {"message": "Lectura de temperatura eliminada correctamente"}