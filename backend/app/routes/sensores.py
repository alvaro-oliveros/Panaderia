from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas

router = APIRouter(prefix="/sensores", tags=["Sensores"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def crear_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    nuevo = models.Sensor(**sensor.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/")
def obtener_sensores(user_id: int = None, db: Session = Depends(get_db)):
    if user_id:
        # Filtrar sensores por sedes del usuario
        user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == user_id).all()
        sede_ids = [us.sede_id for us in user_sedes]
        sensores = db.query(models.Sensor).filter(models.Sensor.sede_id.in_(sede_ids)).all()
    else:
        sensores = db.query(models.Sensor).all()
    return sensores

@router.get("/{sensor_id}")
def obtener_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = db.query(models.Sensor).filter(models.Sensor.idSensores == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return sensor

@router.put("/{sensor_id}")
def actualizar_sensor(sensor_id: int, sensor: schemas.SensorUpdate, db: Session = Depends(get_db)):
    db_sensor = db.query(models.Sensor).filter(models.Sensor.idSensores == sensor_id).first()
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    for key, value in sensor.dict(exclude_unset=True).items():
        setattr(db_sensor, key, value)
    
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@router.delete("/{sensor_id}")
def eliminar_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = db.query(models.Sensor).filter(models.Sensor.idSensores == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    db.delete(sensor)
    db.commit()
    return {"message": "Sensor eliminado correctamente"}