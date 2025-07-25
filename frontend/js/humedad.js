// Pagination state
let currentPage = 0;
let itemsPerPage = 50;
let currentFilters = {};

document.addEventListener('DOMContentLoaded', function() {
    const userData = checkAuth();
    if (!userData) return;

    document.getElementById('userWelcome').textContent = `Bienvenido, ${userData.username}`;
    
    cargarSensores();
    cargarHumedades();

    // Disable manual form submission - ESP32 handles data registration
    const form = document.getElementById('formHumedad');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            alert('Los datos de humedad son registrados automáticamente por el ESP32. No se permite el registro manual.');
        });
    }
});

async function cargarSensores() {
    try {
        const userData = checkAuth();
        let url = `${API_URL}/sensores/`;
        
        if (userData.userType !== 'admin') {
            url += `?user_id=${userData.userId}`;
        }
        
        const response = await fetch(url);
        const sensores = await response.json();
        
        const filtroSensor = document.getElementById('filtroSensor');
        
        if (filtroSensor) {
            filtroSensor.innerHTML = '<option value="">Todos los sensores</option>';
            
            sensores.forEach(sensor => {
                const option = `<option value="${sensor.idSensores}">${sensor.nombre} (${sensor.descripcion})</option>`;
                filtroSensor.innerHTML += option;
            });
        }
    } catch (error) {
        console.error('Error al cargar sensores:', error);
    }
}

function getHumidityStatus(humidity) {
    if (humidity < 45) {
        return { status: 'Crítica Baja', class: 'humidity-very-low' };
    } else if (humidity < 50) {
        return { status: 'Precaución Baja', class: 'humidity-low' };
    } else if (humidity <= 70) {
        return { status: 'Óptima', class: 'humidity-optimal' };
    } else if (humidity <= 75) {
        return { status: 'Precaución Alta', class: 'humidity-high' };
    } else {
        return { status: 'Crítica Alta', class: 'humidity-very-high' };
    }
}

async function cargarHumedades() {
    try {
        const userData = checkAuth();
        const params = new URLSearchParams();
        
        if (userData.userType !== 'admin') {
            params.append('user_id', userData.userId);
        }
        
        // Add pagination parameters
        params.append('limit', itemsPerPage);
        params.append('offset', currentPage * itemsPerPage);
        
        // Add filters if any
        Object.keys(currentFilters).forEach(key => {
            if (currentFilters[key]) {
                params.append(key, currentFilters[key]);
            }
        });
        
        const url = `${API_URL}/humedad/?${params.toString()}`;
        const response = await fetch(url);
        const data = await response.json();
        
        // Handle both old format (array) and new format (object with pagination)
        const humedades = data.humidities || data;
        const total = data.total || (humedades ? humedades.length : 0);
        const hasMore = data.has_more || false;
        
        // Ensure humedades is an array
        if (!Array.isArray(humedades)) {
            console.error('Humedades is not an array:', humedades);
            return;
        }
        
        // Cargar datos de sensores y sedes para mostrar nombres
        const [sensoresResponse, sedesResponse] = await Promise.all([
            fetch(`${API_URL}/sensores/`),
            fetch(`${API_URL}/sedes/`)
        ]);
        const sensores = await sensoresResponse.json();
        const sedes = await sedesResponse.json();
        
        const sensoresMap = {};
        if (Array.isArray(sensores)) {
            sensores.forEach(sensor => {
                sensoresMap[sensor.idSensores] = sensor;
            });
        }
        
        const sedesMap = {};
        if (Array.isArray(sedes)) {
            sedes.forEach(sede => {
                sedesMap[sede.idSedes] = sede.Nombre;
            });
        }
        
        const tbody = document.querySelector('#tablaHumedades tbody');
        tbody.innerHTML = '';
        
        humedades.forEach(hum => {
            const sensor = sensoresMap[hum.Sensor_id];
            const nombreSede = sensor ? sedesMap[sensor.sede_id] : 'N/A';
            const nombreSensor = sensor ? sensor.nombre : 'N/A';
            const fecha = new Date(hum.fecha).toLocaleString('es-ES');
            const humidityInfo = getHumidityStatus(hum.Humedad);
            
            const row = `
                <tr>
                    <td>${hum.idHumedad}</td>
                    <td>${hum.Humedad}%</td>
                    <td>${nombreSensor}</td>
                    <td>${nombreSede}</td>
                    <td>${fecha}</td>
                    <td><span class="humidity-status ${humidityInfo.class}">${humidityInfo.status}</span></td>
                    <td>
                        <button onclick="eliminarHumedad(${hum.idHumedad})" class="delete-btn">Eliminar</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
        
        // Update pagination controls
        updatePaginationControls(total, hasMore);
        
    } catch (error) {
        console.error('Error al cargar humedades:', error);
        alert('Error al cargar las humedades');
    }
}

async function aplicarFiltros() {
    const sensorId = document.getElementById('filtroSensor').value;
    
    // Update current filters
    currentFilters = {};
    if (sensorId) {
        currentFilters.sensor_id = sensorId;
    }
    
    // Reset pagination when applying filters
    resetPagination();
    
    // Reload data with new filters
    cargarHumedades();
}

async function mostrarHumedades(humedades) {
    // Cargar datos de sensores y sedes para mostrar nombres
    const [sensoresResponse, sedesResponse] = await Promise.all([
        fetch(`${API_URL}/sensores/`),
        fetch(`${API_URL}/sedes/`)
    ]);
    const sensores = await sensoresResponse.json();
    const sedes = await sedesResponse.json();
    
    const sensoresMap = {};
    sensores.forEach(sensor => {
        sensoresMap[sensor.idSensores] = sensor;
    });
    
    const sedesMap = {};
    sedes.forEach(sede => {
        sedesMap[sede.idSedes] = sede.Nombre;
    });
    
    const tbody = document.querySelector('#tablaHumedades tbody');
    tbody.innerHTML = '';
    
    humedades.forEach(hum => {
        const sensor = sensoresMap[hum.Sensor_id];
        const nombreSede = sensor ? sedesMap[sensor.sede_id] : 'N/A';
        const nombreSensor = sensor ? sensor.nombre : 'N/A';
        const fecha = new Date(hum.fecha).toLocaleString('es-ES');
        const humidityInfo = getHumidityStatus(hum.Humedad);
        
        const row = `
            <tr>
                <td>${hum.idHumedad}</td>
                <td>${hum.Humedad}%</td>
                <td>${nombreSensor}</td>
                <td>${nombreSede}</td>
                <td>${fecha}</td>
                <td><span class="humidity-status ${humidityInfo.class}">${humidityInfo.status}</span></td>
                <td>
                    <button onclick="eliminarHumedad(${hum.idHumedad})" class="delete-btn">Eliminar</button>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Edit functionality removed - ESP32 handles all data registration automatically

async function eliminarHumedad(id) {
    if (confirm('¿Estás seguro de que quieres eliminar esta lectura de humedad?')) {
        try {
            const response = await fetch(`${API_URL}/humedad/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('Humedad eliminada correctamente');
                cargarHumedades();
            } else {
                const error = await response.json();
                alert('Error al eliminar humedad: ' + (error.detail || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar humedad');
        }
    }
}

function updatePaginationControls(total, hasMore) {
    const paginationDiv = document.getElementById('paginationControls') || createPaginationControls();
    
    const startItem = currentPage * itemsPerPage + 1;
    const endItem = Math.min((currentPage + 1) * itemsPerPage, total);
    
    paginationDiv.innerHTML = `
        <div class="pagination-info">
            Mostrando ${startItem} - ${endItem} de ${total} registros
        </div>
        <div class="pagination-buttons">
            <button ${currentPage === 0 ? 'disabled' : ''} onclick="previousPage()">Anterior</button>
            <span>Página ${currentPage + 1}</span>
            <button ${!hasMore ? 'disabled' : ''} onclick="nextPage()">Siguiente</button>
        </div>
    `;
}

function createPaginationControls() {
    const paginationDiv = document.createElement('div');
    paginationDiv.id = 'paginationControls';
    paginationDiv.className = 'pagination-controls';
    
    const tableContainer = document.querySelector('#tablaHumedades').parentNode;
    tableContainer.appendChild(paginationDiv);
    
    return paginationDiv;
}

function previousPage() {
    if (currentPage > 0) {
        currentPage--;
        cargarHumedades();
    }
}

function nextPage() {
    currentPage++;
    cargarHumedades();
}

function resetPagination() {
    currentPage = 0;
}