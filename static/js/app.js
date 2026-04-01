const AUTH_KEY = "neuroscan_token";

function getToken() {
    return sessionStorage.getItem(AUTH_KEY);
}

function setToken(token) {
    sessionStorage.setItem(AUTH_KEY, token);
}

function clearToken() {
    sessionStorage.removeItem(AUTH_KEY);
}

function isLoggedIn() {
    return !!getToken();
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = "/login";
        return false;
    }
    return true;
}

async function apiFetch(url, options = {}) {
    if (!requireAuth()) return null;
    
    const token = getToken();
    options.headers = {
        ...(options.headers || {}),
        "Authorization": `Bearer ${token}`
    };
    
    const res = await fetch(url, options);
    
    if (res.status === 401) {
        clearToken();
        window.location.href = "/login";
        return null;
    }
    
    return res;
}

function showAlert(message, type = "info") {
    const container = document.getElementById("alert-container");
    const alert = document.createElement("div");
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function formatDate(iso) {
    if (!iso) return "-";
    const date = new Date(iso);
    return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric"
    });
}

function logout() {
    clearToken();
    localStorage.removeItem("doctor_name");
    window.location.href = "/login";
}

function openModal(id) {
    document.getElementById(id).classList.add("show");
}

function closeModal(id) {
    document.getElementById(id).classList.remove("show");
}

document.addEventListener("DOMContentLoaded", () => {
    if (!isLoggedIn() && !window.location.pathname.includes("/login") && !window.location.pathname.includes("/register")) {
        window.location.href = "/login";
    }
    
    const doctorName = localStorage.getItem("doctor_name");
    if (doctorName) {
        const userNameEl = document.querySelector(".user-name");
        const avatarEl = document.querySelector(".avatar");
        if (userNameEl) userNameEl.textContent = doctorName;
        if (avatarEl) avatarEl.textContent = doctorName.charAt(0).toUpperCase();
    }
});
