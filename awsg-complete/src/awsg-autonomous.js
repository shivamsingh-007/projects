/**
 * AWSG - Autonomous Web Security Gateway v2.0.0
 * Real-time threat monitoring and blocking system
 * Works completely offline - protects even when server is down
 * 
 * @license MIT
 */

(function(global) {
  'use strict';

  const VERSION = '2.0.0';
  
  // ============================================================================
  // REAL-TIME THREAT DATABASE (Offline-First)
  // ============================================================================
  
  const THREAT_SIGNATURES = {
    xss: {
      patterns: [
        /<script[\s\S]*?>[\s\S]*?<\/script>/gi,
        /javascript:/gi,
        /on\w+\s*=/gi,
        /<iframe[\s\S]*?>/gi,
        /eval\s*\(/gi,
        /document\.cookie/gi,
        /document\.write/gi,
        /window\.location/gi,
        /<object[\s\S]*?>/gi,
        /<embed[\s\S]*?>/gi,
        /vbscript:/gi,
        /data:text\/html/gi,
        /\.innerHTML\s*=/gi,
        /<svg[\s\S]*?onload/gi
      ],
      severity: 'CRITICAL',
      action: 'BLOCK'
    },
    
    sqli: {
      patterns: [
        /(\bor\b|\band\b)\s+[\'\"]?\d+[\'\"]?\s*=\s*[\'\"]?\d+/gi,
        /union\s+select/gi,
        /;\s*drop\s+table/gi,
        /;\s*delete\s+from/gi,
        /;\s*update\s+\w+\s+set/gi,
        /exec(\s|\()/gi,
        /execute(\s|\()/gi,
        /xp_cmdshell/gi,
        /\/\*[\s\S]*?\*\//g,
        /--\s*$/gm,
        /char\s*\(/gi,
        /concat\s*\(/gi
      ],
      severity: 'CRITICAL',
      action: 'BLOCK'
    },
    
    pathTraversal: {
      patterns: [
        /\.\.[\/\\]/g,
        /\%2e\%2e[\/\\]/gi,
        /\.\.%2f/gi,
        /\.\.%5c/gi
      ],
      severity: 'HIGH',
      action: 'BLOCK'
    },
    
    commandInjection: {
      patterns: [
        /;\s*(ls|cat|curl|wget|nc|bash|sh|cmd|powershell)/gi,
        /\|\s*(ls|cat|curl|wget|nc|bash|sh|cmd)/gi,
        /`[\s\S]*?`/g,
        /\$\([\s\S]*?\)/g
      ],
      severity: 'CRITICAL',
      action: 'BLOCK'
    },
    
    xxe: {
      patterns: [
        /<!ENTITY/gi,
        /<!DOCTYPE.*SYSTEM/gi,
        /SYSTEM\s+["']file:/gi
      ],
      severity: 'HIGH',
      action: 'BLOCK'
    }
  };

  // Private IP ranges for SSRF prevention
  const PRIVATE_IPS = [
    /^10\./,
    /^172\.(1[6-9]|2\d|3[01])\./,
    /^192\.168\./,
    /^127\./,
    /^169\.254\./,
    /^0\.0\.0\.0$/,
    /^::1$/,
    /^fe80:/i,
    /^fc00:/i,
    /^localhost$/i
  ];

  // Dangerous ports
  const BLOCKED_PORTS = ['22', '23', '25', '110', '143', '445', '3306', '3389', '5432', '6379', '27017'];

  // ============================================================================
  // REAL-TIME MONITORING ENGINE
  // ============================================================================

  class ThreatMonitor {
    constructor(config) {
      this.config = config;
      this.threatLog = [];
      this.blockedAttempts = 0;
      this.isActive = true;
      this.watchers = new Set();
      
      // Start real-time monitoring
      this.initializeMonitoring();
    }

    initializeMonitoring() {
      if (typeof window === 'undefined') return;

      // Monitor DOM mutations (real-time XSS injection detection)
      this.monitorDOM();
      
      // Monitor form submissions
      this.monitorForms();
      
      // Monitor URL changes
      this.monitorNavigation();
      
      // Monitor localStorage/sessionStorage access
      this.monitorStorage();
      
      // Monitor console (detect script injection attempts)
      this.monitorConsole();

      this.log('INFO', 'Real-time threat monitoring ACTIVE');
    }

    monitorDOM() {
      if (!window.MutationObserver) return;

      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) { // Element node
              const threat = this.scanElement(node);
              if (threat) {
                this.blockThreat(threat, node);
              }
            }
          });
        });
      });

      observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['src', 'href', 'onclick', 'onerror', 'onload']
      });

      this.watchers.add(observer);
      this.log('INFO', 'DOM monitoring enabled');
    }

    scanElement(element) {
      // Check for dangerous inline event handlers
      for (const attr of element.attributes || []) {
        if (attr.name.startsWith('on')) {
          return {
            type: 'XSS_INLINE_EVENT',
            severity: 'CRITICAL',
            element: element.tagName,
            attribute: attr.name,
            value: attr.value,
            timestamp: Date.now()
          };
        }
        
        // Check for javascript: protocol
        if ((attr.name === 'href' || attr.name === 'src') && 
            attr.value.toLowerCase().startsWith('javascript:')) {
          return {
            type: 'XSS_JAVASCRIPT_PROTOCOL',
            severity: 'CRITICAL',
            element: element.tagName,
            attribute: attr.name,
            value: attr.value,
            timestamp: Date.now()
          };
        }
      }

      // Check for dangerous tags
      const dangerousTags = ['SCRIPT', 'IFRAME', 'OBJECT', 'EMBED'];
      if (dangerousTags.includes(element.tagName)) {
        const src = element.src || element.data;
        if (src && !this.isTrustedSource(src)) {
          return {
            type: 'XSS_DANGEROUS_TAG',
            severity: 'CRITICAL',
            element: element.tagName,
            src: src,
            timestamp: Date.now()
          };
        }
      }

      return null;
    }

    blockThreat(threat, node) {
      this.blockedAttempts++;
      threat.blocked = true;
      this.threatLog.push(threat);

      // ACTUALLY REMOVE THE THREAT
      if (node && node.parentNode) {
        node.parentNode.removeChild(node);
      }

      this.log('CRITICAL', `🚨 THREAT BLOCKED: ${threat.type}`, threat);
      
      // Trigger alert
      this.notifyThreat(threat);
    }

    monitorForms() {
      if (typeof document === 'undefined') return;

      document.addEventListener('submit', (e) => {
        const form = e.target;
        const formData = new FormData(form);
        
        for (const [key, value] of formData.entries()) {
          const threat = this.scanInput(value, key);
          if (threat) {
            e.preventDefault();
            e.stopPropagation();
            this.blockFormSubmission(threat, form);
            return false;
          }
        }
      }, true);

      this.log('INFO', 'Form monitoring enabled');
    }

    blockFormSubmission(threat, form) {
      this.blockedAttempts++;
      threat.blocked = true;
      threat.formAction = form.action;
      this.threatLog.push(threat);

      this.log('CRITICAL', `🚨 MALICIOUS FORM BLOCKED: ${threat.type}`, threat);
      this.notifyThreat(threat);

      // Show user warning
      this.showSecurityWarning('Form submission blocked - malicious content detected');
    }

    monitorNavigation() {
      if (typeof window === 'undefined') return;

      // Intercept window.location changes
      const originalLocationSetter = Object.getOwnPropertyDescriptor(window, 'location').set;
      
      Object.defineProperty(window, 'location', {
        set: (value) => {
          const threat = this.validateURL(value);
          if (threat) {
            this.log('CRITICAL', `🚨 BLOCKED redirect to: ${value}`, threat);
            this.notifyThreat(threat);
            return; // Block the navigation
          }
          return originalLocationSetter.call(window, value);
        }
      });

      // Monitor history API
      const originalPushState = history.pushState;
      const originalReplaceState = history.replaceState;

      history.pushState = (...args) => {
        const url = args[2];
        if (url) {
          const threat = this.validateURL(url);
          if (threat) {
            this.log('CRITICAL', `🚨 BLOCKED navigation to: ${url}`, threat);
            return;
          }
        }
        return originalPushState.apply(history, args);
      };

      history.replaceState = (...args) => {
        const url = args[2];
        if (url) {
          const threat = this.validateURL(url);
          if (threat) {
            this.log('CRITICAL', `🚨 BLOCKED navigation to: ${url}`, threat);
            return;
          }
        }
        return originalReplaceState.apply(history, args);
      };

      this.log('INFO', 'Navigation monitoring enabled');
    }

    monitorStorage() {
      if (typeof window === 'undefined') return;

      const monitorStorageAPI = (storage, name) => {
        const originalSetItem = storage.setItem;
        
        storage.setItem = function(key, value) {
          const threat = this.scanInput(value, `${name}.${key}`);
          if (threat) {
            this.log('CRITICAL', `🚨 BLOCKED ${name} write: ${key}`, threat);
            this.notifyThreat(threat);
            return; // Block the write
          }
          return originalSetItem.call(storage, key, value);
        }.bind(this);
      };

      if (window.localStorage) monitorStorageAPI(localStorage, 'localStorage');
      if (window.sessionStorage) monitorStorageAPI(sessionStorage, 'sessionStorage');

      this.log('INFO', 'Storage monitoring enabled');
    }

    monitorConsole() {
      if (typeof console === 'undefined') return;

      const originalLog = console.log;
      const self = this;

      console.log = function(...args) {
        // Detect potential script injection via console
        args.forEach(arg => {
          if (typeof arg === 'string') {
            const threat = self.scanInput(arg, 'console');
            if (threat) {
              self.log('WARNING', 'Suspicious console activity detected', threat);
            }
          }
        });
        return originalLog.apply(console, args);
      };
    }

    scanInput(value, context = 'unknown') {
      if (typeof value !== 'string') return null;

      for (const [category, config] of Object.entries(THREAT_SIGNATURES)) {
        for (const pattern of config.patterns) {
          if (pattern.test(value)) {
            return {
              type: category.toUpperCase(),
              severity: config.severity,
              context: context,
              pattern: pattern.source,
              matched: value.match(pattern)?.[0],
              timestamp: Date.now()
            };
          }
        }
      }

      return null;
    }

    validateURL(url) {
      try {
        const parsed = new URL(url, window.location.href);
        
        // Check for SSRF
        if (PRIVATE_IPS.some(pattern => pattern.test(parsed.hostname))) {
          return {
            type: 'SSRF_PRIVATE_IP',
            severity: 'CRITICAL',
            url: url,
            hostname: parsed.hostname,
            timestamp: Date.now()
          };
        }

        // Check for dangerous ports
        if (BLOCKED_PORTS.includes(parsed.port)) {
          return {
            type: 'SSRF_DANGEROUS_PORT',
            severity: 'HIGH',
            url: url,
            port: parsed.port,
            timestamp: Date.now()
          };
        }

        // Check for data: URIs (can contain XSS)
        if (parsed.protocol === 'data:') {
          return {
            type: 'XSS_DATA_URI',
            severity: 'HIGH',
            url: url,
            timestamp: Date.now()
          };
        }

      } catch (e) {
        return {
          type: 'INVALID_URL',
          severity: 'MEDIUM',
          url: url,
          error: e.message,
          timestamp: Date.now()
        };
      }

      return null;
    }

    isTrustedSource(url) {
      try {
        const parsed = new URL(url, window.location.href);
        const currentOrigin = window.location.origin;
        
        // Same origin is trusted
        if (parsed.origin === currentOrigin) return true;
        
        // Check against trusted origins
        return this.config.trustedOrigins.some(trusted => {
          return parsed.hostname === trusted || parsed.hostname.endsWith('.' + trusted);
        });
      } catch (e) {
        return false;
      }
    }

    notifyThreat(threat) {
      // Trigger custom event for application handling
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('awsg:threat', {
          detail: threat
        }));
      }

      // Call user callback if provided
      if (this.config.onThreatDetected) {
        this.config.onThreatDetected(threat);
      }
    }

    showSecurityWarning(message) {
      if (typeof document === 'undefined') return;

      const warning = document.createElement('div');
      warning.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 15px 20px;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 14px;
        max-width: 300px;
      `;
      warning.innerHTML = `
        <strong>🛡️ Security Alert</strong><br>
        ${message}
      `;

      document.body.appendChild(warning);

      setTimeout(() => {
        warning.style.transition = 'opacity 0.3s';
        warning.style.opacity = '0';
        setTimeout(() => warning.remove(), 300);
      }, 5000);
    }

    log(level, message, data) {
      if (this.config.logLevel === 'silent' && level !== 'CRITICAL') return;
      
      const timestamp = new Date().toISOString();
      const logEntry = {
        timestamp,
        level,
        message,
        data
      };

      if (typeof console !== 'undefined') {
        const style = level === 'CRITICAL' ? 'color: red; font-weight: bold' : 'color: blue';
        console.log(`%c[AWSG ${level}] ${message}`, style, data || '');
      }
    }

    getMetrics() {
      return {
        active: this.isActive,
        blockedAttempts: this.blockedAttempts,
        totalThreats: this.threatLog.length,
        recentThreats: this.threatLog.slice(-10),
        threatsByType: this.getThreatsByType(),
        uptime: Date.now() - this.startTime
      };
    }

    getThreatsByType() {
      const counts = {};
      this.threatLog.forEach(threat => {
        counts[threat.type] = (counts[threat.type] || 0) + 1;
      });
      return counts;
    }
  }

  // ============================================================================
  // NETWORK REQUEST INTERCEPTOR (Works Offline)
  // ============================================================================

  class NetworkGuard {
    constructor(config, monitor) {
      this.config = config;
      this.monitor = monitor;
      this.interceptFetch();
      this.interceptXHR();
    }

    interceptFetch() {
      if (typeof window === 'undefined' || !window.fetch) return;

      const originalFetch = window.fetch;
      const self = this;

      window.fetch = function(url, options = {}) {
        // Validate URL
        const urlThreat = self.monitor.validateURL(url);
        if (urlThreat) {
          self.monitor.log('CRITICAL', `🚨 BLOCKED fetch to: ${url}`, urlThreat);
          self.monitor.notifyThreat(urlThreat);
          return Promise.reject(new Error(`AWSG: Request blocked - ${urlThreat.type}`));
        }

        // Scan request body
        if (options.body) {
          let bodyData = options.body;
          
          if (typeof bodyData === 'string') {
            try {
              bodyData = JSON.parse(bodyData);
            } catch (e) {
              // Not JSON, scan as string
            }
          }

          const bodyThreat = self.scanRequestData(bodyData, url);
          if (bodyThreat) {
            self.monitor.log('CRITICAL', `🚨 BLOCKED request body to: ${url}`, bodyThreat);
            self.monitor.notifyThreat(bodyThreat);
            return Promise.reject(new Error(`AWSG: Request blocked - ${bodyThreat.type}`));
          }
        }

        // Execute original fetch
        return originalFetch.call(this, url, options);
      };

      self.monitor.log('INFO', 'Fetch interception enabled');
    }

    interceptXHR() {
      if (typeof window === 'undefined' || !window.XMLHttpRequest) return;

      const originalOpen = XMLHttpRequest.prototype.open;
      const originalSend = XMLHttpRequest.prototype.send;
      const self = this;

      XMLHttpRequest.prototype.open = function(method, url, ...args) {
        this._awsgURL = url;
        this._awsgMethod = method;
        
        const urlThreat = self.monitor.validateURL(url);
        if (urlThreat) {
          self.monitor.log('CRITICAL', `🚨 BLOCKED XHR to: ${url}`, urlThreat);
          self.monitor.notifyThreat(urlThreat);
          throw new Error(`AWSG: Request blocked - ${urlThreat.type}`);
        }

        return originalOpen.apply(this, [method, url, ...args]);
      };

      XMLHttpRequest.prototype.send = function(data) {
        if (data) {
          const bodyThreat = self.scanRequestData(data, this._awsgURL);
          if (bodyThreat) {
            self.monitor.log('CRITICAL', `🚨 BLOCKED XHR body to: ${this._awsgURL}`, bodyThreat);
            self.monitor.notifyThreat(bodyThreat);
            throw new Error(`AWSG: Request blocked - ${bodyThreat.type}`);
          }
        }

        return originalSend.apply(this, arguments);
      };

      self.monitor.log('INFO', 'XHR interception enabled');
    }

    scanRequestData(data, url) {
      const scanDeep = (obj, path = []) => {
        if (typeof obj === 'string') {
          return this.monitor.scanInput(obj, `request:${url}:${path.join('.')}`);
        }

        if (typeof obj === 'object' && obj !== null) {
          // Check for prototype pollution
          if ('__proto__' in obj || 'constructor' in obj || 'prototype' in obj) {
            return {
              type: 'PROTOTYPE_POLLUTION',
              severity: 'CRITICAL',
              path: path.join('.'),
              timestamp: Date.now()
            };
          }

          for (const key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
              const result = scanDeep(obj[key], [...path, key]);
              if (result) return result;
            }
          }
        }

        return null;
      };

      return scanDeep(data);
    }
  }

  // ============================================================================
  // MAIN SECURITY GATEWAY
  // ============================================================================

  class AutonomousSecurityGateway {
    constructor(config) {
      this.config = this.validateConfig(config);
      this.startTime = Date.now();
      
      // Initialize monitoring
      this.monitor = new ThreatMonitor(this.config);
      
      // Initialize network guard
      this.networkGuard = new NetworkGuard(this.config, this.monitor);
      
      // Apply security hardening
      this.hardenEnvironment();
      
      this.log('INFO', `🛡️ AWSG v${VERSION} - Autonomous Protection ACTIVE`);
      this.log('INFO', `Monitoring: DOM, Forms, Navigation, Storage, Network`);
      this.log('INFO', `Status: ONLINE - Protection works even if server is offline`);
    }

    validateConfig(config) {
      const defaults = {
        appId: 'awsg-app',
        logLevel: 'warn',
        trustedOrigins: [],
        onThreatDetected: null,
        autoBlock: true,
        showWarnings: true
      };

      const merged = { ...defaults, ...config };

      // Add current origin to trusted
      if (typeof window !== 'undefined') {
        const currentHost = window.location.hostname;
        if (!merged.trustedOrigins.includes(currentHost)) {
          merged.trustedOrigins.push(currentHost);
        }
      }

      return Object.freeze(merged);
    }

    hardenEnvironment() {
      if (typeof window === 'undefined') return;

      // Prevent eval
      try {
        window.eval = function() {
          throw new Error('AWSG: eval() is disabled for security');
        };
      } catch (e) {}

      // Prevent setTimeout with string
      const originalSetTimeout = window.setTimeout;
      window.setTimeout = function(fn, delay, ...args) {
        if (typeof fn === 'string') {
          throw new Error('AWSG: setTimeout with string is disabled');
        }
        return originalSetTimeout(fn, delay, ...args);
      };

      // Prevent setInterval with string
      const originalSetInterval = window.setInterval;
      window.setInterval = function(fn, delay, ...args) {
        if (typeof fn === 'string') {
          throw new Error('AWSG: setInterval with string is disabled');
        }
        return originalSetInterval(fn, delay, ...args);
      };

      this.log('INFO', 'Environment hardening complete');
    }

    // Public API
    getStatus() {
      return {
        version: VERSION,
        active: this.monitor.isActive,
        uptime: Date.now() - this.startTime,
        metrics: this.monitor.getMetrics()
      };
    }

    getThreatLog() {
      return [...this.monitor.threatLog];
    }

    clearThreatLog() {
      this.monitor.threatLog = [];
      this.monitor.blockedAttempts = 0;
    }

    onThreat(callback) {
      this.config.onThreatDetected = callback;
    }

    log(level, message, data) {
      this.monitor.log(level, message, data);
    }
  }

  // ============================================================================
  // FACTORY & EXPORTS
  // ============================================================================

  function createSecurityGateway(config) {
    return new AutonomousSecurityGateway(config);
  }

  // UMD Export
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = createSecurityGateway;
  } else if (typeof define === 'function' && define.amd) {
    define(function() { return createSecurityGateway; });
  } else {
    global.createSecurityGateway = createSecurityGateway;
    global.AWSG = AutonomousSecurityGateway;
  }

})(typeof window !== 'undefined' ? window : global);
