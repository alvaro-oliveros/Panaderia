from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas

router = APIRouter(prefix="/productos", tags=["Productos"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def crear_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    nuevo = models.Producto(**producto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/")
def listar_productos(
    user_id: int = None, 
    limit: int = 50, 
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.Producto)
    
    # If user_id is provided, filter by user's assigned sedes
    if user_id:
        # Get user's assigned sedes
        user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == user_id).all()
        sede_ids = [us.sede_id for us in user_sedes]
        
        if sede_ids:
            query = query.filter(models.Producto.Sede_id.in_(sede_ids))
        else:
            # User has no assigned sedes, return empty list
            return {"productos": [], "total": 0, "has_more": False}
    
    # Count total for pagination info
    total_count = query.count()
    
    # Apply pagination
    productos = query.offset(offset).limit(limit).all()
    
    # Return paginated response
    return {
        "productos": productos,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }

@router.put("/{producto_id}")
def actualizar_producto(producto_id: int, datos: schemas.ProductoCreate, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.idProductos == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    for key, value in datos.dict().items():
        setattr(producto, key, value)
    
    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.idProductos == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(producto)
    db.commit()
    return {"message": "Producto eliminado"}