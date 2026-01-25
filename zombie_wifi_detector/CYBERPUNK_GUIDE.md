# 🎮 CYBERPUNK THEME - COMPLETE INSTALLATION GUIDE

## 🚀 ONE-LINER INSTALLATION

### **Windows:**
```batch
START_CYBERPUNK.bat
```

### **Mac/Linux:**
```bash
cd backend && python app_cyberpunk.py
```

---

## 📦 WHAT'S INCLUDED

### **New Files Created:**
1. `backend/app_cyberpunk.py` - Enhanced backend with cyberpunk features
2. `static/css/cyberpunk.css` - Complete cyberpunk styling (20KB+)
3. `static/js/cyberpunk.js` - All animations and effects
4. `START_CYBERPUNK.bat` - One-click launcher

### **Features Added:**
- ✅ Particle system (floating WiFi signals)
- ✅ Matrix rain background
- ✅ Glitch text effects
- ✅ Neon glow animations
- ✅ Scanning lines
- ✅ Interference overlay
- ✅ Ripple button effects
- ✅ Animated counters
- ✅ Signal strength bars
- ✅ Cyberpunk modals
- ✅ Team/Creators section
- ✅ Fully responsive design

---

## 🎨 HOW TO APPLY TO EXISTING PAGES

### **Option 1: Update Existing HTML Files**

Add to the `<head>` section of your HTML files:

```html
<!-- Add Cyberpunk Theme -->
<link rel="stylesheet" href="/static/css/cyberpunk.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap">
<script src="/static/js/cyberpunk.js" defer></script>
```

### **Option 2: Create New Cyberpunk Pages**

I'll provide complete HTML templates below.

---

## 📄 CYBERPUNK HTML TEMPLATES

### **1. test.html (Enhanced)**

Replace your `frontend/test.html` with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧟 Zombie WiFi Detector | CyberSentry AI</title>
    <link rel="stylesheet" href="/static/css/cyberpunk.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <!-- Particle Background -->
    <canvas id="particleCanvas"></canvas>
    
    <!-- Cyber Grid -->
    <div class="cyber-grid"></div>
    
    <!-- Navigation -->
    <nav class="cyber-nav">
        <div class="nav-logo">
            <i class="fas fa-skull"></i>
            <i class="fas fa-wifi"></i>
            <span class="nav-title">Zombie WiFi Detector</span>
        </div>
        <div class="nav-links">
            <button class="nav-btn" onclick="CyberFX.openModal('creatorsModal')">
                <i class="fas fa-users"></i> Creators
            </button>
            <div class="profile-icon" onclick="window.location.href='/profile'">
                <i class="fas fa-user"></i>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <div class="container">
        <!-- Hero Section -->
        <div class="text-center mb-20">
            <h1 class="glitch" data-text="ZOMBIE WIFI DETECTOR" style="font-size: 56px; margin: 40px 0 20px;">
                ZOMBIE WIFI DETECTOR
            </h1>
            <p style="font-size: 20px; color: rgba(255,255,255,0.8); margin-bottom: 40px;">
                AI-Powered Network Security Scanner
            </p>
            
            <!-- Scan Button -->
            <button class="scan-btn" onclick="runQuickScan()">
                <i class="fas fa-satellite-dish"></i>
                <span>SCAN NOW</span>
            </button>
        </div>
        
        <!-- Stats Grid -->
        <div class="stats-grid" style="margin-top: 60px;">
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-shield-alt"></i></div>
                <div class="stat-value" id="totalScans">0</div>
                <div class="stat-label">Total Scans</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="stat-value" id="threats">0</div>
                <div class="stat-label">Threats Detected</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-clock"></i></div>
                <div class="countdown" id="nextScan">--:--:--</div>
                <div class="stat-label">Next Auto Scan</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-wifi"></i></div>
                <div class="stat-value" id="networks">0</div>
                <div class="stat-label">Networks Found</div>
            </div>
        </div>
        
        <!-- Scan Results -->
        <div id="scanResults" class="mt-20"></div>
        
        <!-- Network List -->
        <div id="networkList" class="network-list"></div>
    </div>
    
    <!-- Creators Modal -->
    <div id="creatorsModal" class="cyber-modal">
        <div class="modal-content">
            <button class="modal-close" onclick="CyberFX.closeModal('creatorsModal')">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="creators-content">
                <h2 class="creators-title">CYBERSENTRY AI</h2>
                <p class="creators-text">
                    THIS MODEL IS A PART OF CYBERSENTRY AI<br>
                    BY TARUN, SHIVAM AND YASH<br>
                    IT WORKS FOR THE SECURITY OF EVERY PERSON<br>
                    FROM THE ZOMBIE WIFI NETWORK THREATS
                </p>
                
                <div class="team-grid">
                    <div class="team-card">
                        <div class="team-avatar">👨‍💻</div>
                        <div class="team-name">TARUN</div>
                        <div class="team-role">Lead Developer</div>
                    </div>
                    
                    <div class="team-card">
                        <div class="team-avatar">👨‍💻</div>
                        <div class="team-name">SHIVAM</div>
                        <div class="team-role">ML Engineer</div>
                    </div>
                    
                    <div class="team-card">
                        <div class="team-avatar">👨‍💻</div>
                        <div class="team-name">YASH</div>
                        <div class="team-role">Security Expert</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="cyber-footer">
        <div class="footer-text">A Product of CyberSentry AI</div>
    </footer>
    
    <!-- Scripts -->
    <script src="/static/js/cyberpunk.js"></script>
    <script>
        // Load stats
        async function loadStats() {
            try {
                const response = await fetch('/api/scans/stats');
                const data = await response.json();
                
                if (data.success) {
                    CyberFX.animateCounter(document.getElementById('totalScans'), data.stats.total_scans);
                    CyberFX.animateCounter(document.getElementById('threats'), data.stats.threats_detected);
                    CyberFX.animateCounter(document.getElementById('networks'), data.stats.available_networks);
                    CyberFX.startCountdown(document.getElementById('nextScan'), data.stats.next_auto_scan);
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        // Run quick scan
        async function runQuickScan() {
            const btn = document.querySelector('.scan-btn');
            const results = document.getElementById('scanResults');
            
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> SCANNING...';
            
            // Create explosion effect
            CyberFX.createScanExplosion();
            
            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const result = data.result;
                    
                    // Show result
                    results.innerHTML = `
                        <div class="cyber-card" style="text-align: center; margin-top: 30px;">
                            <h2 class="glitch" data-text="${result.alert_name}">${result.alert_name}</h2>
                            <p style="font-size: 24px; color: var(--cyber-blue); margin: 20px 0;">
                                Confidence: ${(result.confidence * 100).toFixed(1)}%
                            </p>
                            <p style="color: rgba(255,255,255,0.8);">
                                <i class="fas fa-network-wired"></i> ${result.networks_found} networks found<br>
                                <i class="fas fa-exclamation-triangle"></i> ${result.threats_detected} threats detected
                            </p>
                        </div>
                    `;
                    
                    // Load networks
                    loadNetworks(result.networks);
                    
                    // Reload stats
                    loadStats();
                }
            } catch (error) {
                results.innerHTML = `
                    <div class="cyber-card" style="text-align: center; background: var(--cyber-red);">
                        <i class="fas fa-exclamation-circle" style="font-size: 48px;"></i>
                        <p>Scan failed: ${error.message}</p>
                    </div>
                `;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-satellite-dish"></i> <span>SCAN AGAIN</span>';
            }
        }
        
        // Load networks
        function loadNetworks(networks) {
            const list = document.getElementById('networkList');
            
            if (!networks || networks.length === 0) {
                list.innerHTML = '';
                return;
            }
            
            list.innerHTML = '<h3 style="color: var(--cyber-blue); margin-bottom: 20px; font-size: 24px;">DETECTED NETWORKS</h3>';
            
            networks.forEach(network => {
                const threatClass = ['threat-safe', 'threat-low', 'threat-medium', 'threat-high', 'threat-critical'][network.threat_level];
                
                const item = document.createElement('div');
                item.className = 'network-item';
                item.innerHTML = `
                    <div class="network-header">
                        <div class="network-ssid">
                            <i class="fas fa-wifi"></i>
                            ${network.ssid}
                            ${network.is_zombie ? '<span class="zombie-badge"><i class="fas fa-skull"></i> ZOMBIE</span>' : ''}
                        </div>
                        <span class="threat-badge ${threatClass}">${network.threat_name}</span>
                    </div>
                    <div class="signal-bar">
                        <div class="signal-fill" style="width: ${network.signal_percent}%"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 14px; color: rgba(255,255,255,0.7); margin-top: 10px;">
                        <span><i class="fas fa-lock"></i> ${network.encryption}</span>
                        <span><i class="fas fa-signal"></i> ${network.signal} dBm</span>
                        <span><i class="fas fa-broadcast-tower"></i> Ch ${network.channel}</span>
                    </div>
                `;
                
                list.appendChild(item);
                
                // Animate signal bar
                setTimeout(() => {
                    CyberFX.animateSignalBar(item.querySelector('.signal-fill'), network.signal_percent);
                }, 100);
            });
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            loadStats();
        });
    </script>
</body>
</html>
```

---

## 🎯 QUICK START

### **Step 1: Stop Current Server**
```bash
Ctrl + C
```

### **Step 2: Run Cyberpunk Server**
```bash
# Windows
START_CYBERPUNK.bat

# Mac/Linux
cd backend
python app_cyberpunk.py
```

### **Step 3: Open Browser**
```
http://localhost:5000/test.html
```

---

## ✨ FEATURES SHOWCASE

### **Animations:**
- Particle systems floating in background
- Matrix rain effect
- Glitch text on hover
- Neon button glows
- Scanning lines
- Ripple effects on click
- Smooth transitions

### **Interactive Elements:**
- Stats counter animations
- Real-time countdown timer
- Signal strength bars
- Expandable network cards
- Modal popups
- Profile sections

### **Cyberpunk Aesthetics:**
- Dark backgrounds with neon accents
- Purple, blue, and red color scheme
- Glassmorphism effects
- Animated borders
- Interference overlays
- Grid backgrounds

---

## 🔧 CUSTOMIZATION

### **Change Colors:**

Edit `static/css/cyberpunk.css`:

```css
:root {
    --cyber-purple: #b026ff;  /* Change this */
    --cyber-blue: #00d9ff;    /* Change this */
    --cyber-red: #ff0055;     /* Change this */
}
```

### **Adjust Particle Count:**

Edit `static/js/cyberpunk.js`:

```javascript
// Line 24: Change from 50 to your desired number
for (let i = 0; i < 50; i++) {
```

### **Modify Team Members:**

Edit the creators modal in HTML:

```html
<div class="team-card">
    <div class="team-avatar">👨‍💻</div>
    <div class="team-name">YOUR NAME</div>
    <div class="team-role">Your Role</div>
</div>
```

---

## 📱 RESPONSIVE DESIGN

The theme is fully responsive:
- Desktop: Full effects
- Tablet: Optimized layout
- Mobile: Simplified animations

---

## 🚀 DEPLOYMENT

The cyberpunk theme works with:
- ✅ localhost
- ✅ Network access (LAN)
- ✅ Cloud hosting (Heroku, AWS, DigitalOcean)
- ✅ Docker containers

---

## 🎮 COMPLETE THEME INTEGRATION

All your existing pages can use the cyberpunk theme by adding:

1. Link to CSS: `/static/css/cyberpunk.css`
2. Link to JS: `/static/js/cyberpunk.js`
3. Add particle canvas: `<canvas id="particleCanvas"></canvas>`
4. Add cyber grid: `<div class="cyber-grid"></div>`

---

## 📞 SUMMARY

**Files to use:**
- `app_cyberpunk.py` - Enhanced backend
- `cyberpunk.css` - All styles
- `cyberpunk.js` - All animations
- `test.html` - Enhanced test page

**One command to start:**
```bash
python app_cyberpunk.py
```

**URL to visit:**
```
http://localhost:5000/test.html
```

**Enjoy your cyberpunk zombie WiFi detector!** 🎮🧟‍♂️
