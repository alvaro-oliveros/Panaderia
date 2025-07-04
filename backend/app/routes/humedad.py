from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas

router = APIRouter(prefix="/humedad", tags=["Humedad"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def crear_lectura_humedad(humedad: schemas.HumedadCreate, db: Session = Depends(get_db)):
    nueva = models.Humedad(**humedad.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/")
def obtener_humedades(user_id: int = None, sensor_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Humedad)
    
    if sensor_id:
        query = query.filter(models.Humedad.Sensor_id == sensor_id)
    
    if user_id:
        # Filtrar por sensores de sedes del usuario
        user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == user_id).all()
        sede_ids = [us.sede_id for us in user_sedes]
        sensores_usuario = db.query(models.Sensor).filter(models.Sensor.sede_id.in_(sede_ids)).all()
        sensor_ids = [s.idSensores for s in sensores_usuario]
        query = query.filter(models.Humedad.Sensor_id.in_(sensor_ids))
    
    humedades = query.order_by(models.Humedad.fecha.desc()).all()
    return humedades

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