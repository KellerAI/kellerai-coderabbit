# KellerAI Security Standards
# Version: 1.0
# Last Updated: 2025-10-14

## Security Checklist for Code Reviews

### Authentication and Authorization

- [ ] All API endpoints require authentication (except public endpoints)
- [ ] JWT tokens have appropriate expiration times (access: 15min, refresh: 7 days)
- [ ] JWT secrets are strong (min 32 characters) and stored securely
- [ ] Password hashing uses bcrypt or Argon2 (never MD5/SHA1)
- [ ] Multi-factor authentication implemented for sensitive operations
- [ ] Role-based access control (RBAC) properly enforced
- [ ] Session management follows best practices (secure cookies, timeout)
- [ ] API keys rotated regularly and stored encrypted

### Input Validation

- [ ] All user inputs validated before processing
- [ ] Input validation uses schema validation (Zod, Joi, Pydantic)
- [ ] File uploads validate type, size, and content
- [ ] SQL queries use parameterized statements (no string interpolation)
- [ ] NoSQL queries sanitized to prevent injection
- [ ] API rate limiting configured appropriately
- [ ] Request size limits enforced
- [ ] Content-Type headers validated

### Data Protection

- [ ] Sensitive data encrypted at rest (PII, credentials, tokens)
- [ ] TLS/HTTPS enforced for all communications
- [ ] No secrets in code, logs, or version control
- [ ] Environment variables for all sensitive configuration
- [ ] Database backups encrypted
- [ ] PII handling complies with GDPR/privacy regulations
- [ ] Data retention policies implemented
- [ ] Secure password reset flows

### Error Handling

- [ ] No sensitive information in error messages
- [ ] Stack traces disabled in production
- [ ] Proper HTTP status codes used
- [ ] Error logging includes context but no secrets
- [ ] User-friendly error messages
- [ ] Security events logged for audit

### Dependencies and Infrastructure

- [ ] All dependencies pinned to specific versions
- [ ] Regular security updates applied
- [ ] Automated vulnerability scanning enabled (Dependabot, Snyk)
- [ ] Container images from trusted sources only
- [ ] Non-root users in containers
- [ ] Resource limits configured
- [ ] Network segmentation implemented
- [ ] Secrets management solution used (Vault, AWS Secrets Manager)

### Code Security

- [ ] No hardcoded credentials or API keys
- [ ] CORS properly configured (specific origins, not '*')
- [ ] Security headers configured (Helmet, CSP)
- [ ] XSS prevention measures in place
- [ ] CSRF protection enabled
- [ ] Click-jacking prevention
- [ ] Secure random number generation for crypto operations
- [ ] No eval() or similar dangerous functions

## OWASP Top 10 Compliance

### A01:2021 - Broken Access Control

**Prevention**:
```typescript
// ✅ Verify authorization on EVERY request
app.get('/api/users/:id', authenticateToken, async (req, res) => {
  // Check if user can access this resource
  if (req.user.id !== req.params.id && req.user.role !== 'admin') {
    throw new ForbiddenError('Cannot access other users');
  }

  const user = await userService.getUser(req.params.id);
  res.json(user);
});

// ❌ Missing authorization check
app.get('/api/users/:id', authenticateToken, async (req, res) => {
  // No check if user can access this resource
  const user = await userService.getUser(req.params.id);
  res.json(user);
});
```

### A02:2021 - Cryptographic Failures

**Prevention**:
```python
# ✅ Strong cryptography
from cryptography.fernet import Fernet
import bcrypt

# Encrypt sensitive data at rest
key = os.environ['ENCRYPTION_KEY']
cipher = Fernet(key)
encrypted_data = cipher.encrypt(sensitive_data.encode())

# Hash passwords with strong algorithm
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# ❌ Weak cryptography
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # NEVER use MD5
```

### A03:2021 - Injection

**Prevention**:
```typescript
// ✅ Parameterized queries (Prisma handles this)
await prisma.user.findMany({
  where: { email: userEmail }
});

// ❌ String interpolation
await prisma.$queryRaw`SELECT * FROM users WHERE email = '${userEmail}'`;

// ✅ Input validation
const UserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100).regex(/^[a-zA-Z\s]+$/),
});
```

### A04:2021 - Insecure Design

**Prevention**:
- Implement threat modeling in design phase
- Use secure design patterns (defense in depth, least privilege)
- Regular security architecture reviews
- Rate limiting on all public endpoints
- Circuit breakers for external service calls

### A05:2021 - Security Misconfiguration

**Prevention**:
```typescript
// ✅ Secure configuration
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
  },
}));

// Disable debug mode in production
if (process.env.NODE_ENV === 'production') {
  app.set('x-powered-by', false);
}

// ❌ Insecure configuration
app.use(cors({ origin: '*' })); // Allow all origins
app.set('trust proxy', true); // Without understanding implications
```

### A06:2021 - Vulnerable and Outdated Components

**Prevention**:
- Use Dependabot/Renovate for automated dependency updates
- Regular `npm audit` / `pip-audit` scans
- Pin dependencies to specific versions
- Review dependency licenses
- Remove unused dependencies

### A07:2021 - Identification and Authentication Failures

**Prevention**:
```typescript
// ✅ Secure authentication
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  skipSuccessfulRequests: true,
});

app.post('/api/auth/login', authLimiter, async (req, res) => {
  const { email, password } = req.body;

  const user = await userService.findByEmail(email);
  if (!user) {
    // Use same error message to prevent user enumeration
    throw new UnauthorizedError('Invalid credentials');
  }

  const validPassword = await bcrypt.compare(password, user.passwordHash);
  if (!validPassword) {
    throw new UnauthorizedError('Invalid credentials');
  }

  // Generate secure tokens
  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  res.json({ accessToken, refreshToken });
});
```

### A08:2021 - Software and Data Integrity Failures

**Prevention**:
- Use package lock files (`package-lock.json`, `poetry.lock`)
- Verify package signatures
- Implement CI/CD pipeline security
- Code signing for deployments
- Integrity checks for downloaded files

### A09:2021 - Security Logging and Monitoring Failures

**Prevention**:
```typescript
// ✅ Comprehensive security logging
logger.warn('Failed login attempt', {
  email: req.body.email,
  ip: req.ip,
  userAgent: req.headers['user-agent'],
  timestamp: new Date().toISOString(),
});

// Log all security-sensitive operations
logger.info('User role changed', {
  userId: user.id,
  oldRole: oldRole,
  newRole: newRole,
  changedBy: req.user.id,
});

// Set up alerts for suspicious activity
if (failedAttempts > 10) {
  alertService.send({
    severity: 'HIGH',
    message: 'Multiple failed login attempts',
    ip: req.ip,
  });
}
```

### A10:2021 - Server-Side Request Forgery (SSRF)

**Prevention**:
```typescript
// ✅ Validate and whitelist URLs
const ALLOWED_DOMAINS = [
  'api.kellerai.com',
  's3.amazonaws.com',
];

async function fetchExternalResource(url: string) {
  const parsedUrl = new URL(url);

  if (!ALLOWED_DOMAINS.includes(parsedUrl.hostname)) {
    throw new ValidationError('Invalid domain');
  }

  if (parsedUrl.protocol !== 'https:') {
    throw new ValidationError('Only HTTPS allowed');
  }

  return fetch(url);
}

// ❌ Unvalidated URL fetch
async function fetchExternalResource(url: string) {
  return fetch(url); // Vulnerable to SSRF
}
```

## Secrets Management

### Environment Variables
```bash
# .env.example
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-your-api-key

# Never commit .env file
# Add to .gitignore
.env
.env.local
.env.*.local
```

### Secrets Rotation
- Rotate JWT secrets quarterly
- Rotate API keys monthly
- Rotate database credentials quarterly
- Automated rotation via secrets management service

## Security Testing

### Automated Security Scanning
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
```

### Manual Security Testing
- Quarterly penetration testing
- Annual security audit by third party
- Bug bounty program for responsible disclosure

---

**Version**: 1.0
**Last Updated**: 2025-10-14
**Review Frequency**: Quarterly
**Owner**: Security Team
