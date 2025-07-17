document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const authResult = await authenticateUser(username, password);
            
            if (authResult) {
                const userData = {
                    username: authResult.username,
                    userId: authResult.idUsuarios,
                    rol: authResult.rol,
                    sedeIds: authResult.sede_ids || [],
                    sedes: authResult.sedes || []
                };
                
                sessionStorage.setItem('userData', JSON.stringify(userData));
                window.location.href = 'index.html';
            } else {
                showError('Credenciales inválidas');
            }
        } catch (error) {
            showError('Error de conexión. Intenta de nuevo.');
            console.error('Login error:', error);
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
});

async function authenticateUser(username, password) {
    try {
        console.log('Using API URL:', API_URL);
        
        const response = await fetch(`${API_URL}/usuarios/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const userData = await response.json();
            return userData;
        }
    } catch (error) {
        console.error('Authentication error:', error);
    }
    
    return false;
}