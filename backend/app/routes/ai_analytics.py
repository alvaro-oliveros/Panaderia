from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import httpx

from .. import database, models

router = APIRouter(prefix="/ai", tags=["AI Analytics"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Claude API configuration
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_API_KEY = None  # Will be set via environment variable or config

def get_claude_api_key():
    """Get Claude API key from environment or return None"""
    import os
    return os.getenv("CLAUDE_API_KEY")

async def call_claude_api(prompt: str, data: Dict[str, Any]) -> str:
    """Call Claude API with business data and analysis prompt"""
    
    api_key = get_claude_api_key()
    if not api_key:
        return "Claude API key no configurada. Agrega CLAUDE_API_KEY como variable de entorno."
    
    # Prepare the complete prompt with data
    full_prompt = f"""
Eres un analista de negocio experto especializado en panaderías. Analiza los siguientes datos de negocio y proporciona insights útiles y accionables.

DATOS DEL NEGOCIO:
{json.dumps(data, indent=2, ensure_ascii=False)}

INSTRUCCIONES:
{prompt}

Responde en español con insights específicos, recomendaciones prácticas y observaciones relevantes para el negocio de panadería. Sé conciso pero informativo.
"""

    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(CLAUDE_API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                return f"Error API Claude: {response.status_code} - {response.text}"
                
    except Exception as e:
        return f"Error conexión Claude API: {str(e)}"

def get_business_summary_data(db: Session, days_back: int = 7) -> Dict[str, Any]:
    """Get comprehensive business data for AI analysis"""
    
    # Date range for analysis
    start_date = datetime.now() - timedelta(days=days_back)
    
    # 1. Sales summary
    sales_movements = db.query(models.Movimiento).filter(
        models.Movimiento.tipo == "venta",
        models.Movimiento.fecha >= start_date
    ).all()
    
    total_sales = sum(mov.Cantidad * mov.Precio for mov in sales_movements)
    total_transactions = len(sales_movements)
    
    # 2. Top products by sales
    product_sales = {}
    for mov in sales_movements:
        if mov.producto_id not in product_sales:
            product_sales[mov.producto_id] = {"quantity": 0, "revenue": 0}
        product_sales[mov.producto_id]["quantity"] += mov.Cantidad
        product_sales[mov.producto_id]["revenue"] += mov.Cantidad * mov.Precio
    
    # Get product names
    productos = db.query(models.Producto).all()
    productos_map = {p.idProductos: {"nombre": p.Nombre, "precio": p.Precio, "stock": p.Stock, "categoria": p.Categoria} for p in productos}
    
    # Add product names to sales data
    for prod_id, sales_data in product_sales.items():
        if prod_id in productos_map:
            sales_data["nombre"] = productos_map[prod_id]["nombre"]
            sales_data["categoria"] = productos_map[prod_id]["categoria"]
    
    # Top 10 products by revenue
    top_products = sorted(product_sales.items(), key=lambda x: x[1]["revenue"], reverse=True)[:10]
    
    # 3. Performance by sede
    sedes = db.query(models.Sede).all()
    sedes_map = {s.idSedes: s.Nombre for s in sedes}
    
    sede_performance = {}
    for mov in sales_movements:
        if mov.sede_id not in sede_performance:
            sede_performance[mov.sede_id] = {"revenue": 0, "transactions": 0}
        sede_performance[mov.sede_id]["revenue"] += mov.Cantidad * mov.Precio
        sede_performance[mov.sede_id]["transactions"] += 1
    
    # Add sede names
    for sede_id, perf_data in sede_performance.items():
        if sede_id in sedes_map:
            perf_data["nombre"] = sedes_map[sede_id]
    
    # 4. Low stock products with sede information
    low_stock_products = db.query(models.Producto).filter(models.Producto.Stock < 10).all()
    low_stock_info = []
    for p in low_stock_products:
        sede_name = sedes_map.get(p.Sede_id, f"Sede {p.Sede_id}")
        low_stock_info.append({
            "nombre": p.Nombre,
            "stock_actual": p.Stock,
            "categoria": p.Categoria,
            "precio": p.Precio,
            "sede_id": p.Sede_id,
            "sede_nombre": sede_name
        })
    
    # 5. Recent temperature/humidity data
    recent_temps = db.query(models.Temperatura).order_by(desc(models.Temperatura.fecha)).limit(20).all()
    recent_humidity = db.query(models.Humedad).order_by(desc(models.Humedad.fecha)).limit(20).all()
    
    avg_temp = sum(t.Temperatura for t in recent_temps) / len(recent_temps) if recent_temps else 0
    avg_humidity = sum(h.Humedad for h in recent_humidity) / len(recent_humidity) if recent_humidity else 0
    
    # 6. Movement patterns
    movement_types = {}
    all_movements = db.query(models.Movimiento).filter(models.Movimiento.fecha >= start_date).all()
    for mov in all_movements:
        if mov.tipo not in movement_types:
            movement_types[mov.tipo] = 0
        movement_types[mov.tipo] += 1
    
    return {
        "periodo_analisis": f"Últimos {days_back} días",
        "resumen_ventas": {
            "total_ingresos": round(total_sales, 2),
            "total_transacciones": total_transactions,
            "ingreso_promedio_transaccion": round(total_sales / total_transactions if total_transactions > 0 else 0, 2)
        },
        "productos_top": [
            {
                "producto_id": prod_id,
                "nombre": data.get("nombre", f"Producto {prod_id}"),
                "categoria": data.get("categoria", "Sin categoría"),
                "cantidad_vendida": round(data["quantity"], 2),
                "ingresos": round(data["revenue"], 2)
            } for prod_id, data in top_products
        ],
        "performance_sedes": [
            {
                "sede_id": sede_id,
                "nombre": data.get("nombre", f"Sede {sede_id}"),
                "ingresos": round(data["revenue"], 2),
                "transacciones": data["transactions"],
                "ingreso_promedio": round(data["revenue"] / data["transactions"] if data["transactions"] > 0 else 0, 2)
            } for sede_id, data in sede_performance.items()
        ],
        "productos_stock_bajo": low_stock_info,
        "condiciones_ambientales": {
            "temperatura_promedio": round(avg_temp, 1),
            "humedad_promedio": round(avg_humidity, 1),
            "lecturas_temperatura": len(recent_temps),
            "lecturas_humedad": len(recent_humidity)
        },
        "tipos_movimiento": movement_types,
        "total_productos": len(productos),
        "total_sedes": len(sedes)
    }

@router.get("/business-insights")
async def get_business_insights(days: int = 7, db: Session = Depends(get_db)):
    """Get AI-powered business insights"""
    
    try:
        # Get business data
        business_data = get_business_summary_data(db, days)
        
        # Prepare AI prompt
        prompt = """
        Analiza estos datos de panadería y proporciona:
        
        1. INSIGHTS PRINCIPALES (3-4 puntos clave sobre el rendimiento)
        2. RECOMENDACIONES ESPECÍFICAS (mejoras operativas concretas)
        3. ALERTAS (problemas que requieren atención inmediata)
        4. OPORTUNIDADES (áreas de crecimiento o optimización)
        
        IMPORTANTE: Cuando menciones productos con stock bajo, SIEMPRE incluye el nombre de la sede donde se encuentra cada producto.
        Por ejemplo: "Torta de Chocolate: 8 unidades en Panadería Centro" en lugar de solo "Torta de Chocolate: 8 unidades".
        
        Enfócate en aspectos prácticos como gestión de inventario, rendimiento por ubicación, productos populares, y condiciones de almacenamiento.
        """
        
        # Call Claude API
        ai_response = await call_claude_api(prompt, business_data)
        
        return {
            "success": True,
            "data": business_data,
            "ai_insights": ai_response,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando insights: {str(e)}")

@router.get("/product-analysis/{product_id}")
async def get_product_analysis(product_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get AI analysis for a specific product"""
    
    try:
        # Get product info
        product = db.query(models.Producto).filter(models.Producto.idProductos == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Get product movements
        start_date = datetime.now() - timedelta(days=days)
        movements = db.query(models.Movimiento).filter(
            models.Movimiento.producto_id == product_id,
            models.Movimiento.fecha >= start_date
        ).order_by(desc(models.Movimiento.fecha)).all()
        
        # Prepare product data
        product_data = {
            "producto": {
                "id": product.idProductos,
                "nombre": product.Nombre,
                "precio": product.Precio,
                "stock_actual": product.Stock,
                "categoria": product.Categoria,
                "descripcion": product.Descripcion
            },
            "movimientos_recientes": [
                {
                    "tipo": mov.tipo,
                    "cantidad": mov.Cantidad,
                    "precio": mov.Precio,
                    "fecha": mov.fecha.isoformat(),
                    "sede_id": mov.sede_id
                } for mov in movements[:50]  # Last 50 movements
            ],
            "resumen_periodo": {
                "total_movimientos": len(movements),
                "ventas_cantidad": sum(mov.Cantidad for mov in movements if mov.tipo == "venta"),
                "ingresos_ventas": sum(mov.Cantidad * mov.Precio for mov in movements if mov.tipo == "venta")
            }
        }
        
        # AI prompt for product analysis
        prompt = f"""
        Analiza el rendimiento del producto "{product.Nombre}" y proporciona:
        
        1. ANÁLISIS DE VENTAS (tendencias, velocidad de rotación)
        2. GESTIÓN DE INVENTARIO (recomendaciones de stock)
        3. PRICING INSIGHTS (análisis de precios y márgenes)
        4. RECOMENDACIONES (optimizaciones específicas para este producto)
        
        Considera el stock actual, patrones de venta, y movimientos recientes.
        """
        
        ai_response = await call_claude_api(prompt, product_data)
        
        return {
            "success": True,
            "product_data": product_data,
            "ai_analysis": ai_response,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis de producto: {str(e)}")

@router.get("/daily-summary")
async def get_daily_summary(db: Session = Depends(get_db)):
    """Get AI-powered daily business summary"""
    
    try:
        # Get today's data
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Today's movements
        today_movements = db.query(models.Movimiento).filter(
            models.Movimiento.fecha >= today_start
        ).all()
        
        # Sales summary
        today_sales = [mov for mov in today_movements if mov.tipo == "venta"]
        total_revenue = sum(mov.Cantidad * mov.Precio for mov in today_sales)
        total_items_sold = sum(mov.Cantidad for mov in today_sales)
        
        # Get product and sede names for context
        productos = db.query(models.Producto).all()
        sedes = db.query(models.Sede).all()
        
        daily_data = {
            "fecha": today.isoformat(),
            "resumen_ventas": {
                "ingresos_totales": round(total_revenue, 2),
                "productos_vendidos": round(total_items_sold, 2),
                "transacciones": len(today_sales)
            },
            "actividad_por_tipo": {
                mov_type: len([m for m in today_movements if m.tipo == mov_type])
                for mov_type in ["venta", "reabastecimiento", "ajuste", "agregado", "entrada"]
            },
            "productos_activos": len(productos),
            "sedes_operando": len(sedes)
        }
        
        prompt = """
        Genera un resumen ejecutivo del día actual enfocándose en:
        
        1. RENDIMIENTO DEL DÍA (logros y métricas clave)
        2. ESTADO OPERATIVO (actividad general del negocio)
        3. PUNTOS DE ATENCIÓN (si hay algo que requiere seguimiento)
        4. PREPARACIÓN PARA MAÑANA (recomendaciones para el próximo día)
        
        Mantén un tono profesional pero accesible, como si fuera un reporte para el gerente de la panadería.
        """
        
        ai_response = await call_claude_api(prompt, daily_data)
        
        return {
            "success": True,
            "daily_data": daily_data,
            "ai_summary": ai_response,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando resumen diario: {str(e)}")