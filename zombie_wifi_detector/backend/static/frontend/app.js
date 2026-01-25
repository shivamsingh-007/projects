// ============================================================================
// Zombie WiFi Detector - Frontend Application
// Handles all user interactions, API calls, and UI updates
// ============================================================================

const API_BASE = 'http://localhost:5000/api';
let currentUser = null;
let autoScanInterval = null;

// ============================================================================
// Initialize Application
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Hide loading screen after delay
    setTimeout(() => {
        document.getElementById('loading-screen').style.display = 'none';
    }, 2000);
    
    // Check if user is logged in
    checkSession();
    
    // Request notification permission
    requestNotificationPermission();
});

// ============================================================================
// Authentication Functions
// ============================================================================

async function handleRegister() {
    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    
    if (!username || !email || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Registration successful! Please login.', 'success');
            showLogin();
            // Clear form
            document.getElementById('register-username').value = '';
            document.getElementById('register-email').value = '';
            document.getElementById('register-password').value = '';
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Connection error. Is the server running?', 'error');
        console.error('Register error:', error);
    }
}

async function handleLogin() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    
    if (!username || !password) {
        showToast('Please enter username and password', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            showToast(`Welcome back, ${data.user.username}!`, 'success');
            showDashboard();
            loadUserData();
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Connection error. Is the server running?', 'error');
        console.error('Login error:', error);
    }
}

async function handleLogout() {
    try {
        await fetch(`${API_BASE}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        currentUser = null;
        showToast('Logged out successfully', 'success');
        showLogin();
        
        // Clear dashboard
        document.getElementById('status-card').className = 'status-card';
        document.getElementById('alert-level').textContent = '--';
        document.getElementById('confidence').textContent = '--';
        document.getElementById('last-scan').textContent = 'Never';
        
    } catch (error) {
        console.error('Logout error:', error);
    }
}

async function checkSession() {
    try {
        const response = await fetch(`${API_BASE}/profile`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            showDashboard();
            loadUserData();
        }
    } catch (error) {
        console.error('Session check error:', error);
    }
}

// ============================================================================
// Dashboard Functions
// ============================================================================

async function loadUserData() {
    if (!currentUser) return;
    
    // Update username in nav
    document.getElementById('nav-username').textContent = currentUser.username;
    
    // Load latest scan
    await loadLatestScan();
    
    // Load scan history
    await loadScanHistory();
    
    // Load settings
    await loadSettings();
    
    // Detect interface
    await detectInterface();
}

async function loadLatestScan() {
    try {
        const response = await fetch(`${API_BASE}/scan/latest`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const scan = await response.json();
            updateStatusCard(scan);
        }
    } catch (error) {
        console.log('No previous scans');
    }
}

async function loadScanHistory() {
    try {
        const response = await fetch(`${API_BASE}/scan/history?limit=10`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            displayScanHistory(data.scans);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayScanHistory(scans) {
    const historyList = document.getElementById('history-list');
    
    if (!scans || scans.length === 0) {
        historyList.innerHTML = '<p class="empty-state">No scans yet. Click "Scan Now" to start.</p>';
        return;
    }
    
    historyList.innerHTML = scans.map(scan => `
        <div class="history-item">
            <div class="history-status">
                <span class="status-badge ${scan.status}"></span>
                <span>${getStatusText(scan.status)}</span>
            </div>
            <div class="history-time">${formatTimestamp(scan.timestamp)}</div>
        </div>
    `).join('');
}

function getStatusText(status) {
    const statusMap = {
        'normal': 'Network Clean',
        'low': 'Low Suspicion',
        'medium': 'Suspicious Activity',
        'high': 'High Alert',
        'critical': 'Critical Threat',
        'error': 'Scan Error'
    };
    return statusMap[status] || 'Unknown';
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
}

// ============================================================================
// Scanning Functions
// ============================================================================

async function performScan() {
    const scanBtn = document.getElementById('scan-btn');
    const scanProgress = document.getElementById('scan-progress');
    
    // Disable button
    scanBtn.disabled = true;
    scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Scanning...</span>';
    
    // Show progress
    scanProgress.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({})
        });
        
        const result = await response.json();
        
        if (response.ok && !result.error) {
            updateStatusCard(result);
            showToast('Scan completed successfully', 'success');
            
            // Reload history
            await loadScanHistory();
            
            // Show notification if threat detected
            if (result.alert_level >= 3) {
                showNotification('Threat Detected!', 'Zombie WiFi activity detected on your network');
            }
        } else {
            showToast(result.error || 'Scan failed', 'error');
        }
    } catch (error) {
        showToast('Scan failed. Check server and interface settings.', 'error');
        console.error('Scan error:', error);
    } finally {
        // Re-enable button
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<i class="fas fa-search"></i> <span>Scan Now</span>';
        scanProgress.style.display = 'none';
    }
}

function updateStatusCard(result) {
    const statusCard = document.getElementById('status-card');
    const statusIcon = document.getElementById('status-icon');
    const statusTitle = document.getElementById('status-title');
    const statusMessage = document.getElementById('status-message');
    const alertLevel = document.getElementById('alert-level');
    const confidence = document.getElementById('confidence');
    const lastScan = document.getElementById('last-scan');
    
    // Reset classes
    statusCard.className = 'status-card';
    statusIcon.className = 'status-icon';
    
    // Update based on status
    const status = result.status || 'normal';
    const level = result.alert_level || 0;
    const conf = result.confidence || 0;
    
    // Apply status classes
    if (level === 0) {
        statusCard.classList.add('status-normal');
        statusIcon.classList.add('normal');
        statusTitle.textContent = '✓ Network Secure';
        statusMessage.textContent = 'No threats detected. Your network is safe.';
    } else if (level <= 2) {
        statusCard.classList.add('status-warning');
        statusIcon.classList.add('warning');
        statusTitle.textContent = '⚠ Suspicious Activity';
        statusMessage.textContent = 'Some suspicious patterns detected. Monitor closely.';
    } else {
        statusCard.classList.add('status-danger');
        statusIcon.classList.add('danger');
        statusTitle.textContent = '🚨 THREAT DETECTED';
        statusMessage.textContent = 'Zombie WiFi detected! Take action immediately.';
    }
    
    // Update details
    alertLevel.textContent = getAlertLevelText(level);
    confidence.textContent = `${(conf * 100).toFixed(1)}%`;
    lastScan.textContent = result.timestamp ? formatTimestamp(result.timestamp) : 'Just now';
}

function getAlertLevelText(level) {
    const levels = ['NORMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
    return levels[level] || 'UNKNOWN';
}

// ============================================================================
// Settings Functions
// ============================================================================

async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const settings = await response.json();
            
            // Update form
            if (settings.interface) {
                document.getElementById('interface-select').value = settings.interface;
            }
            
            const scanInterval = settings.scan_interval || 3600;
            document.getElementById('scan-interval').value = scanInterval / 3600; // Convert to hours
            
            document.getElementById('notifications-enabled').checked = 
                settings.notifications_enabled !== false;
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function saveSettings() {
    const interfaceValue = document.getElementById('interface-select').value;
    const scanIntervalHours = parseInt(document.getElementById('scan-interval').value);
    const notificationsEnabled = document.getElementById('notifications-enabled').checked;
    
    if (!interfaceValue) {
        showToast('Please select a network interface', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                interface: interfaceValue,
                scan_interval: scanIntervalHours * 3600,
                notifications_enabled: notificationsEnabled
            })
        });
        
        if (response.ok) {
            showToast('Settings saved successfully', 'success');
            closeSettings();
        } else {
            showToast('Failed to save settings', 'error');
        }
    } catch (error) {
        showToast('Error saving settings', 'error');
        console.error('Settings error:', error);
    }
}

async function detectInterface() {
    try {
        const response = await fetch(`${API_BASE}/detect-interface`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const select = document.getElementById('interface-select');
            
            select.innerHTML = data.interfaces.map(iface => 
                `<option value="${iface}">${iface}</option>`
            ).join('');
            
            if (data.recommended) {
                select.value = data.recommended;
            }
        }
    } catch (error) {
        console.error('Interface detection error:', error);
    }
}

async function toggleAutoScan() {
    const enabled = document.getElementById('auto-scan-toggle').checked;
    
    try {
        const response = await fetch(`${API_BASE}/auto-scan/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ enabled })
        });
        
        if (response.ok) {
            showToast(`Auto-scan ${enabled ? 'enabled' : 'disabled'}`, 'success');
        } else {
            showToast('Failed to toggle auto-scan', 'error');
        }
    } catch (error) {
        showToast('Error toggling auto-scan', 'error');
        console.error('Auto-scan error:', error);
    }
}

// ============================================================================
// UI Helper Functions
// ============================================================================

function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
}

function showLogin() {
    document.getElementById('auth-page').style.display = 'flex';
    document.getElementById('dashboard-page').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
}

function showDashboard() {
    document.getElementById('auth-page').style.display = 'none';
    document.getElementById('dashboard-page').style.display = 'block';
}

function showSettings() {
    document.getElementById('settings-modal').classList.add('show');
}

function closeSettings() {
    document.getElementById('settings-modal').classList.remove('show');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// ============================================================================
// Notification Functions
// ============================================================================

function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

function showNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '/favicon.ico',
            badge: '/favicon.ico'
        });
    }
}

// ============================================================================
// Keyboard Shortcuts
// ============================================================================

document.addEventListener('keydown', (e) => {
    // Close modal on Escape
    if (e.key === 'Escape') {
        closeSettings();
    }
    
    // Ctrl+Enter to scan
    if (e.ctrlKey && e.key === 'Enter') {
        if (currentUser) {
            performScan();
        }
    }
});

// Close modal when clicking outside
document.getElementById('settings-modal').addEventListener('click', (e) => {
    if (e.target.id === 'settings-modal') {
        closeSettings();
    }
});

// Enter key to submit forms
document.getElementById('login-password').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleLogin();
});

document.getElementById('register-password').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleRegister();
});

console.log('🔒 Zombie WiFi Detector - Frontend Loaded');
console.log('Backend API:', API_BASE);
