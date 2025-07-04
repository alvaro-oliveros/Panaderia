const API_URL = "http://127.0.0.1:8000";

function checkAuth() {
    const userData = sessionStorage.getItem('userData');
    if (!userData) {
        window.location.href = 'login.html';
        return null;
    }
    return JSON.parse(userData);
}

function logout() {
    sessionStorage.removeItem('userData');
    window.location.href = 'login.html';
}

function isAdmin() {
    const userData = checkAuth();
    return userData && userData.rol === 'admin';
}

function getCurrentUser() {
    const userData = checkAuth();
    return userData ? userData.userId : null;
}
