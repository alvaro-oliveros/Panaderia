document.addEventListener('DOMContentLoaded', function() {
    const userData = checkAuth();
    if (!userData) return;

    setupUserInterface(userData);
    setupTabNavigation();
    loadDashboardData();
});

function setupUserInterface(userData) {
    const userWelcome = document.getElementById('userWelcome');
    const sedesLink = document.getElementById('sedesLink');
    const usuariosLink = document.getElementById('usuariosLink');
    
    if (userData.userType === 'admin') {
        userWelcome.textContent = `Bienvenido, Administrador ${userData.username}`;
    } else {
        userWelcome.textContent = `Bienvenido, ${userData.bakeryName} (${userData.username})`;
        sedesLink.style.display = 'none';
        usuariosLink.style.display = 'none';
        
        // Hide sedes tab for non-admin users
        const sedesTab = document.querySelector('[data-table="sedes"]');
        if (sedesTab) {
            sedesTab.style.display = 'none';
        }
        
        // Set productos as the default active tab for non-admin users
        showTable('productos');
        const productosTab = document.querySelector('[data-table="productos"]');
        if (productosTab) {
            document.querySelector('.tab-button.active').classList.remove('active');
            productosTab.classList.add('active');
        }
    }
}

function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tableName = this.getAttribute('data-table');
            
            // Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Show the selected table
            showTable(tableName);
        });
    });
}

function showTable(tableName) {
    // Hide all table containers
    const containers = ['sedesContainer', 'productosContainer', 'movimientosContainer', 'sensoresContainer', 'temperaturaContainer', 'humedadContainer'];
    containers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            container.style.display = 'none';
        }
    });
    
    // Show the selected table container
    const selectedContainer = document.getElementById(tableName + 'Container');
    if (selectedContainer) {
        selectedContainer.style.display = 'block';
    }
}

async function loadDashboardData() {
    const userData = checkAuth();
    if (!userData) return;

    try {
        await Promise.all([
            loadSedes(),
            loadProductos(),
            loadMovimientos(),
            loadSensores(),
            loadTemperatura(),
            loadHumedad()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function loadSedes() {
    const userData = checkAuth();
    if (userData.userType !== 'admin') {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/sedes/`);
        const sedes = await response.json();
        const tbody = document.getElementById('sedesTableBody');
        
        tbody.innerHTML = '';
        sedes.forEach(sede => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${sede.idSedes}</td>
                <td>${sede.Nombre}</td>
                <td>${sede.Direccion}</td>
            `;
        });
    } catch (error) {
        console.error('Error loading sedes:', error);
    }
}

async function loadProductos() {
    const userData = checkAuth();
    let url = `${API_URL}/productos/`;
    
    // For regular users, filter by their assigned sedes
    if (userData.userType === 'bakery' && userData.userId) {
        url += `?user_id=${userData.userId}`;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();
        
        // Handle both old format (array) and new format (object with pagination)
        const productos = data.productos || data;
        const tbody = document.getElementById('productosTableBody');
        
        tbody.innerHTML = '';
        productos.forEach(producto => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${producto.idProductos}</td>
                <td>${producto.Nombre}</td>
                <td>S/.${producto.Precio.toFixed(2)}</td>
                <td>${producto.Stock}</td>
            `;
        });
    } catch (error) {
        console.error('Error loading productos:', error);
    }
}

async function loadMovimientos() {
    const userData = checkAuth();
    let url = `${API_URL}/movimientos/`;
    
    // For regular users, filter by their assigned sedes
    if (userData.userType === 'bakery' && userData.userId) {
        url += `?user_id=${userData.userId}`;
    }

    try {
        const response = await fetch(url);
        const movimientosData = await response.json();
        const tbody = document.getElementById('movimientosTableBody');
        
        // Handle both old format (array) and new format (object with pagination)
        const movimientos = movimientosData.movements || movimientosData;
        
        // Also load sedes and productos for display names
        const [sedesResponse, productosResponse] = await Promise.all([
            fetch(`${API_URL}/sedes/`),
            fetch(`${API_URL}/productos/?limit=1000`)
        ]);
        const sedes = await sedesResponse.json();
        const productosData = await productosResponse.json();
        
        // Handle both old format (array) and new format (object with pagination)
        const productos = productosData.productos || productosData;
        
        // Create lookup maps
        const sedesMap = {};
        sedes.forEach(sede => {
            sedesMap[sede.idSedes] = sede.Nombre;
        });
        
        const productosMap = {};
        productos.forEach(producto => {
            productosMap[producto.idProductos] = producto.Nombre;
        });
        
        tbody.innerHTML = '';
        movimientos.forEach(movimiento => {
            const row = tbody.insertRow();
            const fecha = new Date(movimiento.fecha).toLocaleDateString();
            const sedeNombre = sedesMap[movimiento.sede_id] || `Sede ${movimiento.sede_id}`;
            const productoNombre = productosMap[movimiento.producto_id] || `Producto ${movimiento.producto_id}`;
            
            row.innerHTML = `
                <td>${movimiento.idMovimientos}</td>
                <td>${productoNombre}</td>
                <td>${sedeNombre}</td>
                <td>${movimiento.tipo}</td>
                <td>${movimiento.Cantidad}</td>
                <td>${fecha}</td>
            `;
        });
    } catch (error) {
        console.error('Error loading movimientos:', error);
    }
}

async function loadSensores() {
    const userData = checkAuth();
    let url = `${API_URL}/sensores/`;
    
    if (userData.userType === 'bakery' && userData.userId) {
        url += `?user_id=${userData.userId}`;
    }

    try {
        const response = await fetch(url);
        const sensores = await response.json();
        const tbody = document.getElementById('sensoresTableBody');
        
        // Load sedes for display names
        const sedesResponse = await fetch(`${API_URL}/sedes/`);
        const sedes = await sedesResponse.json();
        
        const sedesMap = {};
        sedes.forEach(sede => {
            sedesMap[sede.idSedes] = sede.Nombre;
        });
        
        tbody.innerHTML = '';
        sensores.forEach(sensor => {
            const row = tbody.insertRow();
            const sedeNombre = sedesMap[sensor.sede_id] || `Sede ${sensor.sede_id}`;
            
            row.innerHTML = `
                <td>${sensor.idSensores}</td>
                <td>${sensor.nombre}</td>
                <td>${sensor.descripcion}</td>
                <td>${sedeNombre}</td>
            `;
        });
    } catch (error) {
        console.error('Error loading sensores:', error);
    }
}

async function loadTemperatura() {
    const userData = checkAuth();
    let url = `${API_URL}/temperatura/`;
    
    if (userData.userType === 'bakery' && userData.userId) {
        url += `?user_id=${userData.userId}`;
    }

    try {
        const response = await fetch(url);
        const temperaturas = await response.json();
        const tbody = document.getElementById('temperaturaTableBody');
        
        // Load sensores and sedes for display names
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
        
        tbody.innerHTML = '';
        // Show only the latest 10 temperature readings
        const latestTemperaturas = temperaturas.slice(0, 10);
        
        latestTemperaturas.forEach(temp => {
            const row = tbody.insertRow();
            const sensor = sensoresMap[temp.Sensor_id];
            const sedeNombre = sensor ? sedesMap[sensor.sede_id] : 'N/A';
            const sensorNombre = sensor ? sensor.nombre : 'N/A';
            const fecha = new Date(temp.fecha).toLocaleString('es-ES');
            
            row.innerHTML = `
                <td>${temp.idTemperatura}</td>
                <td>${temp.Temperatura}°C</td>
                <td>${sensorNombre}</td>
                <td>${sedeNombre}</td>
                <td>${fecha}</td>
            `;
        });
    } catch (error) {
        console.error('Error loading temperatura:', error);
    }
}

async function loadHumedad() {
    const userData = checkAuth();
    let url = `${API_URL}/humedad/`;
    
    if (userData.userType === 'bakery' && userData.userId) {
        url += `?user_id=${userData.userId}`;
    }

    try {
        const response = await fetch(url);
        const humedades = await response.json();
        const tbody = document.getElementById('humedadTableBody');
        
        // Load sensores and sedes for display names
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
        
        tbody.innerHTML = '';
        // Show only the latest 10 humidity readings
        const latestHumedades = humedades.slice(0, 10);
        
        latestHumedades.forEach(hum => {
            const row = tbody.insertRow();
            const sensor = sensoresMap[hum.Sensor_id];
            const sedeNombre = sensor ? sedesMap[sensor.sede_id] : 'N/A';
            const sensorNombre = sensor ? sensor.nombre : 'N/A';
            const fecha = new Date(hum.fecha).toLocaleString('es-ES');
            const humidityInfo = getHumidityStatus(hum.Humedad);
            
            row.innerHTML = `
                <td>${hum.idHumedad}</td>
                <td>${hum.Humedad}%</td>
                <td>${sensorNombre}</td>
                <td>${sedeNombre}</td>
                <td>${fecha}</td>
                <td><span class="humidity-status ${humidityInfo.class}">${humidityInfo.status}</span></td>
            `;
        });
    } catch (error) {
        console.error('Error loading humedad:', error);
    }
}