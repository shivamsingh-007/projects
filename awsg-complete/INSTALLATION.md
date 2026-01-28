# 🛡️ AWSG - Autonomous Web Security Gateway

**Real-time threat monitoring and blocking system that works completely offline**

---

## 📁 Package Contents

```
awsg-complete/
├── src/
│   ├── awsg-autonomous.js      ← Main security module (USE THIS)
│   └── awsg.d.ts               ← TypeScript definitions
├── examples/
│   ├── demo-realtime.html      ← Interactive demo (OPEN THIS FIRST)
│   └── integration-examples.js ← Framework integration guides
├── tests/
│   ├── quick-test.js           ← Fast validation
│   └── test-suite.js           ← Full test suite
├── docs/
│   ├── README.md               ← Complete documentation
│   ├── DEPLOYMENT-GUIDE.md     ← Production deployment
│   └── PRODUCTION-CHECKLIST.md ← Pre-deployment checklist
├── package.json                ← NPM configuration
└── INSTALLATION.md             ← This file
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: See It In Action First

```bash
# Open the interactive demo
open examples/demo-realtime.html
```

**Click the attack buttons** to see real-time blocking in action!

### Step 2: Add to Your Application

Choose your installation method:

#### Option A: Direct Script Tag (Easiest)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Your App</title>
</head>
<body>
    <!-- Your app content -->
    
    <!-- Add AWSG at the bottom, before closing body tag -->
    <script src="path/to/awsg-autonomous.js"></script>
    <script>
        // Initialize protection
        const security = createSecurityGateway({
            appId: 'your-app-name',
            trustedOrigins: ['api.yoursite.com']
        });
        
        console.log('✅ AWSG Protection Active');
    </script>
</body>
</html>
```

#### Option B: NPM/Module Import

```bash
# Copy awsg-autonomous.js to your project
cp src/awsg-autonomous.js your-project/src/lib/
```

```javascript
// Import in your main app file
import createSecurityGateway from './lib/awsg-autonomous.js';

// Initialize
const security = createSecurityGateway({
    appId: 'your-app',
    trustedOrigins: ['api.yoursite.com']
});
```

#### Option C: React Application

```jsx
// App.jsx or App.tsx
import { useEffect } from 'react';
import createSecurityGateway from './lib/awsg-autonomous.js';

function App() {
    useEffect(() => {
        // Initialize AWSG on component mount
        const security = createSecurityGateway({
            appId: 'react-app',
            trustedOrigins: ['api.yoursite.com'],
            onThreatDetected: (threat) => {
                console.log('🚨 Threat blocked:', threat.type);
            }
        });
        
        console.log('✅ AWSG Protection Active');
    }, []); // Empty dependency array = run once on mount
    
    return (
        <div className="App">
            {/* Your app components */}
        </div>
    );
}

export default App;
```

#### Option D: Vue.js Application

```javascript
// main.js
import { createApp } from 'vue';
import App from './App.vue';
import createSecurityGateway from './lib/awsg-autonomous.js';

// Initialize AWSG before creating Vue app
const security = createSecurityGateway({
    appId: 'vue-app',
    trustedOrigins: ['api.yoursite.com']
});

console.log('✅ AWSG Protection Active');

const app = createApp(App);
app.mount('#app');
```

#### Option E: Next.js Application

```jsx
// pages/_app.js
import { useEffect } from 'react';
import createSecurityGateway from '../lib/awsg-autonomous.js';

function MyApp({ Component, pageProps }) {
    useEffect(() => {
        // Client-side only
        if (typeof window !== 'undefined') {
            const security = createSecurityGateway({
                appId: 'nextjs-app',
                trustedOrigins: ['api.yoursite.com']
            });
            
            console.log('✅ AWSG Protection Active');
        }
    }, []);
    
    return <Component {...pageProps} />;
}

export default MyApp;
```

#### Option F: Angular Application

```typescript
// app.component.ts
import { Component, OnInit } from '@angular/core';
declare const createSecurityGateway: any;

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html'
})
export class AppComponent implements OnInit {
    ngOnInit() {
        // Load AWSG script dynamically
        const script = document.createElement('script');
        script.src = '/assets/awsg-autonomous.js';
        script.onload = () => {
            const security = createSecurityGateway({
                appId: 'angular-app',
                trustedOrigins: ['api.yoursite.com']
            });
            
            console.log('✅ AWSG Protection Active');
        };
        document.head.appendChild(script);
    }
}
```

---

## ⚙️ Configuration

### Minimal Configuration (Recommended)

```javascript
const security = createSecurityGateway({
    appId: 'my-app'
});
```

### Full Configuration

```javascript
const security = createSecurityGateway({
    // Required: Your app identifier
    appId: 'my-app',
    
    // Optional: Logging level
    logLevel: 'warn', // 'silent' | 'warn' | 'debug'
    
    // Optional: Trusted domains (for APIs, CDNs, etc.)
    trustedOrigins: [
        'api.yoursite.com',
        'cdn.yoursite.com',
        'fonts.googleapis.com',
        'checkout.stripe.com'
    ],
    
    // Optional: Automatically block threats (default: true)
    autoBlock: true,
    
    // Optional: Show user warnings (default: true)
    showWarnings: true,
    
    // Optional: Custom threat handler
    onThreatDetected: (threat) => {
        console.log('🚨 Threat:', threat.type, threat.severity);
        
        // Send to your analytics/monitoring
        if (window.gtag) {
            gtag('event', 'security_threat', {
                threat_type: threat.type,
                severity: threat.severity
            });
        }
        
        // Send to your backend for logging
        fetch('/api/security/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(threat)
        }).catch(() => {}); // Silent fail if offline
    }
});
```

---

## 📊 Monitoring Threats

### Get Real-Time Status

```javascript
// Get current status
const status = security.getStatus();

console.log('Active:', status.active);
console.log('Uptime:', status.uptime);
console.log('Blocked:', status.metrics.blockedAttempts);
console.log('Total Threats:', status.metrics.totalThreats);
```

### Listen to Threat Events

```javascript
// Method 1: DOM Event
window.addEventListener('awsg:threat', (event) => {
    const threat = event.detail;
    console.log('Threat blocked:', threat);
});

// Method 2: Callback
security.onThreat((threat) => {
    if (threat.severity === 'CRITICAL') {
        alert('Critical security threat blocked!');
    }
});
```

### Display Security Dashboard

```javascript
// Update every 5 seconds
setInterval(() => {
    const status = security.getStatus();
    const metrics = status.metrics;
    
    // Update your UI
    document.getElementById('threats-blocked').textContent = 
        metrics.blockedAttempts;
    document.getElementById('total-threats').textContent = 
        metrics.totalThreats;
}, 5000);
```

---

## ✅ Verify Installation

### Method 1: Console Check

```javascript
// In browser console
console.log(typeof createSecurityGateway); 
// Should output: "function"

const status = security.getStatus();
console.log(status.active);
// Should output: true
```

### Method 2: Run Tests

```bash
# Open browser console and run:
node tests/quick-test.js

# Expected output:
# ✓ Module loads
# ✓ Creates instance
# ✓ Has detector
# ✓ Detects XSS
# ✓ Detects SQLi
# ... etc
```

### Method 3: Try an Attack

```javascript
// In your browser console, try to inject a script:
const script = document.createElement('script');
script.textContent = 'alert("test")';
document.body.appendChild(script);

// Check console - you should see:
// [AWSG CRITICAL] 🚨 THREAT BLOCKED: XSS_DANGEROUS_TAG
```

---

## 🎯 What Gets Protected Automatically

Once installed, AWSG automatically protects against:

✅ **XSS (Cross-Site Scripting)**
- Script tag injection
- Event handler injection
- `javascript:` protocol
- Data URIs
- Malicious iframes

✅ **SQL Injection**
- UNION SELECT attacks
- Tautologies (OR 1=1)
- DROP TABLE attacks
- Stacked queries

✅ **SSRF (Server-Side Request Forgery)**
- Requests to private IPs
- Localhost access attempts
- Dangerous port access

✅ **Prototype Pollution**
- `__proto__` manipulation
- Constructor pollution

✅ **Path Traversal**
- `../` attacks
- Directory traversal

✅ **Command Injection**
- Shell command patterns
- Code execution attempts

---

## 🔧 Troubleshooting

### Issue: "createSecurityGateway is not defined"

**Cause:** Script not loaded yet  
**Solution:** Make sure script tag is before your initialization code

```html
<!-- ✅ Correct -->
<script src="awsg-autonomous.js"></script>
<script>
    const security = createSecurityGateway({ appId: 'app' });
</script>

<!-- ❌ Wrong -->
<script>
    const security = createSecurityGateway({ appId: 'app' });
</script>
<script src="awsg-autonomous.js"></script>
```

### Issue: Legitimate API calls blocked

**Cause:** API domain not in trusted origins  
**Solution:** Add your API domain

```javascript
const security = createSecurityGateway({
    appId: 'my-app',
    trustedOrigins: [
        'api.mysite.com',  // Add your API domain
        'cdn.mysite.com'   // Add your CDN domain
    ]
});
```

### Issue: Form submission blocked incorrectly

**Cause:** Input contains SQL-like keywords  
**Solution:** Whitelist specific patterns (contact support) or disable for specific forms

```javascript
// Temporary workaround: disable monitoring for specific form
const form = document.getElementById('my-special-form');
form.setAttribute('data-awsg-bypass', 'true'); // Not implemented yet, contact us
```

### Issue: Console shows many warnings

**Cause:** Debug mode enabled  
**Solution:** Change log level

```javascript
const security = createSecurityGateway({
    appId: 'my-app',
    logLevel: 'silent' // or 'warn'
});
```

---

## 📈 Production Deployment Checklist

Before deploying to production:

- [ ] Tested in staging environment
- [ ] Configured `trustedOrigins` for all your APIs/CDNs
- [ ] Set appropriate `logLevel` ('warn' or 'silent')
- [ ] Added threat monitoring/logging
- [ ] Verified no false positives on legitimate actions
- [ ] Tested with real user workflows
- [ ] Set up alerts for critical threats
- [ ] Documented in your deployment docs

---

## 🆘 Support

### Documentation
- **Full Docs**: `docs/README.md`
- **Deployment Guide**: `docs/DEPLOYMENT-GUIDE.md`
- **Production Checklist**: `docs/PRODUCTION-CHECKLIST.md`

### Examples
- **Interactive Demo**: `examples/demo-realtime.html`
- **Framework Examples**: `examples/integration-examples.js`

### Testing
- **Quick Test**: `tests/quick-test.js`
- **Full Suite**: `tests/test-suite.js`

---

## 📄 License

MIT License - Free for commercial use

---

## 🎉 You're Protected!

Once you complete the installation steps above, your application is automatically protected against:
- XSS attacks
- SQL injection
- SSRF attempts
- Prototype pollution
- Path traversal
- Command injection

**And it works even when your server is offline!** 🛡️

---

**Need help?** Check `docs/README.md` for detailed documentation.
