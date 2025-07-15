// AI Configuration - Real Claude API Only
const AI_CONFIG = {
    USE_REAL_AI: true,  // Always use real Claude API
    SHOW_MODE_INDICATOR: false  // Hide mode indicator since only real AI is used
};

// Timezone utility function for Lima, Peru
function getTodayInLimaTimezone() {
    // Create a date in Lima timezone using Intl.DateTimeFormat
    const now = new Date();
    const limaTime = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'America/Lima',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(now);
    return limaTime; // Returns YYYY-MM-DD format
}

document.addEventListener('DOMContentLoaded', function() {
    const userData = checkAuth();
    setupUserInterface(userData);
    loadAnalytics();
});

function setupUserInterface(userData) {
    const userWelcome = document.getElementById('userWelcome');
    const usuariosLink = document.getElementById('usuariosLink');
    const sedesLink = document.getElementById('sedesLink');
    
    if (userData.rol === 'admin') {
        userWelcome.textContent = `Bienvenido, ${userData.username}`;
        // Admin can see all navigation links
    } else {
        userWelcome.textContent = `Bienvenido, ${userData.username}`;
        // Hide admin-only features
        if (usuariosLink) usuariosLink.style.display = 'none';
    }
}

async function loadAnalytics() {
    try {
        // Load all analytics data in parallel
        await Promise.all([
            loadSalesToday(),
            loadProductsSold(),
            loadLowStock(),
            loadTemperatureStatus(),
            loadTopProducts(),
            loadSedesPerformance(),
            loadRecentActivity(),
            loadAIInsights()  // Add AI insights
        ]);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

async function loadSalesToday() {
    try {
        const response = await fetch(`${API_URL}/movimientos/?limit=1000`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Get today's date in Lima timezone (Peru) in YYYY-MM-DD format
        const today = getTodayInLimaTimezone();
        console.log('📅 Today\'s date (Lima timezone):', today);
        
        // Filter sales from today
        const todaySales = data.movements.filter(mov => {
            const movDate = mov.fecha.split('T')[0];
            return movDate === today && mov.tipo === 'venta';
        });
        
        const totalSales = todaySales.reduce((sum, mov) => sum + (mov.Cantidad * mov.Precio), 0);
        const salesCount = todaySales.length;
        
        if (salesCount === 0) {
            document.getElementById('salesTodayValue').textContent = 'S/.0.00';
            document.getElementById('salesTodayChange').textContent = 'Sin ventas hoy';
        } else {
            document.getElementById('salesTodayValue').textContent = `S/.${totalSales.toFixed(2)}`;
            document.getElementById('salesTodayChange').textContent = `${salesCount} transacciones hoy`;
        }
        
    } catch (error) {
        document.getElementById('salesTodayValue').textContent = 'Error';
        console.error('❌ Error loading sales data:', error);
    }
}

async function loadProductsSold() {
    try {
        const response = await fetch(`${API_URL}/movimientos/?limit=1000`);
        const data = await response.json();
        
        // Get today's date in Lima timezone (Peru) in YYYY-MM-DD format
        const today = getTodayInLimaTimezone();
        
        // Count products sold today
        const todaySales = data.movements.filter(mov => {
            const movDate = mov.fecha.split('T')[0];
            return movDate === today && mov.tipo === 'venta';
        });
        
        const totalProducts = todaySales.reduce((sum, mov) => sum + mov.Cantidad, 0);
        
        if (totalProducts === 0) {
            document.getElementById('productsSoldValue').textContent = '0';
            document.getElementById('productsSoldChange').textContent = 'Sin productos vendidos hoy';
        } else {
            document.getElementById('productsSoldValue').textContent = Math.round(totalProducts);
            document.getElementById('productsSoldChange').textContent = `unidades vendidas hoy`;
        }
        
    } catch (error) {
        document.getElementById('productsSoldValue').textContent = 'Error';
        console.error('Error loading products sold:', error);
    }
}

async function loadLowStock() {
    try {
        const response = await fetch(`${API_URL}/productos/?limit=1000`);
        const productosData = await response.json();
        
        // Handle both old format (array) and new format (object with pagination)
        const productos = productosData.productos || productosData;
        
        // Filter products with low stock (less than 10)
        const lowStockProducts = productos.filter(p => p.Stock < 10);
        
        document.getElementById('lowStockValue').textContent = lowStockProducts.length;
        
        if (lowStockProducts.length > 0) {
            document.getElementById('lowStockChange').textContent = 'Requieren reabastecimiento';
            document.querySelector('.low-stock').classList.add('alert');
        } else {
            document.getElementById('lowStockChange').textContent = 'Stock en buen estado';
        }
        
    } catch (error) {
        document.getElementById('lowStockValue').textContent = 'Error';
        console.error('Error loading stock data:', error);
    }
}

async function loadTemperatureStatus() {
    try {
        const response = await fetch(`${API_URL}/temperatura/?limit=20`);
        const data = await response.json();
        
        // Handle both old format (array) and new format (object with pagination)
        const temperaturas = data.temperatures || data;
        
        if (temperaturas.length > 0) {
            // Get last 10 readings for average
            const recentTemps = temperaturas.slice(0, 10);
            const avgTemp = recentTemps.reduce((sum, t) => sum + t.Temperatura, 0) / recentTemps.length;
            
            document.getElementById('temperatureValue').textContent = `${avgTemp.toFixed(1)}°C`;
            
            // Status based on temperature
            if (avgTemp < 18) {
                document.getElementById('temperatureStatus').textContent = 'Muy fría';
                document.querySelector('.temperature-status').classList.add('cold');
            } else if (avgTemp > 28) {
                document.getElementById('temperatureStatus').textContent = 'Muy caliente';
                document.querySelector('.temperature-status').classList.add('hot');
            } else {
                document.getElementById('temperatureStatus').textContent = 'Óptima';
                document.querySelector('.temperature-status').classList.add('optimal');
            }
        } else {
            document.getElementById('temperatureValue').textContent = 'Sin datos';
            document.getElementById('temperatureStatus').textContent = 'No disponible';
        }
        
    } catch (error) {
        document.getElementById('temperatureValue').textContent = 'Error';
        console.error('Error loading temperature data:', error);
    }
}

async function loadTopProducts() {
    try {
        const [movimientosResponse, productosResponse, sedesResponse] = await Promise.all([
            fetch(`${API_URL}/movimientos/?limit=1000`),
            fetch(`${API_URL}/productos/?limit=1000`),
            fetch(`${API_URL}/sedes/`)
        ]);
        
        const movimientosData = await movimientosResponse.json();
        const productosData = await productosResponse.json();
        const sedes = await sedesResponse.json();
        
        // Handle both old and new API formats
        const movimientos = { movements: movimientosData.movements || movimientosData };
        const productos = productosData.productos || productosData;
        
        // Get today's date in Lima timezone (Peru) in YYYY-MM-DD format
        const today = getTodayInLimaTimezone();
        
        // Filter today's sales
        const todaySales = movimientos.movements.filter(mov => {
            const movDate = mov.fecha.split('T')[0];
            return movDate === today && mov.tipo === 'venta';
        });
        
        // Count sales by product AND sede combination
        const productSales = {};
        todaySales.forEach(mov => {
            const key = `${mov.producto_id}-${mov.sede_id}`;
            if (!productSales[key]) {
                productSales[key] = {
                    producto_id: mov.producto_id,
                    sede_id: mov.sede_id,
                    cantidad: 0
                };
            }
            productSales[key].cantidad += mov.Cantidad;
        });
        
        // Get top 5 products
        const sortedProducts = Object.values(productSales)
            .sort((a, b) => b.cantidad - a.cantidad)
            .slice(0, 5);
        
        // Create products and sedes maps
        const productosMap = {};
        productos.forEach(p => {
            productosMap[p.idProductos] = { nombre: p.Nombre, sede_id: p.Sede_id };
        });
        
        const sedesMap = {};
        sedes.forEach(s => {
            sedesMap[s.idSedes] = s.Nombre;
        });
        
        const container = document.getElementById('topProductsToday');
        if (sortedProducts.length > 0) {
            container.innerHTML = sortedProducts.map((product, index) => {
                const productInfo = productosMap[product.producto_id];
                const productName = productInfo ? productInfo.nombre : `Producto ${product.producto_id}`;
                const sedeName = sedesMap[product.sede_id] || `Sede ${product.sede_id}`;
                
                return `
                    <div class="top-product-item">
                        <span class="rank">${index + 1}.</span>
                        <span class="product-name">${productName}</span>
                        <span class="sede-name">(${sedeName})</span>
                        <span class="quantity">${Math.round(product.cantidad)} vendidos</span>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<div class="no-data">Sin ventas registradas hoy</div>';
        }
        
    } catch (error) {
        document.getElementById('topProductsToday').innerHTML = '<div class="error">Error cargando datos</div>';
        console.error('Error loading top products:', error);
    }
}

async function loadSedesPerformance() {
    try {
        const [movimientosResponse, sedesResponse] = await Promise.all([
            fetch(`${API_URL}/movimientos/?limit=1000`),
            fetch(`${API_URL}/sedes/`)
        ]);
        
        const movimientosData = await movimientosResponse.json();
        const sedes = await sedesResponse.json();
        
        // Handle both old and new API formats
        const movimientos = { movements: movimientosData.movements || movimientosData };
        
        // Calculate sales by sede
        const sedesSales = {};
        movimientos.movements.filter(mov => mov.tipo === 'venta').forEach(mov => {
            if (!sedesSales[mov.sede_id]) {
                sedesSales[mov.sede_id] = { total: 0, count: 0 };
            }
            sedesSales[mov.sede_id].total += mov.Cantidad * mov.Precio;
            sedesSales[mov.sede_id].count += 1;
        });
        
        // Create sedes map
        const sedesMap = {};
        sedes.forEach(s => {
            sedesMap[s.idSedes] = s.Nombre;
        });
        
        // Sort by performance
        const sortedSedes = Object.entries(sedesSales)
            .sort(([,a], [,b]) => b.total - a.total)
            .slice(0, 5);
        
        const container = document.getElementById('sedesPerformance');
        if (sortedSedes.length > 0) {
            container.innerHTML = sortedSedes.map(([sedeId, data], index) => `
                <div class="sede-performance-item">
                    <span class="rank">${index + 1}.</span>
                    <span class="sede-name">${sedesMap[sedeId] || `Sede ${sedeId}`}</span>
                    <span class="performance">S/.${data.total.toFixed(0)} (${data.count} ventas)</span>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="no-data">Sin datos de performance</div>';
        }
        
    } catch (error) {
        document.getElementById('sedesPerformance').innerHTML = '<div class="error">Error cargando datos</div>';
        console.error('Error loading sedes performance:', error);
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch(`${API_URL}/movimientos/?limit=5`);
        const movimientosData = await response.json();
        
        // Get product and sede names
        const [productosResponse, sedesResponse] = await Promise.all([
            fetch(`${API_URL}/productos/?limit=1000`),
            fetch(`${API_URL}/sedes/`)
        ]);
        
        const productosData = await productosResponse.json();
        const sedes = await sedesResponse.json();
        
        // Handle both old and new API formats
        const data = { movements: movimientosData.movements || movimientosData };
        const productos = productosData.productos || productosData;
        
        // Create lookup maps
        const productosMap = {};
        productos.forEach(p => {
            productosMap[p.idProductos] = p.Nombre;
        });
        
        const sedesMap = {};
        sedes.forEach(s => {
            sedesMap[s.idSedes] = s.Nombre;
        });
        
        const container = document.getElementById('recentActivity');
        if (data.movements && data.movements.length > 0) {
            container.innerHTML = data.movements.map(mov => {
                const timeAgo = getTimeAgo(new Date(mov.fecha));
                const productName = productosMap[mov.producto_id] || `Producto ${mov.producto_id}`;
                const sedeName = sedesMap[mov.sede_id] || `Sede ${mov.sede_id}`;
                
                return `
                    <div class="activity-item">
                        <span class="activity-type ${mov.tipo}">${mov.tipo}</span>
                        <span class="activity-desc">${productName} en ${sedeName}</span>
                        <span class="activity-time">${timeAgo}</span>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<div class="no-data">Sin actividad reciente</div>';
        }
        
    } catch (error) {
        document.getElementById('recentActivity').innerHTML = '<div class="error">Error cargando actividad</div>';
        console.error('Error loading recent activity:', error);
    }
}

function getTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Hace unos segundos';
    if (diffInSeconds < 3600) return `Hace ${Math.floor(diffInSeconds / 60)} min`;
    if (diffInSeconds < 86400) return `Hace ${Math.floor(diffInSeconds / 3600)} h`;
    return `Hace ${Math.floor(diffInSeconds / 86400)} días`;
}

async function loadAIInsights() {
    try {
        // Update AI section to show loading
        const aiSection = document.querySelector('.ai-section .ai-placeholder');
        if (aiSection) {
            aiSection.innerHTML = `
                <div class="ai-icon">🤖</div>
                <h3>Análisis con IA</h3>
                <p>Generando insights inteligentes...</p>
                <div class="ai-loading">
                    <div class="loading-spinner"></div>
                    <span>Analizando datos con Claude AI...</span>
                </div>
            `;
        }

        // Use real Claude API
        console.log('🤖 USING CLAUDE AI - Generating business insights...');
        await loadRealAIInsights();
        
    } catch (error) {
        console.error('Error loading AI insights:', error);
        showAIError("Error de conexión con el servicio de IA");
    }
}

async function loadRealAIInsights() {
    try {
        const response = await fetch(`${API_URL}/ai/business-insights?days=7`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.ai_insights) {
                updateAISection(data.ai_insights, data.data);
            } else {
                showAIError("No se pudieron generar insights inteligentes");
            }
        } else {
            const error = await response.text();
            console.error('AI API error:', error);
            
            if (response.status === 500 && error.includes("CLAUDE_API_KEY")) {
                showAISetupInstructions();
            } else {
                showAIError("Error conectando con el servicio de IA");
            }
        }
    } catch (error) {
        throw error;
    }
}


function updateAISection(aiInsights, businessData) {
    const aiSection = document.querySelector('.ai-section .ai-placeholder');
    if (!aiSection) return;
    
    // Format AI insights for display
    const formattedInsights = formatAIInsights(aiInsights);
    
    aiSection.innerHTML = `
        <div class="ai-icon">🤖</div>
        <h3>Insights Inteligentes</h3>
        <div class="ai-insights-content">
            ${formattedInsights}
        </div>
        <div class="ai-metadata">
            <small>🎯 Análisis basado en ${businessData.resumen_ventas?.total_transacciones || 0} transacciones de los últimos 7 días</small>
        </div>
        <button class="refresh-ai-btn" onclick="loadAIInsights()">🔄 Actualizar Análisis</button>
    `;
}

function formatAIInsights(insights) {
    // Basic formatting for AI response
    const lines = insights.split('\n').filter(line => line.trim());
    let formattedContent = '';
    
    for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine) continue;
        
        // Handle headers (lines that are all caps or start with numbers)
        if (trimmedLine.match(/^[0-9]+\./) || trimmedLine === trimmedLine.toUpperCase()) {
            formattedContent += `<h4 class="ai-section-header">${trimmedLine}</h4>`;
        } else if (trimmedLine.startsWith('-') || trimmedLine.startsWith('•')) {
            formattedContent += `<div class="ai-insight-item">${trimmedLine}</div>`;
        } else {
            formattedContent += `<p class="ai-insight-text">${trimmedLine}</p>`;
        }
    }
    
    return formattedContent || '<p>Análisis completado sin insights específicos.</p>';
}

function showAIError(message) {
    const aiSection = document.querySelector('.ai-section .ai-placeholder');
    if (aiSection) {
        aiSection.innerHTML = `
            <div class="ai-icon">⚠️</div>
            <h3>Análisis con IA</h3>
            <p class="ai-error">${message}</p>
            <button class="retry-ai-btn" onclick="loadAIInsights()">🔄 Reintentar</button>
        `;
    }
}

function showAISetupInstructions() {
    const aiSection = document.querySelector('.ai-section .ai-placeholder');
    if (aiSection) {
        aiSection.innerHTML = `
            <div class="ai-icon">🔧</div>
            <h3>Configuración de IA Requerida</h3>
            <div class="ai-setup-instructions">
                <p>Para activar los insights inteligentes, configura tu API key de Claude:</p>
                <ol>
                    <li>Obtén una API key de <a href="https://console.anthropic.com/" target="_blank">Anthropic Claude</a></li>
                    <li>Agrega la variable de entorno: <code>CLAUDE_API_KEY=tu_api_key</code></li>
                    <li>Reinicia el servidor backend</li>
                </ol>
                <p><small>Una vez configurado, tendrás acceso a análisis inteligentes automáticos de tus datos de negocio.</small></p>
            </div>
        `;
    }
}

