from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas

router = APIRouter(prefix="/sedes", tags=["Sedes"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def crear_sede(sede: schemas.SedeCreate, db: Session = Depends(get_db)):
    nueva = models.Sede(**sede.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/")
def listar_sedes(db: Session = Depends(get_db)):
    return db.query(models.Sede).all()

@router.put("/{sede_id}")
def actualizar_sede(sede_id: int, datos: schemas.SedeCreate, db: Session = Depends(get_db)):
    sede = db.query(models.Sede).filter(models.Sede.idSedes == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    
    for key, value in datos.dict().items():
        setattr(sede, key, value)
    
    db.commit()
    db.refresh(sede)
    return sede

@router.delete("/{sede_id}")
def eliminar_sede(sede_id: int, db: Session = Depends(get_db)):
    sede = db.query(models.Sede).filter(models.Sede.idSedes == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    
    db.delete(sede)
    db.commit()
    return {"message": "Sede eliminada"}