from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def crear_movimiento(mov: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    nuevo = models.Movimiento(**mov.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/")
def listar_movimientos(
    user_id: int = None, 
    limit: int = 50, 
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.Movimiento)
    
    # If user_id is provided, filter by user's assigned sedes
    if user_id:
        # Get user's assigned sedes
        user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == user_id).all()
        sede_ids = [us.sede_id for us in user_sedes]
        
        if sede_ids:
            query = query.filter(models.Movimiento.sede_id.in_(sede_ids))
        else:
            # User has no assigned sedes, return empty list
            return {"movements": [], "total": 0, "has_more": False}
    
    # Count total for pagination info
    total_count = query.count()
    
    # Order by most recent first and apply pagination
    movements = query.order_by(models.Movimiento.fecha.desc()).offset(offset).limit(limit).all()
    
    # Return paginated response
    return {
        "movements": movements,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }

@router.put("/{movimiento_id}")
def actualizar_movimiento(movimiento_id: int, datos: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    movimiento = db.query(models.Movimiento).filter(models.Movimiento.idMovimientos == movimiento_id).first()
    if not movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    
    for key, value in datos.dict().items():
        setattr(movimiento, key, value)
    
    db.commit()
    db.refresh(movimiento)
    return movimiento

@router.delete("/{movimiento_id}")
def eliminar_movimiento(movimiento_id: int, db: Session = Depends(get_db)):
    movimiento = db.query(models.Movimiento).filter(models.Movimiento.idMovimientos == movimiento_id).first()
    if not movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    
    db.delete(movimiento)
    db.commit()
    return {"message": "Movimiento eliminado"}