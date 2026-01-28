# 📋 AWSG Installation - Step-by-Step Visual Guide

## 📦 What You Received

```
awsg-complete/
├── 📄 README.md              ← Start here
├── 🚀 QUICKSTART.md          ← 60-second setup
├── 📖 INSTALLATION.md        ← Detailed guide
├── 📦 package.json           ← NPM config
│
├── 📂 src/
│   ├── awsg-autonomous.js   ← ⭐ MAIN FILE - Copy this!
│   └── awsg.d.ts            ← TypeScript definitions
│
├── 📂 examples/
│   ├── demo-realtime.html   ← 🎮 Try this first!
│   └── integration-examples.js
│
├── 📂 docs/
│   ├── README.md
│   ├── DEPLOYMENT-GUIDE.md
│   └── PRODUCTION-CHECKLIST.md
│
└── 📂 tests/
    ├── quick-test.js
    └── test-suite.js
```

---

## 🎯 Installation Methods (Choose One)

### ⚡ Method 1: Direct Script Tag (Easiest - Recommended)

**Perfect for:** Vanilla JS, simple HTML sites, WordPress, etc.

```
┌─────────────────────────────────────────────────┐
│ Step 1: Copy File                               │
└─────────────────────────────────────────────────┘

Your project structure:
your-project/
├── index.html
└── js/
    └── awsg-autonomous.js  ← Copy here

Command:
cp awsg-complete/src/awsg-autonomous.js your-project/js/

┌─────────────────────────────────────────────────┐
│ Step 2: Add to HTML                             │
└─────────────────────────────────────────────────┘

Open: your-project/index.html

Add before closing </body> tag:
```

```html
<!DOCTYPE html>
<html>
<head>
    <title>Your App</title>
</head>
<body>
    <!-- Your existing content -->
    <h1>My Application</h1>
    <p>Welcome!</p>
    
    <!-- ⬇️ Add these 2 lines here -->
    <script src="js/awsg-autonomous.js"></script>
    <script>
        const security = createSecurityGateway({
            appId: 'your-app-name'
        });
        console.log('✅ AWSG Active');
    </script>
</body>
</html>
```

```
┌─────────────────────────────────────────────────┐
│ Step 3: Test                                    │
└─────────────────────────────────────────────────┘

1. Open your app in browser
2. Open Console (F12)
3. You should see: "✅ AWSG Active"
4. Try this in console:

   const s = document.createElement('script');
   s.textContent = 'alert("test")';
   document.body.appendChild(s);

5. You should see: "[AWSG CRITICAL] 🚨 THREAT BLOCKED"

✅ Done! Your app is protected!
```

---

### ⚛️ Method 2: React Application

**Perfect for:** Create React App, Vite, etc.

```
┌─────────────────────────────────────────────────┐
│ Step 1: Copy File                               │
└─────────────────────────────────────────────────┘

Your project structure:
my-react-app/
├── public/
│   └── js/
│       └── awsg-autonomous.js  ← Copy here
└── src/
    └── App.jsx

Command:
mkdir -p my-react-app/public/js
cp awsg-complete/src/awsg-autonomous.js my-react-app/public/js/

┌─────────────────────────────────────────────────┐
│ Step 2: Load in index.html                      │
└─────────────────────────────────────────────────┘

Open: my-react-app/public/index.html

Add in <body> before root div:
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>React App</title>
</head>
<body>
    <!-- ⬇️ Add this line -->
    <script src="%PUBLIC_URL%/js/awsg-autonomous.js"></script>
    
    <div id="root"></div>
</body>
</html>
```

```
┌─────────────────────────────────────────────────┐
│ Step 3: Initialize in App.jsx                   │
└─────────────────────────────────────────────────┘

Open: my-react-app/src/App.jsx
```

```jsx
import { useEffect } from 'react';
import './App.css';

function App() {
    // ⬇️ Add this useEffect hook
    useEffect(() => {
        // Initialize AWSG
        const security = window.createSecurityGateway({
            appId: 'my-react-app',
            trustedOrigins: ['api.mysite.com']
        });
        
        console.log('✅ AWSG Protection Active');
        
        // Optional: Listen to threats
        security.onThreat((threat) => {
            console.log('🚨 Blocked:', threat.type);
        });
    }, []); // Empty array = run once
    
    return (
        <div className="App">
            <h1>My React App</h1>
            {/* Your components */}
        </div>
    );
}

export default App;
```

```
┌─────────────────────────────────────────────────┐
│ Step 4: Test                                    │
└─────────────────────────────────────────────────┘

1. Run: npm start
2. Open browser console (F12)
3. Should see: "✅ AWSG Protection Active"
4. Try attack: (paste in console)

   const s = document.createElement('script');
   s.textContent = 'alert("xss")';
   document.body.appendChild(s);

5. Should see: "🚨 THREAT BLOCKED"

✅ Done! React app is protected!
```

---

### 🟢 Method 3: Vue.js Application

```
┌─────────────────────────────────────────────────┐
│ Step 1: Copy File                               │
└─────────────────────────────────────────────────┘

Your project structure:
my-vue-app/
├── public/
│   └── js/
│       └── awsg-autonomous.js  ← Copy here
└── src/
    └── main.js

Command:
mkdir -p my-vue-app/public/js
cp awsg-complete/src/awsg-autonomous.js my-vue-app/public/js/

┌─────────────────────────────────────────────────┐
│ Step 2: Load in index.html                      │
└─────────────────────────────────────────────────┘

Open: my-vue-app/public/index.html

Add in <body>:
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Vue App</title>
</head>
<body>
    <!-- ⬇️ Add this line -->
    <script src="js/awsg-autonomous.js"></script>
    
    <div id="app"></div>
</body>
</html>
```

```
┌─────────────────────────────────────────────────┐
│ Step 3: Initialize in main.js                   │
└─────────────────────────────────────────────────┘

Open: my-vue-app/src/main.js
```

```javascript
import { createApp } from 'vue';
import App from './App.vue';

// ⬇️ Add AWSG initialization
const security = window.createSecurityGateway({
    appId: 'my-vue-app',
    trustedOrigins: ['api.mysite.com']
});

console.log('✅ AWSG Protection Active');

const app = createApp(App);
app.mount('#app');
```

```
✅ Done! Vue app is protected!
```

---

### 🔷 Method 4: Next.js Application

```
┌─────────────────────────────────────────────────┐
│ Step 1: Copy File                               │
└─────────────────────────────────────────────────┘

Your project structure:
my-nextjs-app/
├── public/
│   └── js/
│       └── awsg-autonomous.js  ← Copy here
└── pages/
    └── _app.js

Command:
mkdir -p my-nextjs-app/public/js
cp awsg-complete/src/awsg-autonomous.js my-nextjs-app/public/js/

┌─────────────────────────────────────────────────┐
│ Step 2: Load in _document.js (create if needed) │
└─────────────────────────────────────────────────┘

Create: my-nextjs-app/pages/_document.js
```

```jsx
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
    return (
        <Html>
            <Head />
            <body>
                {/* ⬇️ Add AWSG script */}
                <script src="/js/awsg-autonomous.js"></script>
                <Main />
                <NextScript />
            </body>
        </Html>
    );
}
```

```
┌─────────────────────────────────────────────────┐
│ Step 3: Initialize in _app.js                   │
└─────────────────────────────────────────────────┘

Open: my-nextjs-app/pages/_app.js
```

```jsx
import { useEffect } from 'react';

function MyApp({ Component, pageProps }) {
    // ⬇️ Add AWSG initialization
    useEffect(() => {
        // Client-side only
        if (typeof window !== 'undefined') {
            const security = window.createSecurityGateway({
                appId: 'my-nextjs-app',
                trustedOrigins: ['api.mysite.com']
            });
            
            console.log('✅ AWSG Protection Active');
        }
    }, []);
    
    return <Component {...pageProps} />;
}

export default MyApp;
```

```
✅ Done! Next.js app is protected!
```

---

## 🎮 Test Your Installation

### Quick Test (Browser Console)

```javascript
// 1. Check if AWSG is loaded
console.log(typeof createSecurityGateway);
// Should output: "function"

// 2. Check if initialized
console.log(security.getStatus().active);
// Should output: true

// 3. Try an attack
const script = document.createElement('script');
script.textContent = 'alert("test")';
document.body.appendChild(script);
// Should see: [AWSG CRITICAL] 🚨 THREAT BLOCKED
```

### Visual Test (Open Demo)

```bash
# Open the interactive demo
open awsg-complete/examples/demo-realtime.html
```

Click the red attack buttons - all should be blocked!

---

## ⚙️ Configuration Guide

### Minimal (Default - Recommended)

```javascript
const security = createSecurityGateway({
    appId: 'my-app'
});
```

This is enough for most applications!

### Add Your API Domain

```javascript
const security = createSecurityGateway({
    appId: 'my-app',
    trustedOrigins: [
        'api.mysite.com',     // Your API
        'cdn.mysite.com'      // Your CDN
    ]
});
```

### Full Configuration (Advanced)

```javascript
const security = createSecurityGateway({
    appId: 'my-app',
    logLevel: 'warn',  // 'silent' | 'warn' | 'debug'
    trustedOrigins: [
        'api.mysite.com',
        'cdn.mysite.com',
        'fonts.googleapis.com'
    ],
    onThreatDetected: (threat) => {
        // Custom handling
        console.log('Threat:', threat.type);
        
        // Send to analytics
        gtag('event', 'security_threat', {
            type: threat.type
        });
    }
});
```

---

## 🔍 Verify It's Working

### Method 1: Check Console

After installation, you should see:
```
✅ AWSG Protection Active
[AWSG INFO] Real-time threat monitoring ACTIVE
[AWSG INFO] Monitoring: DOM, Forms, Navigation, Storage, Network
```

### Method 2: Monitor Metrics

```javascript
// In console or your code:
setInterval(() => {
    const status = security.getStatus();
    console.log('Blocked:', status.metrics.blockedAttempts);
}, 10000);
```

### Method 3: Try Real Attacks

Open `examples/demo-realtime.html` and click attack buttons!

---

## 🚨 Common Issues & Solutions

### Issue: "createSecurityGateway is not defined"

❌ **Problem:** Script loaded after initialization code  
✅ **Solution:** Move script tag BEFORE your initialization

```html
<!-- ✅ Correct order -->
<script src="awsg-autonomous.js"></script>
<script>
    const security = createSecurityGateway({ appId: 'app' });
</script>
```

### Issue: "Cannot read property 'getStatus' of undefined"

❌ **Problem:** Security object not created  
✅ **Solution:** Check console for errors, ensure script loaded

### Issue: API calls are blocked

❌ **Problem:** API domain not trusted  
✅ **Solution:** Add to trustedOrigins

```javascript
trustedOrigins: ['api.yoursite.com']
```

---

## 📊 What Happens Now?

AWSG is now actively protecting your application:

```
┌──────────────────────────────────────┐
│ ✅ XSS attacks blocked               │
│ ✅ SQL injection prevented           │
│ ✅ SSRF attempts stopped             │
│ ✅ Malicious scripts removed         │
│ ✅ Forms scanned                     │
│ ✅ Navigation protected              │
└──────────────────────────────────────┘
```

All in real-time, with zero server dependency!

---

## 📚 Next Steps

1. ✅ **Test**: Open `examples/demo-realtime.html`
2. 📖 **Read**: `INSTALLATION.md` for detailed docs
3. 🚀 **Deploy**: `docs/DEPLOYMENT-GUIDE.md` for production
4. 📊 **Monitor**: Set up threat logging

---

## 🆘 Need Help?

1. **Quick answers**: See [INSTALLATION.md](INSTALLATION.md)
2. **Full docs**: See [docs/README.md](docs/README.md)
3. **Examples**: See [examples/](examples/)

---

**✅ You're now protected with enterprise-grade security!** 🛡️
