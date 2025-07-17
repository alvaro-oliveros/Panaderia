from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas
import hashlib

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

@router.post("/")
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing_user = db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user (password stored as plain text to match your schema)
    nuevo_usuario = models.Usuario(
        username=usuario.username,
        password=usuario.password,
        rol=usuario.rol
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    # Assign sedes to user if provided
    if usuario.sede_ids:
        for sede_id in usuario.sede_ids:
            usuario_sede = models.UsuarioSede(
                usuario_id=nuevo_usuario.idUsuarios,
                sede_id=sede_id
            )
            db.add(usuario_sede)
        db.commit()
    
    # Get assigned sedes
    user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == nuevo_usuario.idUsuarios).all()
    sede_ids = [us.sede_id for us in user_sedes]
    
    # Return user without password
    return {
        "idUsuarios": nuevo_usuario.idUsuarios,
        "username": nuevo_usuario.username,
        "rol": nuevo_usuario.rol,
        "sede_ids": sede_ids
    }

@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    # Return users without passwords but with their assigned sedes
    result = []
    for usuario in usuarios:
        user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == usuario.idUsuarios).all()
        sede_ids = [us.sede_id for us in user_sedes]
        
        result.append({
            "idUsuarios": usuario.idUsuarios,
            "username": usuario.username,
            "rol": usuario.rol,
            "sede_ids": sede_ids
        })
    
    return result

@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.idUsuarios == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Get assigned sedes
    user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == usuario_id).all()
    sede_ids = [us.sede_id for us in user_sedes]
    
    return {
        "idUsuarios": usuario.idUsuarios,
        "username": usuario.username,
        "rol": usuario.rol,
        "sede_ids": sede_ids
    }

@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: int, datos: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.idUsuarios == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Check if username is being changed and if it already exists
    if datos.username and datos.username != usuario.username:
        existing_user = db.query(models.Usuario).filter(models.Usuario.username == datos.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Update user fields (excluding sede_ids)
    update_data = datos.dict(exclude_unset=True, exclude={'sede_ids'})
    for key, value in update_data.items():
        setattr(usuario, key, value)
    
    # Update sede assignments if provided
    if datos.sede_ids is not None:
        # Delete existing assignments
        db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == usuario_id).delete()
        
        # Add new assignments
        for sede_id in datos.sede_ids:
            usuario_sede = models.UsuarioSede(
                usuario_id=usuario_id,
                sede_id=sede_id
            )
            db.add(usuario_sede)
    
    db.commit()
    db.refresh(usuario)
    
    # Get updated assigned sedes
    user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == usuario_id).all()
    sede_ids = [us.sede_id for us in user_sedes]
    
    return {
        "idUsuarios": usuario.idUsuarios,
        "username": usuario.username,
        "rol": usuario.rol,
        "sede_ids": sede_ids
    }

@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.idUsuarios == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usuario)
    db.commit()
    return {"message": "Usuario eliminado"}

@router.post("/login")
def login_usuario(login_data: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.username == login_data.username).first()
    
    if not usuario or usuario.password != login_data.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Get user's assigned sedes with sede names
    user_sedes = db.query(models.UsuarioSede).filter(models.UsuarioSede.usuario_id == usuario.idUsuarios).all()
    sede_ids = [us.sede_id for us in user_sedes]
    
    # Get sede names
    sedes_info = []
    if sede_ids:
        sedes = db.query(models.Sede).filter(models.Sede.idSedes.in_(sede_ids)).all()
        sedes_info = [{"idSedes": sede.idSedes, "Nombre": sede.Nombre} for sede in sedes]
    
    return {
        "idUsuarios": usuario.idUsuarios,
        "username": usuario.username,
        "rol": usuario.rol,
        "sede_ids": sede_ids,
        "sedes": sedes_info
    }