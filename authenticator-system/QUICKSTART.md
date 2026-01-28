# Quick Reference Guide

## 🚀 Quick Start Commands

### Setup (First Time)
```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Or manually:
cd backend && npm install
cd ../frontend && npm install
```

### Configure Environment
```bash
cd backend
cp ../.env.example .env
nano .env  # Edit with your credentials
```

### Run Locally
```bash
# Terminal 1 - Backend
cd backend
npm start

# Terminal 2 - Frontend  
cd frontend
npm start
```

### Run with Docker
```bash
docker-compose up
```

---

## 📝 Required Environment Variables

```env
# Database
MONGODB_URI=mongodb://localhost:27017/otp-authenticator

# JWT
JWT_SECRET=your_super_secret_key_change_this

# Email (Gmail)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Twilio (SMS)
TWILIO_ACCOUNT_SID=ACxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## 🔑 Getting API Keys

### MongoDB Atlas
1. Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Create free cluster
3. Get connection string
4. Whitelist IP: 0.0.0.0/0 (for development)

### Gmail App Password
1. Enable 2FA: [myaccount.google.com/security](https://myaccount.google.com/security)
2. Generate: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Select: Mail + Other (Custom)
4. Copy 16-character password

### Twilio
1. Sign up: [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Get $15 free credit
3. Find credentials: [console.twilio.com](https://console.twilio.com/)
4. Buy/get phone number
5. For trial: Verify recipient numbers first

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/signup` | Register user & send OTP | No |
| POST | `/api/auth/verify-otp` | Verify OTP codes | No |
| POST | `/api/auth/resend-otp` | Resend OTP | No |
| GET | `/api/auth/status/:userId` | Check status | No |
| GET | `/api/auth/profile` | Get profile | Yes |

---

## 💻 Code Examples

### JavaScript/Fetch
```javascript
// Signup
const response = await fetch('http://localhost:5000/api/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    mobile: '+1234567890',
    password: 'Test123'
  })
});
const data = await response.json();
console.log('User ID:', data.data.user.id);

// Verify OTP
const verifyResponse = await fetch('http://localhost:5000/api/auth/verify-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    userId: data.data.user.id,
    emailOTP: '123456',
    mobileOTP: '789012'
  })
});
```

### Python
```python
import requests

# Signup
response = requests.post('http://localhost:5000/api/auth/signup', json={
    'name': 'John Doe',
    'email': 'john@example.com',
    'mobile': '+1234567890',
    'password': 'Test123'
})
user_id = response.json()['data']['user']['id']

# Verify OTP
verify = requests.post('http://localhost:5000/api/auth/verify-otp', json={
    'userId': user_id,
    'emailOTP': '123456',
    'mobileOTP': '789012'
})
```

### cURL
```bash
# Signup
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@test.com","mobile":"+1234567890","password":"Test123"}'

# Verify
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"userId":"USER_ID","emailOTP":"123456","mobileOTP":"789012"}'
```

---

## 🔧 Common Commands

### Development
```bash
# Backend with hot reload
cd backend
npm run dev

# Frontend
cd frontend
npm start

# Check health
curl http://localhost:5000/health
```

### Database
```bash
# Connect to MongoDB
mongosh "mongodb://localhost:27017/otp-authenticator"

# View collections
db.users.find().pretty()
db.otps.find().pretty()

# Clear data
db.users.deleteMany({})
db.otps.deleteMany({})
```

### Docker
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Clean up
docker-compose down -v
```

---

## 🐛 Quick Fixes

### Email not sending
```bash
# Use Gmail App Password (not regular password)
# Enable 2FA first, then generate App Password
```

### SMS not sending
```bash
# For Twilio trial: Verify recipient number first
# Check number format: +1234567890 (E.164)
```

### MongoDB connection error
```bash
# Start MongoDB
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # macOS

# Or use MongoDB Atlas cloud
```

### CORS error
```bash
# Update backend/.env
FRONTEND_URL=http://localhost:3000
```

### Rate limit exceeded
```bash
# Wait 1 hour, or adjust limits in:
# backend/middleware/rateLimiter.js
```

---

## 📊 Verification Flow

```
1. User fills signup form
   ↓
2. System sends OTP to email + mobile
   ↓
3. User enters both OTPs
   ↓
4. System verifies codes
   ↓
5. Status: "Verified" ✓
```

**Statuses:**
- **Not Verified** - Neither email nor mobile verified
- **Pending** - One verified, one remaining
- **Verified** - Both email and mobile verified ✓

---

## 🔒 Security Features

- ✅ bcrypt password hashing
- ✅ JWT authentication (30-day expiry)
- ✅ Rate limiting (3 OTP/hour, 5 signup/hour)
- ✅ OTP expiration (5 minutes)
- ✅ Max 5 verification attempts
- ✅ Input validation & sanitization
- ✅ CORS protection
- ✅ Helmet.js security headers

---

## 📱 Mobile Number Format

Always use E.164 format:

```
✅ Correct:
+1234567890        (US)
+918876543210      (India)
+447700900000      (UK)
+61412345678       (Australia)

❌ Incorrect:
1234567890         (Missing +)
(123) 456-7890     (Has formatting)
123-456-7890       (Has dashes)
```

---

## 📦 Project Structure

```
authenticator-system/
├── backend/           # Express API
│   ├── config/       # DB, Email, Twilio
│   ├── models/       # User, OTP schemas
│   ├── routes/       # Auth endpoints
│   ├── middleware/   # Auth, validation, rate limit
│   └── server.js     # Main server
├── frontend/         # React app
│   ├── src/
│   │   ├── components/  # Signup, Verify, Success
│   │   └── services/    # API calls
│   └── public/
├── docs/            # Documentation
│   ├── API.md
│   ├── INTEGRATION.md
│   └── TROUBLESHOOTING.md
└── .env.example     # Environment template
```

---

## 🚀 Deployment URLs

### Backend
- Heroku: `heroku create your-app-name`
- DigitalOcean: SSH + PM2 + Nginx
- Railway: `railway init`

### Frontend
- Vercel: `vercel` (in frontend directory)
- Netlify: Connect Git repo
- AWS S3: Static hosting

---

## 📚 Documentation Files

- **README.md** - Main documentation
- **INTEGRATION.md** - Integration guide
- **API.md** - API documentation
- **TROUBLESHOOTING.md** - Common issues & fixes
- **.env.example** - Environment variables template

---

## ⚡ Pro Tips

1. **Always use HTTPS in production**
2. **Rotate JWT_SECRET regularly**
3. **Monitor rate limit violations**
4. **Set up email alerts for errors**
5. **Use MongoDB Atlas for production**
6. **Upgrade Twilio for production SMS**
7. **Implement logging (Winston/Pino)**
8. **Add health check monitoring**
9. **Use Redis for rate limiting at scale**
10. **Implement request signing for sensitive ops**

---

## 🆘 Need Help?

1. Check **TROUBLESHOOTING.md** first
2. Review **INTEGRATION.md** for examples
3. Test with **Postman collection**
4. Enable debug mode in .env:
   ```env
   NODE_ENV=development
   ```
5. Check logs:
   ```bash
   # Backend
   tail -f backend/logs/app.log
   
   # Heroku
   heroku logs --tail
   ```

---

**Quick Links:**
- [Main README](README.md)
- [API Docs](docs/API.md)
- [Integration Guide](docs/INTEGRATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

**Ready to build? Start with `./setup.sh` or follow Quick Start above!** 🎉
