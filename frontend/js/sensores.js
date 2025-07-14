document.addEventListener('DOMContentLoaded', function() {
    const userData = checkAuth();
    if (!userData) return;

    document.getElementById('userWelcome').textContent = `Bienvenido, ${userData.username}`;
    
    cargarSedes();
    cargarSensores();

    document.getElementById('formSensor').addEventListener('submit', agregarSensor);
    document.getElementById('formEditarSensor').addEventListener('submit', actualizarSensor);
    
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

async function cargarSedes() {
    try {
        const userData = checkAuth();
        let url = `${API_URL}/sedes/`;
        
        if (userData.userType !== 'admin') {
            url += `?user_id=${userData.userId}`;
        }
        
        const response = await fetch(url);
        const sedes = await response.json();
        
        const selectSede = document.getElementById('sede_id');
        const editSelectSede = document.getElementById('editSedeId');
        
        selectSede.innerHTML = '<option value="">Seleccionar sede</option>';
        editSelectSede.innerHTML = '<option value="">Seleccionar sede</option>';
        
        sedes.forEach(sede => {
            const option = `<option value="${sede.idSedes}">${sede.Nombre}</option>`;
            selectSede.innerHTML += option;
            editSelectSede.innerHTML += option;
        });
    } catch (error) {
        console.error('Error al cargar sedes:', error);
    }
}

async function cargarSensores() {
    try {
        const userData = checkAuth();
        let url = `${API_URL}/sensores/`;
        
        if (userData.userType !== 'admin') {
            url += `?user_id=${userData.userId}`;
        }
        
        const response = await fetch(url);
        const sensores = await response.json();
        
        // También cargar datos de sedes para mostrar nombres
        const sedesResponse = await fetch(`${API_URL}/sedes/`);
        const sedes = await sedesResponse.json();
        const sedesMap = {};
        sedes.forEach(sede => {
            sedesMap[sede.idSedes] = sede.Nombre;
        });
        
        const tbody = document.querySelector('#tablaSensores tbody');
        tbody.innerHTML = '';
        
        sensores.forEach(sensor => {
            const row = `
                <tr>
                    <td>${sensor.idSensores}</td>
                    <td>${sensor.nombre}</td>
                    <td>${sensor.descripcion}</td>
                    <td>${sedesMap[sensor.sede_id] || 'N/A'}</td>
                    <td>
                        <button onclick="editarSensor(${sensor.idSensores})" class="edit-btn">Editar</button>
                        <button onclick="eliminarSensor(${sensor.idSensores})" class="delete-btn">Eliminar</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (error) {
        console.error('Error al cargar sensores:', error);
        alert('Error al cargar los sensores');
    }
}

async function agregarSensor(event) {
    event.preventDefault();
    
    const sensorData = {
        nombre: document.getElementById('nombre').value,
        descripcion: document.getElementById('descripcion').value,
        sede_id: parseInt(document.getElementById('sede_id').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/sensores/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(sensorData)
        });
        
        if (response.ok) {
            alert('Sensor agregado correctamente');
            document.getElementById('formSensor').reset();
            cargarSensores();
        } else {
            const error = await response.json();
            alert('Error al agregar sensor: ' + (error.detail || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al agregar sensor');
    }
}

async function editarSensor(id) {
    try {
        const response = await fetch(`${API_URL}/sensores/${id}`);
        const sensor = await response.json();
        
        document.getElementById('editId').value = sensor.idSensores;
        document.getElementById('editNombre').value = sensor.nombre;
        document.getElementById('editDescripcion').value = sensor.descripcion;
        document.getElementById('editSedeId').value = sensor.sede_id;
        
        const modal = document.getElementById('modalEditar');
        modal.style.display = 'flex';
        modal.classList.add('show');
    } catch (error) {
        console.error('Error al cargar sensor:', error);
        alert('Error al cargar datos del sensor');
    }
}

async function actualizarSensor(event) {
    event.preventDefault();
    
    const id = document.getElementById('editId').value;
    const sensorData = {
        nombre: document.getElementById('editNombre').value,
        descripcion: document.getElementById('editDescripcion').value,
        sede_id: parseInt(document.getElementById('editSedeId').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/sensores/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(sensorData)
        });
        
        if (response.ok) {
            alert('Sensor actualizado correctamente');
            const modal = document.getElementById('modalEditar');
            modal.style.display = 'none';
            modal.classList.remove('show');
            cargarSensores();
        } else {
            const error = await response.json();
            alert('Error al actualizar sensor: ' + (error.detail || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar sensor');
    }
}

async function eliminarSensor(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este sensor?')) {
        try {
            const response = await fetch(`${API_URL}/sensores/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('Sensor eliminado correctamente');
                cargarSensores();
            } else {
                const error = await response.json();
                alert('Error al eliminar sensor: ' + (error.detail || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar sensor');
        }
    }
}