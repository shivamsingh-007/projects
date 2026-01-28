# 🔧 Troubleshooting Guide

Common issues and their solutions for the OTP Authenticator System.

## Table of Contents
- [Database Issues](#database-issues)
- [Email Issues](#email-issues)
- [SMS/Twilio Issues](#smstwilio-issues)
- [Authentication Issues](#authentication-issues)
- [Rate Limiting Issues](#rate-limiting-issues)
- [Frontend Issues](#frontend-issues)
- [Deployment Issues](#deployment-issues)

---

## Database Issues

### "Cannot connect to MongoDB"

**Symptoms:**
```
MongooseServerSelectionError: connect ECONNREFUSED 127.0.0.1:27017
```

**Solutions:**

1. **Check if MongoDB is running:**
```bash
# Linux/Ubuntu
sudo systemctl status mongodb
sudo systemctl start mongodb

# macOS
brew services list
brew services start mongodb-community

# Windows
net start MongoDB
```

2. **Verify connection string in .env:**
```env
# Local MongoDB
MONGODB_URI=mongodb://localhost:27017/otp-authenticator

# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/otp-authenticator
```

3. **For MongoDB Atlas:**
   - Whitelist your IP in Network Access
   - Check credentials are correct
   - Ensure cluster is active

4. **Test connection:**
```bash
# Using mongosh
mongosh "mongodb://localhost:27017"

# Using MongoDB Compass
# Connect to: mongodb://localhost:27017
```

### "Authentication failed"

**Symptoms:**
```
MongoServerError: Authentication failed
```

**Solutions:**

1. **Check credentials:**
```env
# Ensure username and password are correct
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/dbname
```

2. **URL encode special characters:**
```javascript
// If password contains special characters like @, #, $
// Use encodeURIComponent() or URL encode manually
// @ -> %40
// # -> %23
```

3. **Verify database user exists in Atlas:**
   - Go to Database Access
   - Check user has read/write permissions

---

## Email Issues

### Gmail - "Email not sending"

**Symptoms:**
- No email received
- Error: "Invalid login"
- Error: "Less secure app access"

**Solutions:**

1. **Use App Password (REQUIRED):**
```
Step 1: Enable 2-Factor Authentication
  - Go to: https://myaccount.google.com/security
  - Enable "2-Step Verification"

Step 2: Generate App Password
  - Go to: https://myaccount.google.com/apppasswords
  - Select: Mail + Other (Custom name)
  - Copy the 16-character password
  - Use in .env (without spaces):

EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop
```

2. **Verify Gmail settings:**
```bash
# Test SMTP connection
telnet smtp.gmail.com 587
```

3. **Check spam folder** - emails might be marked as spam initially

4. **Enable less secure apps (if App Password doesn't work):**
   - Go to: https://myaccount.google.com/lesssecureapps
   - Turn on (not recommended for production)

### Using Different Email Provider

**For SendGrid:**

1. Install package:
```bash
npm install @sendgrid/mail
```

2. Update `backend/config/email.js`:
```javascript
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const sendOTPEmail = async (email, otp, name) => {
  const msg = {
    to: email,
    from: process.env.EMAIL_USER,
    subject: 'Email Verification - OTP Code',
    html: `Your OTP is: ${otp}`,
  };
  
  await sgMail.send(msg);
};
```

**For AWS SES:**

1. Install AWS SDK:
```bash
npm install aws-sdk
```

2. Configure credentials and update email.js accordingly

### "Email takes too long to arrive"

**Solutions:**

1. **Check email server logs:**
```bash
# In development mode, check backend console
# It will show: "Email sent: <message-id>"
```

2. **Verify SMTP connection:**
   - Test with different email provider
   - Check firewall settings
   - Verify port 587 or 465 is open

---

## SMS/Twilio Issues

### "SMS not received"

**Symptoms:**
- No SMS received
- Error: "Unable to create record"
- Error: "Phone number not verified"

**Solutions:**

1. **For Trial Accounts - Verify phone number:**
```
Step 1: Go to Twilio Console
Step 2: Phone Numbers → Verified Caller IDs
Step 3: Click "+ Add" and verify your number
Step 4: Can only send to verified numbers on trial
```

2. **Check phone number format:**
```javascript
// CORRECT - E.164 format
"+1234567890"  // US
"+918876543210"  // India
"+447700900000"  // UK

// INCORRECT
"1234567890"  // Missing +
"(123) 456-7890"  // Contains formatting
```

3. **Verify Twilio credentials in .env:**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

4. **Check Twilio balance:**
   - Go to Console → Billing
   - Trial accounts get $15 credit
   - Upgrade for production use

5. **Verify Twilio phone number:**
   - Must be a verified Twilio number
   - Must have SMS capability
   - Check in: Phone Numbers → Manage → Active Numbers

### "Invalid 'To' Phone Number"

**Solution:**
```javascript
// Validate format before sending
const validateMobile = (mobile) => {
  const phoneRegex = /^\+?[1-9]\d{1,14}$/;
  return phoneRegex.test(mobile);
};

// Usage
if (!validateMobile(mobile)) {
  throw new Error('Invalid phone number format. Use E.164 format.');
}
```

### "Insufficient funds"

**Solution:**
- Add credits to Twilio account
- Upgrade from trial to paid account

---

## Authentication Issues

### "Not authorized, no token"

**Symptoms:**
```json
{
  "success": false,
  "message": "Not authorized, no token"
}
```

**Solutions:**

1. **Include token in request:**
```javascript
// Frontend
const token = localStorage.getItem('token');

fetch('/api/auth/profile', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

2. **Check token exists:**
```javascript
if (!token) {
  console.error('No token found');
  // Redirect to login
}
```

### "Not authorized, token failed"

**Symptoms:**
- 401 Unauthorized
- "jwt expired" or "invalid token"

**Solutions:**

1. **Token expired:**
```javascript
// Tokens expire after 30 days (default)
// User needs to login again
// Check expiration in JWT_SECRET config
```

2. **Invalid JWT_SECRET:**
```env
# Ensure same secret in both dev and prod
JWT_SECRET=your_consistent_secret_key_here
```

3. **Token format:**
```javascript
// Must be: "Bearer <token>"
// NOT: "<token>" or "bearer <token>"
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Rate Limiting Issues

### "Too many requests"

**Symptoms:**
```json
{
  "success": false,
  "message": "Too many OTP requests. Please try again after an hour."
}
```

**Solutions:**

1. **Wait for cooldown period:**
   - Signup: 1 hour (5 requests max)
   - OTP: 1 hour (3 requests max)
   - Verification: 1 hour (10 attempts max)

2. **For development, adjust limits:**

Edit `backend/middleware/rateLimiter.js`:
```javascript
const otpLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,  // Change to 5 minutes: 5 * 60 * 1000
  max: 10,  // Increase to 10 attempts
  // ...
});
```

3. **For production:**
   - Use Redis for distributed rate limiting
   - Implement user-specific rate limits
   - Monitor abuse patterns

4. **Clear rate limit (development only):**
```javascript
// In your route, temporarily disable:
// router.post('/resend-otp', /* otpLimiter, */ async (req, res) => {
```

---

## Frontend Issues

### "CORS Error"

**Symptoms:**
```
Access to fetch at 'http://localhost:5000/api/auth/signup' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Solutions:**

1. **Update FRONTEND_URL in backend/.env:**
```env
FRONTEND_URL=http://localhost:3000
```

2. **Check CORS configuration in server.js:**
```javascript
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}));
```

3. **For production:**
```env
FRONTEND_URL=https://your-production-domain.com
```

### "Network Error" / "Failed to fetch"

**Solutions:**

1. **Verify backend is running:**
```bash
curl http://localhost:5000/health
```

2. **Check API URL in frontend:**
```javascript
// frontend/src/services/api.js
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
});
```

3. **Add to frontend .env.local:**
```env
REACT_APP_API_URL=http://localhost:5000/api
```

### "Cannot read property of undefined"

**Symptoms:**
- Frontend crashes
- Console error about undefined properties

**Solutions:**

1. **Check API response format:**
```javascript
// Always check response exists
const response = await authAPI.signup(data);
if (response && response.data) {
  // Use response.data
}
```

2. **Add error boundaries:**
```jsx
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

---

## Deployment Issues

### Heroku - "Application error"

**Solutions:**

1. **Check logs:**
```bash
heroku logs --tail
```

2. **Verify all environment variables:**
```bash
heroku config
```

3. **Check Procfile exists:**
```
web: node backend/server.js
```

4. **Ensure PORT is from env:**
```javascript
const PORT = process.env.PORT || 5000;
```

### Vercel - "Build failed"

**Solutions:**

1. **Check build logs in Vercel dashboard**

2. **Verify build command:**
```json
{
  "scripts": {
    "build": "react-scripts build"
  }
}
```

3. **Set environment variables in Vercel:**
   - Go to Project Settings → Environment Variables
   - Add REACT_APP_API_URL

### Docker - "Container exits immediately"

**Solutions:**

1. **Check Docker logs:**
```bash
docker-compose logs
```

2. **Verify environment variables in docker-compose.yml**

3. **Test build separately:**
```bash
docker build -t otp-backend ./backend
docker run -it otp-backend
```

---

## General Debugging Tips

### Enable Debug Mode

1. **Backend:**
```javascript
// Add to server.js
if (process.env.NODE_ENV === 'development') {
  app.use((req, res, next) => {
    console.log(`${req.method} ${req.path}`, req.body);
    next();
  });
}
```

2. **Frontend:**
```javascript
// Add console logs
console.log('API Response:', response);
console.log('User Data:', userData);
```

### Check Environment Variables

```bash
# Backend
cd backend
node -e "require('dotenv').config(); console.log(process.env)"

# Frontend
cd frontend
npm run start | grep REACT_APP_
```

### Test API with cURL

```bash
# Health check
curl http://localhost:5000/health

# Signup
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","mobile":"+1234567890","password":"Test123"}'
```

### Database Debugging

```bash
# Connect to MongoDB
mongosh "mongodb://localhost:27017/otp-authenticator"

# List users
db.users.find().pretty()

# List OTPs
db.otps.find().pretty()

# Delete test data
db.users.deleteMany({})
db.otps.deleteMany({})
```

---

## Still Having Issues?

1. **Check the README.md** for setup instructions
2. **Review API.md** for endpoint documentation
3. **Read INTEGRATION.md** for integration examples
4. **Check GitHub Issues** (if using version control)
5. **Enable debug logging** and check console output
6. **Test with Postman** to isolate frontend vs backend issues

---

## Get Help

If you're still stuck:

1. Provide:
   - Error message (full stack trace)
   - Environment (OS, Node version, MongoDB version)
   - Steps to reproduce
   - What you've tried

2. Check:
   - All environment variables are set
   - Services are running (MongoDB, backend, frontend)
   - Ports are not in use by other applications
   - Firewall is not blocking connections

---

**Remember:** Most issues are configuration-related. Double-check your .env file! 🔍
