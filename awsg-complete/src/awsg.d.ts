/**
 * AWSG TypeScript Definitions
 * Type definitions for the Adaptive Web Security Gateway
 */

declare module 'awsg' {
  /**
   * Configuration options for the security gateway
   */
  export interface SecurityConfig {
    /** Unique identifier for your application */
    appId: string;
    
    /** Logging level: 'silent' | 'warn' | 'debug' */
    logLevel?: 'silent' | 'warn' | 'debug';
    
    /** Array of high-risk URL paths that require extra scrutiny */
    dangerZone?: string[];
    
    /** Array of trusted origin domains for CORS and redirects */
    trustedOrigins?: string[];
    
    /** Maximum risk score before blocking (0-100) */
    maxRiskScore?: number;
    
    /** Automatically generate Content Security Policy headers */
    autoCSP?: boolean;
    
    /** Enable behavioral analysis and anomaly detection */
    behavioral?: boolean;
  }

  /**
   * Threat detection result
   */
  export interface ThreatDetectionResult {
    /** Whether a threat was detected */
    detected: boolean;
    
    /** Risk score from 0-100 */
    score: number;
    
    /** Type of threat detected */
    type?: 'XSS' | 'SQLi' | 'NoSQLi' | 'SSRF' | 'PrototypePollution' | 'OpenRedirect';
    
    /** Array of pattern matches */
    matches?: Array<{
      pattern: string;
      match: string;
    }>;
    
    /** Reason for detection */
    reason?: string;
    
    /** Path to the polluted property (for prototype pollution) */
    path?: string;
  }

  /**
   * Comprehensive scan result
   */
  export interface ScanResult {
    /** Whether the input is safe */
    safe: boolean;
    
    /** Overall risk score */
    riskScore: number;
    
    /** Array of detected threats */
    threats: ThreatDetectionResult[];
    
    /** Time taken to scan (milliseconds) */
    duration: number;
    
    /** Timestamp of the scan */
    timestamp: number;
  }

  /**
   * Behavioral profile data
   */
  export interface BehaviorProfile {
    /** Average mouse movement entropy */
    mouseEntropy: number;
    
    /** Average keystroke timing in milliseconds */
    keystrokeAvg: number;
    
    /** Unique session fingerprint */
    sessionFingerprint: string;
    
    /** Whether still in learning mode */
    learning: boolean;
  }

  /**
   * Request metrics
   */
  export interface RequestMetrics {
    /** Total number of requests processed */
    totalRequests: number;
    
    /** Average request processing duration */
    averageDuration: string;
    
    /** Number of threats blocked */
    threats: number;
  }

  /**
   * Complete metrics object
   */
  export interface Metrics {
    /** AWSG version */
    version: string;
    
    /** Current configuration */
    config: {
      appId: string;
      dangerZone: string[];
      maxRiskScore: number;
    };
    
    /** Request processing metrics */
    requests: RequestMetrics;
    
    /** Behavioral analysis data */
    behavior: BehaviorProfile;
  }

  /**
   * Main Security Gateway class
   */
  export class SecurityGateway {
    /** Gateway configuration */
    readonly config: Readonly<SecurityConfig>;
    
    /** Threat detector instance */
    readonly detector: ThreatDetector;
    
    /** CSRF protection instance */
    readonly csrf: CSRFProtection;
    
    /** Behavioral monitor instance */
    readonly monitor: BehaviorMonitor;
    
    /** Request proxy instance */
    readonly proxy: RequestProxy;
    
    constructor(config: SecurityConfig);
    
    /**
     * Wrap the native fetch function with security checks
     * @param originalFetch - The original fetch function to wrap
     * @returns Wrapped fetch function
     */
    proxyFetch(originalFetch: typeof fetch): typeof fetch;
    
    /**
     * Sanitize potentially dangerous input
     * @param input - String or object to sanitize
     * @returns Sanitized input or null if cannot be sanitized
     */
    sanitize(input: string | object): string | null;
    
    /**
     * Get the current CSRF token
     * @returns CSRF token string
     */
    getCSRFToken(): string;
    
    /**
     * Get the current behavioral profile
     * @returns Behavioral profile data
     */
    getBehaviorProfile(): BehaviorProfile;
    
    /**
     * Get comprehensive metrics
     * @returns Metrics object
     */
    getMetrics(): Metrics;
    
    /**
     * Export security log as JSON
     * @returns JSON string of security events
     */
    exportLog(): string;
  }

  /**
   * Threat detection engine
   */
  export class ThreatDetector {
    constructor(config: SecurityConfig);
    
    /**
     * Detect XSS attacks in input
     * @param input - String to scan
     * @returns Detection result
     */
    detectXSS(input: string): ThreatDetectionResult;
    
    /**
     * Detect SQL injection in input
     * @param input - String to scan
     * @returns Detection result
     */
    detectSQLi(input: string): ThreatDetectionResult;
    
    /**
     * Detect NoSQL injection in input
     * @param input - String to scan
     * @returns Detection result
     */
    detectNoSQLi(input: string): ThreatDetectionResult;
    
    /**
     * Detect SSRF attempts in URLs
     * @param url - URL to validate
     * @returns Detection result
     */
    detectSSRF(url: string): ThreatDetectionResult;
    
    /**
     * Detect prototype pollution in objects
     * @param obj - Object to scan
     * @param path - Current property path (internal use)
     * @returns Detection result
     */
    detectPrototypePollution(obj: any, path?: string[]): ThreatDetectionResult;
    
    /**
     * Detect open redirect vulnerabilities
     * @param url - URL to validate
     * @param trustedOrigins - Array of trusted origins
     * @returns Detection result
     */
    detectOpenRedirect(url: string, trustedOrigins: string[]): ThreatDetectionResult;
    
    /**
     * Perform comprehensive scan on input
     * @param data - Data to scan (string or object)
     * @param context - Additional context for scanning
     * @returns Comprehensive scan result
     */
    scan(data: string | object, context?: { type?: string }): ScanResult;
  }

  /**
   * CSRF protection module
   */
  export class CSRFProtection {
    constructor(config: SecurityConfig);
    
    /**
     * Get the current CSRF token
     * @returns CSRF token
     */
    getToken(): string;
    
    /**
     * Validate request origin
     * @param origin - Request origin header
     * @param referer - Request referer header
     * @returns Whether origin is valid
     */
    validateOrigin(origin: string | null, referer: string | null): boolean;
    
    /**
     * Validate CSRF token
     * @param token - Token to validate
     * @returns Whether token is valid
     */
    validateToken(token: string): boolean;
    
    /**
     * Inject CSRF token into request
     * @param request - Request object to modify
     * @returns Modified request
     */
    injectToken(request: { headers?: Record<string, string> }): any;
  }

  /**
   * Behavioral monitoring and anomaly detection
   */
  export class BehaviorMonitor {
    constructor(config: SecurityConfig);
    
    /**
     * Get current behavioral profile
     * @returns Profile data
     */
    getProfile(): BehaviorProfile;
    
    /**
     * Analyze current behavior for anomalies
     * @returns Anomaly score (0-100)
     */
    analyzeAnomaly(): number;
  }

  /**
   * Request proxy for fetch interception
   */
  export class RequestProxy {
    constructor(
      config: SecurityConfig,
      detector: ThreatDetector,
      csrf: CSRFProtection,
      monitor: BehaviorMonitor
    );
    
    /**
     * Create proxied fetch function
     * @param originalFetch - Original fetch to wrap
     * @returns Proxied fetch function
     */
    proxyFetch(originalFetch: typeof fetch): typeof fetch;
    
    /**
     * Get request processing metrics
     * @returns Metrics object
     */
    getMetrics(): RequestMetrics;
  }

  /**
   * Factory function to create security gateway instance
   * @param config - Configuration options
   * @returns SecurityGateway instance
   */
  export default function createSecurityGateway(config: SecurityConfig): SecurityGateway;
}

/**
 * Global type augmentation for when AWSG is loaded via script tag
 */
declare global {
  interface Window {
    createSecurityGateway: typeof import('awsg').default;
    AWSG: typeof import('awsg').SecurityGateway;
    __security?: import('awsg').SecurityGateway;
  }
}

export {};
