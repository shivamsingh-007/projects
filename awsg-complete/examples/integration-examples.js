/**
 * AWSG Integration Examples
 * Production-ready implementations for popular frameworks
 */

// ============================================================================
// 1. VANILLA JAVASCRIPT
// ============================================================================

// Simple integration
const security = createSecurityGateway({
  appId: 'my-app',
  logLevel: 'warn',
  dangerZone: ['/api/admin', '/api/payment'],
  trustedOrigins: ['api.example.com', 'cdn.example.com'],
  maxRiskScore: 75,
  autoCSP: true,
  behavioral: true
});

// Wrap fetch globally
window.fetch = security.proxyFetch(window.fetch);

// Use as normal
fetch('/api/users')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Request blocked:', error));

// Manual sanitization
const userInput = document.getElementById('search').value;
const safe = security.sanitize(userInput);
document.getElementById('results').textContent = safe;

// ============================================================================
// 2. REACT INTEGRATION
// ============================================================================

// Create a React hook
function useSecurityGateway(config) {
  const [security] = React.useState(() => createSecurityGateway(config));
  
  React.useEffect(() => {
    // Wrap fetch on mount
    const originalFetch = window.fetch;
    window.fetch = security.proxyFetch(originalFetch);
    
    return () => {
      // Restore on unmount
      window.fetch = originalFetch;
    };
  }, [security]);
  
  return security;
}

// Usage in App component
function App() {
  const security = useSecurityGateway({
    appId: 'react-app',
    dangerZone: ['/api/admin'],
    trustedOrigins: ['api.example.com']
  });
  
  const [data, setData] = React.useState(null);
  
  const fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      const json = await response.json();
      setData(json);
    } catch (error) {
      console.error('Security blocked request:', error);
    }
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    const input = e.target.search.value;
    const sanitized = security.sanitize(input);
    // Use sanitized input
  };
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input name="search" type="text" />
        <button type="submit">Search</button>
      </form>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}

// ============================================================================
// 3. VUE.JS INTEGRATION
// ============================================================================

// Create a Vue plugin
const AWSGPlugin = {
  install(app, options) {
    const security = createSecurityGateway(options);
    
    // Wrap fetch globally
    window.fetch = security.proxyFetch(window.fetch);
    
    // Provide security instance
    app.provide('security', security);
    
    // Add global method
    app.config.globalProperties.$security = security;
  }
};

// Register plugin
const app = Vue.createApp({
  // ... your app
});

app.use(AWSGPlugin, {
  appId: 'vue-app',
  dangerZone: ['/api/admin'],
  trustedOrigins: ['api.example.com']
});

// Use in component
export default {
  setup() {
    const security = Vue.inject('security');
    
    const fetchData = async () => {
      try {
        const response = await fetch('/api/data');
        return await response.json();
      } catch (error) {
        console.error('Blocked:', error);
      }
    };
    
    return { fetchData };
  }
};

// ============================================================================
// 4. ANGULAR INTEGRATION
// ============================================================================

// Create an Angular service
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SecurityService {
  private gateway;
  
  constructor() {
    this.gateway = createSecurityGateway({
      appId: 'angular-app',
      dangerZone: ['/api/admin'],
      trustedOrigins: ['api.example.com']
    });
  }
  
  sanitize(input: string): string {
    return this.gateway.sanitize(input);
  }
  
  getCSRFToken(): string {
    return this.gateway.getCSRFToken();
  }
  
  getMetrics() {
    return this.gateway.getMetrics();
  }
}

// HTTP Interceptor
@Injectable()
export class SecurityInterceptor implements HttpInterceptor {
  constructor(private security: SecurityService) {}
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Add CSRF token
    const token = this.security.getCSRFToken();
    
    const secureReq = req.clone({
      setHeaders: {
        'X-CSRF-Token': token
      }
    });
    
    return next.handle(secureReq);
  }
}

// Module configuration
import { HTTP_INTERCEPTORS } from '@angular/common/http';

@NgModule({
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: SecurityInterceptor,
      multi: true
    }
  ]
})
export class AppModule {}

// ============================================================================
// 5. NEXT.JS INTEGRATION
// ============================================================================

// _app.js
import { useEffect } from 'react';

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    // Initialize on client side only
    if (typeof window !== 'undefined') {
      const security = createSecurityGateway({
        appId: 'nextjs-app',
        dangerZone: ['/api/admin'],
        trustedOrigins: ['api.example.com']
      });
      
      window.fetch = security.proxyFetch(window.fetch);
      window.__security = security;
    }
  }, []);
  
  return <Component {...pageProps} />;
}

export default MyApp;

// API route middleware (pages/api/middleware.js)
export function securityMiddleware(handler) {
  return async (req, res) => {
    const security = createSecurityGateway({
      appId: 'nextjs-api',
      maxRiskScore: 75
    });
    
    // Scan request body
    if (req.body) {
      const detector = new security.detector;
      const scan = detector.scan(req.body);
      
      if (!scan.safe) {
        return res.status(400).json({
          error: 'Request blocked',
          riskScore: scan.riskScore
        });
      }
    }
    
    return handler(req, res);
  };
}

// Usage in API route
export default securityMiddleware(async (req, res) => {
  // Your API logic
  res.json({ message: 'Success' });
});

// ============================================================================
// 6. SVELTE INTEGRATION
// ============================================================================

// security.js (store)
import { writable } from 'svelte/store';

function createSecurityStore() {
  const security = createSecurityGateway({
    appId: 'svelte-app',
    dangerZone: ['/api/admin'],
    trustedOrigins: ['api.example.com']
  });
  
  // Wrap fetch
  window.fetch = security.proxyFetch(window.fetch);
  
  const { subscribe } = writable(security);
  
  return {
    subscribe,
    sanitize: (input) => security.sanitize(input),
    getMetrics: () => security.getMetrics(),
    getCSRFToken: () => security.getCSRFToken()
  };
}

export const security = createSecurityStore();

// Usage in component
<script>
  import { security } from './security.js';
  
  let data = null;
  
  async function fetchData() {
    try {
      const response = await fetch('/api/data');
      data = await response.json();
    } catch (error) {
      console.error('Blocked:', error);
    }
  }
  
  function handleInput(event) {
    const safe = $security.sanitize(event.target.value);
    // Use safe value
  }
</script>

// ============================================================================
// 7. AXIOS INTEGRATION
// ============================================================================

import axios from 'axios';

const security = createSecurityGateway({
  appId: 'axios-app',
  dangerZone: ['/api/admin'],
  trustedOrigins: ['api.example.com']
});

// Request interceptor
axios.interceptors.request.use(
  (config) => {
    // Add CSRF token
    config.headers['X-CSRF-Token'] = security.getCSRFToken();
    
    // Scan request data
    if (config.data) {
      const scan = security.detector.scan(config.data);
      if (!scan.safe) {
        throw new Error(`Request blocked (risk: ${scan.riskScore})`);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Usage
axios.get('/api/users')
  .then(response => console.log(response.data))
  .catch(error => console.error('Error:', error));

// ============================================================================
// 8. EXPRESS.JS MIDDLEWARE (Node.js)
// ============================================================================

const express = require('express');
const app = express();

// Create security middleware
function awsgMiddleware(config) {
  const security = createSecurityGateway(config);
  
  return (req, res, next) => {
    // Scan request body
    if (req.body) {
      const scan = security.detector.scan(req.body);
      
      if (!scan.safe) {
        return res.status(400).json({
          error: 'Request blocked by security gateway',
          riskScore: scan.riskScore,
          threats: scan.threats
        });
      }
    }
    
    // Scan query parameters
    if (req.query) {
      const scan = security.detector.scan(req.query);
      
      if (!scan.safe) {
        return res.status(400).json({
          error: 'Query parameters blocked',
          riskScore: scan.riskScore
        });
      }
    }
    
    // Add CSRF token to response
    res.locals.csrfToken = security.getCSRFToken();
    
    next();
  };
}

// Use middleware
app.use(express.json());
app.use(awsgMiddleware({
  appId: 'express-app',
  dangerZone: ['/admin', '/payment'],
  trustedOrigins: ['api.example.com'],
  maxRiskScore: 75
}));

app.post('/api/users', (req, res) => {
  // Request is already sanitized
  res.json({ success: true });
});

// ============================================================================
// 9. FORM VALIDATION HELPER
// ============================================================================

class SecureForm {
  constructor(formElement, security) {
    this.form = formElement;
    this.security = security;
    this.init();
  }
  
  init() {
    this.form.addEventListener('submit', (e) => {
      if (!this.validate()) {
        e.preventDefault();
        this.showError('Form contains unsafe content');
      }
    });
  }
  
  validate() {
    const formData = new FormData(this.form);
    
    for (const [key, value] of formData.entries()) {
      const scan = this.security.detector.scan(value);
      
      if (!scan.safe) {
        console.error(`Field "${key}" failed security check:`, scan);
        return false;
      }
    }
    
    return true;
  }
  
  showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'security-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = 'color: red; padding: 10px; margin: 10px 0; border: 1px solid red;';
    
    this.form.insertBefore(errorDiv, this.form.firstChild);
    
    setTimeout(() => errorDiv.remove(), 5000);
  }
}

// Usage
const security = createSecurityGateway({ appId: 'form-app' });
const form = document.querySelector('#myForm');
new SecureForm(form, security);

// ============================================================================
// 10. REAL-TIME DASHBOARD
// ============================================================================

class SecurityDashboard {
  constructor(security, containerElement) {
    this.security = security;
    this.container = containerElement;
    this.init();
  }
  
  init() {
    this.render();
    
    // Update every 5 seconds
    setInterval(() => this.render(), 5000);
  }
  
  render() {
    const metrics = this.security.getMetrics();
    const behavior = this.security.getBehaviorProfile();
    
    this.container.innerHTML = `
      <div style="font-family: monospace; padding: 20px; background: #f5f5f5;">
        <h3>AWSG Security Dashboard</h3>
        
        <div style="margin: 20px 0;">
          <h4>Configuration</h4>
          <div>App ID: ${metrics.config.appId}</div>
          <div>Max Risk Score: ${metrics.config.maxRiskScore}</div>
          <div>Danger Zones: ${metrics.config.dangerZone.join(', ') || 'None'}</div>
        </div>
        
        <div style="margin: 20px 0;">
          <h4>Request Metrics</h4>
          <div>Total Requests: ${metrics.requests.totalRequests}</div>
          <div>Average Duration: ${metrics.requests.averageDuration}</div>
          <div>Threats Blocked: ${metrics.requests.threats}</div>
        </div>
        
        <div style="margin: 20px 0;">
          <h4>Behavioral Analysis</h4>
          <div>Mouse Entropy: ${behavior.mouseEntropy.toFixed(2)}</div>
          <div>Keystroke Avg: ${behavior.keystrokeAvg.toFixed(2)}ms</div>
          <div>Session Fingerprint: ${behavior.sessionFingerprint}</div>
          <div>Learning Mode: ${behavior.learning ? 'Active' : 'Complete'}</div>
        </div>
        
        <button onclick="console.log(this.exportLog())">Export Log</button>
      </div>
    `.trim();
  }
}

// Usage
const dashboard = new SecurityDashboard(
  security,
  document.getElementById('dashboard')
);
