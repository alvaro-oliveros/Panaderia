// Auto-detect API URL based on environment
function getApiUrl() {
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://127.0.0.1:8000';
    } else {
        // For production, use nginx proxy path
        return `${window.location.protocol}//${hostname}/api`;
    }
}

const API_URL = getApiUrl();
// Make API_URL available globally
window.API_URL = API_URL;

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