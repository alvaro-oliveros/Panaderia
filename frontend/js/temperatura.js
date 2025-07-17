// Pagination state
let currentPage = 0;
let itemsPerPage = 50;
let currentFilters = {};

document.addEventListener('DOMContentLoaded', function() {
    const userData = checkAuth();
    if (!userData) return;

    document.getElementById('userWelcome').textContent = `Bienvenido, ${userData.username}`;
    
    cargarSensores();
    cargarTemperaturas();

    document.getElementById('formTemperatura').addEventListener('submit', agregarTemperatura);
    document.getElementById('formEditarTemperatura').addEventListener('submit', actualizarTemperatura);
    
    // Modal handling
    const modal = document.getElementById('modalEditar');
    const closeBtn = document.getElementsByClassName('close')[0];
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
        }
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
        
        const selectSensor = document.getElementById('sensor_id');
        const filtroSensor = document.getElementById('filtroSensor');
        const editSelectSensor = document.getElementById('editSensorId');
        
        selectSensor.innerHTML = '<option value="">Seleccionar sensor</option>';
        filtroSensor.innerHTML = '<option value="">Todos los sensores</option>';
        editSelectSensor.innerHTML = '<option value="">Seleccionar sensor</option>';
        
        sensores.forEach(sensor => {
            const option = `<option value="${sensor.idSensores}">${sensor.nombre} (${sensor.descripcion})</option>`;
            selectSensor.innerHTML += option;
            filtroSensor.innerHTML += option;
            editSelectSensor.innerHTML += option;
        });
    } catch (error) {
        console.error('Error al cargar sensores:', error);
    }
}

async function cargarTemperaturas() {
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
        
        const url = `${API_URL}/temperatura/?${params.toString()}`;
        const response = await fetch(url);
        const data = await response.json();
        
        // Handle both old format (array) and new format (object with pagination)
        const temperaturas = data.temperatures || data;
        const total = data.total || (temperaturas ? temperaturas.length : 0);
        const hasMore = data.has_more || false;
        
        // Ensure temperaturas is an array
        if (!Array.isArray(temperaturas)) {
            console.error('Temperaturas is not an array:', temperaturas);
            return;
        }
        
        // Cargar datos de sensores y sedes para mostrar nombres
        const sensoresResponse = await fetch(`${API_URL}/sensores/`);
        const sensores = await sensoresResponse.json();
        const sensoresMap = {};
        if (Array.isArray(sensores)) {
            sensores.forEach(sensor => {
                sensoresMap[sensor.idSensores] = sensor;
            });
        }
        
        const sedesResponse = await fetch(`${API_URL}/sedes/`);
        const sedes = await sedesResponse.json();
        const sedesMap = {};
        if (Array.isArray(sedes)) {
            sedes.forEach(sede => {
                sedesMap[sede.idSedes] = sede.Nombre;
            });
        }
        
        const tbody = document.querySelector('#tablaTemperaturas tbody');
        tbody.innerHTML = '';
        
        temperaturas.forEach(temp => {
            const sensor = sensoresMap[temp.Sensor_id];
            const nombreSede = sensor ? sedesMap[sensor.sede_id] : 'N/A';
            const nombreSensor = sensor ? sensor.nombre : 'N/A';
            const fecha = new Date(temp.fecha).toLocaleString('es-ES');
            
            const row = `
                <tr>
                    <td>${temp.idTemperatura}</td>
                    <td>${temp.Temperatura}°C</td>
                    <td>${nombreSensor}</td>
                    <td>${nombreSede}</td>
                    <td>${fecha}</td>
                    <td>
                        <button onclick="editarTemperatura(${temp.idTemperatura})" class="edit-btn">Editar</button>
                        <button onclick="eliminarTemperatura(${temp.idTemperatura})" class="delete-btn">Eliminar</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
        
        // Update pagination controls
        updatePaginationControls(total, hasMore);
        
    } catch (error) {
        console.error('Error al cargar temperaturas:', error);
        alert('Error al cargar las temperaturas');
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
    cargarTemperaturas();
}

async function mostrarTemperaturas(temperaturas) {
    // Cargar datos de sensores y sedes para mostrar nombres
    const sensoresResponse = await fetch(`${API_URL}/sensores/`);
    const sensores = await sensoresResponse.json();
    const sensoresMap = {};
    sensores.forEach(sensor => {
        sensoresMap[sensor.idSensores] = sensor;
    });
    
    const sedesResponse = await fetch(`${API_URL}/sedes/`);
    const sedes = await sedesResponse.json();
    const sedesMap = {};
    sedes.forEach(sede => {
        sedesMap[sede.idSedes] = sede.Nombre;
    });
    
    const tbody = document.querySelector('#tablaTemperaturas tbody');
    tbody.innerHTML = '';
    
    temperaturas.forEach(temp => {
        const sensor = sensoresMap[temp.Sensor_id];
        const nombreSede = sensor ? sedesMap[sensor.sede_id] : 'N/A';
        const nombreSensor = sensor ? sensor.nombre : 'N/A';
        const fecha = new Date(temp.fecha).toLocaleString('es-ES');
        
        const row = `
            <tr>
                <td>${temp.idTemperatura}</td>
                <td>${temp.Temperatura}°C</td>
                <td>${nombreSensor}</td>
                <td>${nombreSede}</td>
                <td>${fecha}</td>
                <td>
                    <button onclick="editarTemperatura(${temp.idTemperatura})" class="edit-btn">Editar</button>
                    <button onclick="eliminarTemperatura(${temp.idTemperatura})" class="delete-btn">Eliminar</button>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

async function agregarTemperatura(event) {
    event.preventDefault();
    
    const temperaturaData = {
        Temperatura: parseFloat(document.getElementById('temperatura').value),
        Sensor_id: parseInt(document.getElementById('sensor_id').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/temperatura/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(temperaturaData)
        });
        
        if (response.ok) {
            alert('Temperatura registrada correctamente');
            document.getElementById('formTemperatura').reset();
            cargarTemperaturas();
        } else {
            const error = await response.json();
            alert('Error al registrar temperatura: ' + (error.detail || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al registrar temperatura');
    }
}


async function editarTemperatura(id) {
    try {
        const response = await fetch(`${API_URL}/temperatura/${id}`);
        const temperatura = await response.json();
        
        document.getElementById('editId').value = temperatura.idTemperatura;
        document.getElementById('editTemperatura').value = temperatura.Temperatura;
        document.getElementById('editSensorId').value = temperatura.Sensor_id;
        
        const modal = document.getElementById('modalEditar');
        modal.style.display = 'flex';
        modal.classList.add('show');
    } catch (error) {
        console.error('Error al cargar temperatura:', error);
        alert('Error al cargar datos de la temperatura');
    }
}

async function actualizarTemperatura(event) {
    event.preventDefault();
    
    const id = document.getElementById('editId').value;
    const temperaturaData = {
        Temperatura: parseFloat(document.getElementById('editTemperatura').value),
        Sensor_id: parseInt(document.getElementById('editSensorId').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/temperatura/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(temperaturaData)
        });
        
        if (response.ok) {
            alert('Temperatura actualizada correctamente');
            const modal = document.getElementById('modalEditar');
            modal.style.display = 'none';
            modal.classList.remove('show');
            cargarTemperaturas();
        } else {
            const error = await response.json();
            alert('Error al actualizar temperatura: ' + (error.detail || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar temperatura');
    }
}

async function eliminarTemperatura(id) {
    if (confirm('¿Estás seguro de que quieres eliminar esta lectura de temperatura?')) {
        try {
            const response = await fetch(`${API_URL}/temperatura/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('Temperatura eliminada correctamente');
                cargarTemperaturas();
            } else {
                const error = await response.json();
                alert('Error al eliminar temperatura: ' + (error.detail || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar temperatura');
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
    
    const tableContainer = document.querySelector('#tablaTemperaturas').parentNode;
    tableContainer.appendChild(paginationDiv);
    
    return paginationDiv;
}

function previousPage() {
    if (currentPage > 0) {
        currentPage--;
        cargarTemperaturas();
    }
}

function nextPage() {
    currentPage++;
    cargarTemperaturas();
}

// Update the aplicarFiltros function to reset pagination
function resetPagination() {
    currentPage = 0;
}