from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import os
import tempfile
import time
from openai import OpenAI

from .. import database, models
from ..routes.ai_analytics import get_business_summary_data

router = APIRouter(prefix="/voice", tags=["Voice Chat"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OpenAI configuration
def get_openai_client():
    """Get OpenAI client with API key from environment"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key no configurada")
    return OpenAI(api_key=api_key)

def build_database_context(db: Session, user_id: int) -> str:
    """Build comprehensive database context for GPT queries"""
    
    # Get user info and permissions
    user = db.query(models.Usuario).filter(models.Usuario.idUsuarios == user_id).first()
    if not user:
        return "Usuario no encontrado"
    
    # Get business data (which now includes sede info for low stock products)
    business_data = get_business_summary_data(db, days_back=7)
    
    # Use the improved low stock data from business_data that includes sede information
    low_stock_with_sede = business_data.get('productos_stock_bajo', [])
    
    # Get recent environmental data
    recent_temp = db.query(models.Temperatura).order_by(desc(models.Temperatura.fecha)).first()
    recent_humidity = db.query(models.Humedad).order_by(desc(models.Humedad.fecha)).first()
    
    # Build context
    context = f"""
CONTEXTO DE LA PANADERÍA - BASE DE DATOS ACTUAL

INFORMACIÓN DEL USUARIO:
- Usuario: {user.username}
- Rol: {user.rol}
- Permisos: {'Administrador total' if user.rol == 'admin' else 'Usuario regular con acceso limitado'}

RESUMEN DEL NEGOCIO (últimos 7 días):
- Ingresos totales: S/. {business_data['resumen_ventas']['total_ingresos']:,.2f}
- Transacciones: {business_data['resumen_ventas']['total_transacciones']}
- Promedio por transacción: S/. {business_data['resumen_ventas']['ingreso_promedio_transaccion']:,.2f}

PRODUCTOS CON STOCK BAJO (menos de 10 unidades):
{', '.join([f"{p['nombre']}: {p['stock_actual']} unidades en {p.get('sede_nombre', 'Sede no especificada')}" for p in low_stock_with_sede]) if low_stock_with_sede else "Todos los productos tienen stock adecuado"}

CONDICIONES AMBIENTALES ACTUALES:
- Temperatura: {f"{recent_temp.Temperatura:.1f}°C (hace {_get_time_ago(recent_temp.fecha)})" if recent_temp else "Sin datos de temperatura"}
- Humedad: {f"{recent_humidity.Humedad:.1f}% (hace {_get_time_ago(recent_humidity.fecha)})" if recent_humidity else "Sin datos de humedad"}

SEDES OPERATIVAS: {business_data['total_sedes']}
PRODUCTOS TOTALES: {business_data['total_productos']}

PRODUCTOS MÁS VENDIDOS (últimos 7 días):
{chr(10).join([f"- {p['nombre']}: {p['cantidad_vendida']} unidades (S/. {p['ingresos']:,.2f})" for p in business_data['productos_top'][:5]])}

RENDIMIENTO POR SEDE:
{chr(10).join([f"- {s['nombre']}: S/. {s['ingresos']:,.2f} en {s['transacciones']} transacciones" for s in business_data['performance_sedes']])}
"""
    
    return context

def _get_time_ago(date_time: datetime) -> str:
    """Helper function to get human-readable time difference"""
    if not date_time:
        return "fecha desconocida"
    
    now = datetime.now(date_time.tzinfo) if date_time.tzinfo else datetime.now()
    diff = now - date_time
    
    if diff.days > 0:
        return f"{diff.days} día{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hora{'s' if hours > 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minuto{'s' if minutes > 1 else ''}"
    else:
        return "ahora mismo"

def classify_query_type(query: str) -> str:
    """Classify the type of query for analytics"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['venta', 'vendido', 'ingreso', 'dinero', 'precio']):
        return "sales"
    elif any(word in query_lower for word in ['stock', 'inventario', 'producto', 'cantidad']):
        return "inventory"
    elif any(word in query_lower for word in ['temperatura', 'humedad', 'ambiente', 'clima']):
        return "environmental"
    elif any(word in query_lower for word in ['sede', 'tienda', 'ubicación', 'sucursal']):
        return "locations"
    elif any(word in query_lower for word in ['usuario', 'empleado', 'staff', 'personal']):
        return "users"
    else:
        return "general"

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Transcribe audio to Spanish text using Whisper API"""
    
    start_time = time.time()
    
    try:
        # Validate user
        user = db.query(models.Usuario).filter(models.Usuario.idUsuarios == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Validate audio file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Archivo debe ser de audio")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Initialize OpenAI client
            client = get_openai_client()
            
            # Transcribe audio using Whisper
            with open(temp_file_path, 'rb') as audio_data:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data,
                    language="es"  # Spanish
                )
            
            transcribed_text = transcript.text
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "transcription": transcribed_text,
                "language": "es",
                "execution_time_ms": execution_time,
                "audio_duration": len(content) // 16000,  # Approximate duration estimation
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "error": str(e),
            "execution_time_ms": execution_time
        }

@router.post("/query")
async def process_voice_query(
    query: str = Form(...),
    user_id: int = Form(...),
    session_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Process transcribed text query and generate intelligent response"""
    
    start_time = time.time()
    query_type = classify_query_type(query)
    
    try:
        # Validate user
        user = db.query(models.Usuario).filter(models.Usuario.idUsuarios == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Get or create chat session
        if session_id:
            chat_session = db.query(models.ChatSession).filter(
                models.ChatSession.idChatSession == session_id,
                models.ChatSession.Usuario_id == user_id,
                models.ChatSession.session_active == True
            ).first()
        else:
            chat_session = None
        
        if not chat_session:
            chat_session = models.ChatSession(
                Usuario_id=user_id,
                session_start=datetime.now(),
                total_queries=0,
                session_active=True
            )
            db.add(chat_session)
            db.commit()
            db.refresh(chat_session)
        
        # Build database context
        context = build_database_context(db, user_id)
        
        # Initialize OpenAI client
        client = get_openai_client()
        
        # Create comprehensive prompt
        system_prompt = f"""
Eres un asistente inteligente especializado en gestión de panaderías peruanas. Tu trabajo es responder preguntas sobre el negocio usando los datos proporcionados.

CONTEXTO DE LA BASE DE DATOS:
{context}

INSTRUCCIONES:
1. Responde SOLO con información basada en los datos proporcionados
2. Si no tienes los datos necesarios, dilo claramente
3. Sé conciso pero informativo (máximo 150 palabras)
4. Usa un tono profesional pero amigable
5. Incluye números específicos cuando sea relevante
6. Si es una consulta sobre acciones (como registrar ventas), explica el proceso
7. Para datos ambientales, menciona si hay alguna condición preocupante
8. IMPORTANTE: Cuando menciones productos con stock bajo, SIEMPRE incluye la sede donde se encuentra cada producto
   - CORRECTO: "Torta de Chocolate: 8 unidades en Panadería Centro"
   - INCORRECTO: "Torta de Chocolate: 8 unidades"
   - La información de sede está disponible en el contexto - úsala SIEMPRE para productos con stock bajo
9. MONEDA: Todos los precios e ingresos están en SOLES PERUANOS (S/.). Siempre usa S/. para cantidades monetarias, nunca dólares ($)

TIPOS DE CONSULTAS QUE PUEDES MANEJAR:
- Ventas y ingresos
- Stock e inventario
- Productos más vendidos
- Rendimiento por sede
- Condiciones ambientales
- Alertas de stock bajo
- Información general del negocio

Responde en español de manera natural y conversacional.

RECORDATORIO FINAL: Esta es una panadería PERUANA. Todos los valores monetarios DEBEN mostrarse en SOLES PERUANOS con el símbolo S/. Por ejemplo: "S/. 1,250.00" NO "$1,250.00". Es MUY IMPORTANTE usar la moneda correcta.
"""
        
        # Enhance query for inventory questions and currency
        enhanced_query = query
        if query_type == "inventory" and any(word in query.lower() for word in ['stock', 'inventario', 'poco stock', 'low stock']):
            enhanced_query = f"{query} - Recuerda incluir la sede (ubicación) para cada producto con stock bajo."
        
        # Add currency instruction to all queries
        enhanced_query = f"{enhanced_query} IMPORTANTE: Usa SIEMPRE soles peruanos (S/.) para cantidades monetarias, NUNCA dólares ($)."
        
        # Generate AI response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enhanced_query}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        execution_time = int((time.time() - start_time) * 1000)
        
        # Log the voice query
        voice_query = models.VoiceQuery(
            ChatSession_id=chat_session.idChatSession,
            Usuario_id=user_id,
            audio_transcription=query,  # In this case, it's already transcribed
            user_query=query,
            ai_response=ai_response,
            query_type=query_type,
            execution_time_ms=execution_time,
            success=True
        )
        db.add(voice_query)
        
        # Update chat session
        chat_session.total_queries += 1
        db.commit()
        
        return {
            "success": True,
            "query": query,
            "response": ai_response,
            "query_type": query_type,
            "session_id": chat_session.idChatSession,
            "execution_time_ms": execution_time
        }
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        
        # Log failed query
        try:
            voice_query = models.VoiceQuery(
                ChatSession_id=session_id,
                Usuario_id=user_id,
                audio_transcription=query,
                user_query=query,
                ai_response="",
                query_type=query_type,
                execution_time_ms=execution_time,
                success=False,
                error_message=str(e)
            )
            db.add(voice_query)
            db.commit()
        except:
            pass  # Don't fail on logging failure
        
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")

@router.post("/chat")
async def voice_chat_complete(
    audio_file: UploadFile = File(...),
    user_id: int = Form(...),
    session_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Complete voice chat workflow: audio → transcription → AI response"""
    
    try:
        # Step 1: Transcribe audio
        transcription_result = await transcribe_audio(audio_file, user_id, db)
        
        if not transcription_result["success"]:
            return transcription_result
        
        transcribed_text = transcription_result["transcription"]
        
        # Step 2: Process query
        query_result = await process_voice_query(transcribed_text, user_id, session_id, db)
        
        # Combine results
        return {
            "success": True,
            "transcription": transcribed_text,
            "transcription_time_ms": transcription_result["execution_time_ms"],
            "query": transcribed_text,
            "response": query_result["response"],
            "query_type": query_result["query_type"],
            "session_id": query_result["session_id"],
            "total_time_ms": transcription_result["execution_time_ms"] + query_result["execution_time_ms"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en chat por voz: {str(e)}")

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: int,
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    
    try:
        # Validate session belongs to user
        session = db.query(models.ChatSession).filter(
            models.ChatSession.idChatSession == session_id,
            models.ChatSession.Usuario_id == user_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Get voice queries for this session
        queries = db.query(models.VoiceQuery).filter(
            models.VoiceQuery.ChatSession_id == session_id
        ).order_by(desc(models.VoiceQuery.fecha)).limit(limit).all()
        
        return {
            "success": True,
            "session_info": {
                "session_id": session.idChatSession,
                "start_time": session.session_start.isoformat(),
                "total_queries": session.total_queries,
                "active": session.session_active
            },
            "chat_history": [
                {
                    "query_id": q.idVoiceQuery,
                    "transcription": q.audio_transcription,
                    "query": q.user_query,
                    "response": q.ai_response,
                    "query_type": q.query_type,
                    "timestamp": q.fecha.isoformat(),
                    "execution_time_ms": q.execution_time_ms,
                    "success": q.success
                } for q in reversed(queries)  # Show oldest first
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")

@router.get("/sessions/{user_id}")
async def get_user_sessions(
    user_id: int,
    active_only: bool = False,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get chat sessions for a user"""
    
    try:
        query = db.query(models.ChatSession).filter(models.ChatSession.Usuario_id == user_id)
        
        if active_only:
            query = query.filter(models.ChatSession.session_active == True)
        
        sessions = query.order_by(desc(models.ChatSession.session_start)).limit(limit).all()
        
        return {
            "success": True,
            "sessions": [
                {
                    "session_id": s.idChatSession,
                    "start_time": s.session_start.isoformat(),
                    "end_time": s.session_end.isoformat() if s.session_end else None,
                    "total_queries": s.total_queries,
                    "active": s.session_active,
                    "duration_minutes": int((s.session_end - s.session_start).total_seconds() / 60) if s.session_end else None
                } for s in sessions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo sesiones: {str(e)}")

@router.post("/sessions/{session_id}/close")
async def close_chat_session(
    session_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Close a chat session"""
    
    try:
        session = db.query(models.ChatSession).filter(
            models.ChatSession.idChatSession == session_id,
            models.ChatSession.Usuario_id == user_id,
            models.ChatSession.session_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Sesión activa no encontrada")
        
        session.session_end = datetime.now()
        session.session_active = False
        db.commit()
        
        return {
            "success": True,
            "message": "Sesión cerrada exitosamente",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cerrando sesión: {str(e)}")