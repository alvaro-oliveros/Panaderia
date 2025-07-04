document.addEventListener('DOMContentLoaded', function() {
    const userData = checkAuth();
    if (!userData) return;

    document.getElementById('userWelcome').textContent = `Bienvenido, ${userData.username}`;
    
    cargarSensores();
    cargarHumedades();

    document.getElementById('formHumedad').addEventListener('submit', agregarHumedad);
    document.getElementById('formEditarHumedad').addEventListener('submit', actualizarHumedad);
    
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
        const editSelectSensor = document.getElementById('editSensorId');
        const filtroSensor = document.getElementById('filtroSensor');
        
        selectSensor.innerHTML = '<option value="">Seleccionar sensor</option>';
        editSelectSensor.innerHTML = '<option value="">Seleccionar sensor</option>';
        filtroSensor.innerHTML = '<option value="">Todos los sensores</option>';
        
        sensores.forEach(sensor => {
            const option = `<option value="${sensor.idSensores}">${sensor.nombre} (${sensor.descripcion})</option>`;
            selectSensor.innerHTML += option;
            editSelectSensor.innerHTML += option;
            filtroSensor.innerHTML += option;
        });
    } catch (error) {
        console.error('Error al cargar sensores:', error);
    }
}

function getHumidityStatus(humidity) {
    if (humidity < 40) {
        return { status: 'Muy Baja', class: 'humidity-very-low' };
    } else if (humidity < 50) {
        return { status: 'Baja', class: 'humidity-low' };
    } else if (humidity <= 65) {
        return { status: 'Óptima', class: 'humidity-optimal' };
    } else if (humidity <= 75) {
        return { status: 'Alta', class: 'humidity-high' };
    } else {
        return { status: 'Muy Alta', class: 'humidity-very-high' };
    }
}

async function cargarHumedades() {
    try {
        const userData = checkAuth();
        let url = `${API_URL}/humedad/`;
        
        if (userData.userType !== 'admin') {
            url += `?user_id=${userData.userId}`;
        }
        
        const response = await fetch(url);
        const humedades = await response.json();
        
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
                        <button onclick="editarHumedad(${hum.idHumedad})" class="edit-btn">Editar</button>
                        <button onclick="eliminarHumedad(${hum.idHumedad})" class="delete-btn">Eliminar</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (error) {
        console.error('Error al cargar humedades:', error);
        alert('Error al cargar las humedades');
    }
}

async function aplicarFiltros() {
    try {
        const userData = checkAuth();
        const sensorId = document.getElementById('filtroSensor').value;
        
        let url = `${API_URL}/humedad/`;
        const params = new URLSearchParams();
        
        if (userData.userType !== 'admin') {
            params.append('user_id', userData.userId);
        }
        
        if (sensorId) {
            params.append('sensor_id', sensorId);
        }
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const humedades = await response.json();
        
        // Actualizar tabla con datos filtrados
        mostrarHumedades(humedades);
    } catch (error) {
        console.error('Error al aplicar filtros:', error);
        alert('Error al aplicar filtros');
    }
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
                    <button onclick="editarHumedad(${hum.idHumedad})" class="edit-btn">Editar</button>
                    <button onclick="eliminarHumedad(${hum.idHumedad})" class="delete-btn">Eliminar</button>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

async function agregarHumedad(event) {
    event.preventDefault();
    
    const humedadData = {
        Humedad: parseFloat(document.getElementById('humedad').value),
        Sensor_id: parseInt(document.getElementById('sensor_id').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/humedad/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(humedadData)
        });
        
        if (response.ok) {
            alert('Humedad registrada correctamente');
            document.getElementById('formHumedad').reset();
            cargarHumedades();
        } else {
            const error = await response.json();
            alert('Error al registrar humedad: ' + (error.detail || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al registrar humedad');
    }
}

async function editarHumedad(id) {
    try {
        const response = await fetch(`${API_URL}/humedad/${id}`);
        const humedad = await response.json();
        
        document.getElementById('editId').value = humedad.idHumedad;
        document.getElementById('editHumedad').value = humedad.Humedad;
        document.getElementById('editSensorId').value = humedad.Sensor_id;
        
        const modal = document.getElementById('modalEditar');
        modal.style.display = 'flex';
        modal.classList.add('show');
    } catch (error) {
        console.error('Error al cargar humedad:', error);
        alert('Error al cargar datos de humedad');
    }
}

async function actualizarHumedad(event) {
    event.preventDefault();
    
    const id = document.getElementById('editId').value;
    const humedadData = {
        Humedad: parseFloat(document.getElementById('editHumedad').value),
        Sensor_id: parseInt(document.getElementById('editSensorId').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/humedad/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(humedadData)
        });
        
        if (response.ok) {
            alert('Humedad actualizada correctamente');
            const modal = document.getElementById('modalEditar');
            modal.style.display = 'none';
            modal.classList.remove('show');
            cargarHumedades();
        } else {
            const error = await response.json();
            alert('Error al actualizar humedad: ' + (error.detail || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar humedad');
    }
}

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