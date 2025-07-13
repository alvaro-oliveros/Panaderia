# Docker Data Generation Guide

## Business Data Generation in Docker Container

The Docker container includes the `generate_business_data.py` script for populating the database with realistic test data.

### Usage

After starting the Docker container, you can generate business data:

```bash
# Start the container
docker-compose up -d

# Generate business data
docker-compose exec bakery-app python /app/generate_business_data.py
```

### What Gets Generated

- **5 bakery locations** (sedes) with realistic addresses
- **185+ products** across different categories (Pan, Pastelería, Tortas, Ingredientes, Bebidas)
- **25,000+ historical movements** covering 6 months of sales data
- **Realistic patterns** including weekends, holidays, and seasonal variations

### Generated Data Structure

- **Sedes**: Panadería Centro, Norte, Sur, Residencial, Plaza
- **Products per sede**: ~37 products each with proper pricing and stock levels
- **Movement types**: ventas, reabastecimiento, ajuste, entrada
- **Time range**: 180 days of historical data

### Access the Data

After generation, access your data through:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/docs
- **Direct endpoints**: /sedes/, /productos/, /movimientos/

### Notes

- The script takes ~3-5 minutes to complete
- Data is persisted in the Docker volume
- Safe to run multiple times (will create additional data)
- Perfect for AI analytics and dashboard demonstrations

### Example Output

```
🍞 Generador de Datos de Negocio - Sistema de Panadería
============================================================
✅ API conectada correctamente
🏢 Creando sedes... ✅ 5 sedes creadas
🥖 Creando productos... ✅ 185 productos creados
📊 Generando movimientos... ✅ 25,266 movimientos creados
⏱️ Tiempo total: 203.2 segundos
```

This makes your Docker container a complete, self-contained bakery management system with rich test data!