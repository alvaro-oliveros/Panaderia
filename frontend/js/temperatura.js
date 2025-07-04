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

async function cargarTemperaturas() {
    try {
        const userData = checkAuth();
        let url = `${API_URL}/temperatura/`;
        
        if (userData.userType !== 'admin') {
            url += `?user_id=${userData.userId}`;
        }
        
        const response = await fetch(url);
        const temperaturas = await response.json();
        
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
    } catch (error) {
        console.error('Error al cargar temperaturas:', error);
        alert('Error al cargar las temperaturas');
    }
}

async function aplicarFiltros() {
    try {
        const userData = checkAuth();
        const sensorId = document.getElementById('filtroSensor').value;
        
        let url = `${API_URL}/temperatura/`;
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
        const temperaturas = await response.json();
        
        // Actualizar tabla con datos filtrados
        mostrarTemperaturas(temperaturas);
    } catch (error) {
        console.error('Error al aplicar filtros:', error);
        alert('Error al aplicar filtros');
    }
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
        alert('Error al cargar datos de temperatura');
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