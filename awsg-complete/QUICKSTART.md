# 🚀 AWSG Quick Start - 60 Second Setup

## Step 1: Copy the file (5 seconds)

```bash
# Copy awsg-autonomous.js to your project
cp src/awsg-autonomous.js /your-project/public/js/
```

## Step 2: Add to your HTML (30 seconds)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Your App</title>
</head>
<body>
    <!-- Your existing content -->
    <h1>My Application</h1>
    
    <!-- Add these 2 lines at the bottom -->
    <script src="/js/awsg-autonomous.js"></script>
    <script>
        const security = createSecurityGateway({ appId: 'my-app' });
    </script>
</body>
</html>
```

## Step 3: Done! (Test it - 25 seconds)

Open browser console and type:

```javascript
// Try to inject a script (will be blocked)
const script = document.createElement('script');
script.textContent = 'alert("test")';
document.body.appendChild(script);
```

You should see:
```
[AWSG CRITICAL] 🚨 THREAT BLOCKED: XSS_DANGEROUS_TAG
```

**✅ Your app is now protected!**

---

## Common Frameworks

### React
```jsx
// App.jsx
import { useEffect } from 'react';

function App() {
    useEffect(() => {
        const security = createSecurityGateway({ appId: 'my-app' });
    }, []);
    
    return <div>Your App</div>;
}
```

### Vue.js
```javascript
// main.js
import createSecurityGateway from './awsg-autonomous.js';
const security = createSecurityGateway({ appId: 'my-app' });
```

### Next.js
```jsx
// pages/_app.js
import { useEffect } from 'react';

function MyApp({ Component, pageProps }) {
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const security = createSecurityGateway({ appId: 'my-app' });
        }
    }, []);
    
    return <Component {...pageProps} />;
}
```

---

## Need More?

📖 **Full Documentation**: `INSTALLATION.md`  
🎮 **Interactive Demo**: `examples/demo-realtime.html`  
📚 **Complete Guide**: `docs/README.md`
