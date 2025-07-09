from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas
from datetime import datetime

router = APIRouter(prefix="/humedad", tags=["Humedad"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def crear_lectura_humedad(humedad: schemas.HumedadCreate, db: Session = Depends(get_db)):
    # Create humidity record
    data = humedad.dict()
    
    # Create the model instance
    nueva = models.Humedad(
        Humedad=data['Humedad'],
        Sensor_id=data['Sensor_id']
    )
    
    # If ESP32 sends fecha, parse it and use it (assume it's already in Lima time)
    if data.get('fecha'):
        try:
            fecha_esp32 = datetime.fromisoformat(data['fecha'])
            nueva.fecha = fecha_esp32
        except ValueError:
            # If parsing fails, let model use default
            pass
    
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/")
def obtener_humedades(
    user_id: int = None, 
    sensor_id: int = None, 
    limit: int = 50, 
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.Humedad)
    
    if sensor_id:
        query = query.filter(models.Humedad.Sensor_id == sensor_id)
    
    if user_id:
        # Filtrar por sensores de sedes del usuario
        user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == user_id).all()
        sede_ids = [us.sede_id for us in user_sedes]
        
        if sede_ids:
            sensores_usuario = db.query(models.Sensor).filter(models.Sensor.sede_id.in_(sede_ids)).all()
            sensor_ids = [s.idSensores for s in sensores_usuario]
            query = query.filter(models.Humedad.Sensor_id.in_(sensor_ids))
        else:
            # User has no assigned sedes, return empty list
            return {"humidities": [], "total": 0, "has_more": False}
    
    # Count total for pagination info
    total_count = query.count()
    
    # Order by most recent first and apply pagination
    humedades = query.order_by(models.Humedad.fecha.desc()).offset(offset).limit(limit).all()
    
    # Return paginated response
    return {
        "humidities": humedades,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }

@router.get("/{humedad_id}")
def obtener_humedad(humedad_id: int, db: Session = Depends(get_db)):
    humedad = db.query(models.Humedad).filter(models.Humedad.idHumedad == humedad_id).first()
    if not humedad:
        raise HTTPException(status_code=404, detail="Lectura de humedad no encontrada")
    return humedad

@router.put("/{humedad_id}")
def actualizar_humedad(humedad_id: int, humedad: schemas.HumedadUpdate, db: Session = Depends(get_db)):
    db_humedad = db.query(models.Humedad).filter(models.Humedad.idHumedad == humedad_id).first()
    if not db_humedad:
        raise HTTPException(status_code=404, detail="Lectura de humedad no encontrada")
    
    for key, value in humedad.dict(exclude_unset=True).items():
        setattr(db_humedad, key, value)
    
    db.commit()
    db.refresh(db_humedad)
    return db_humedad

@router.delete("/{humedad_id}")
def eliminar_humedad(humedad_id: int, db: Session = Depends(get_db)):
    humedad = db.query(models.Humedad).filter(models.Humedad.idHumedad == humedad_id).first()
    if not humedad:
        raise HTTPException(status_code=404, detail="Lectura de humedad no encontrada")
    
    db.delete(humedad)
    db.commit()
    return {"message": "Lectura de humedad eliminada correctamente"}