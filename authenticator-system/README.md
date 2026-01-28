# 🔐 OTP Authenticator System

A complete, production-ready email and mobile OTP (One-Time Password) authentication system built with Node.js, Express, MongoDB, React, Nodemailer, and Twilio.

## ✨ Features

- ✅ **Dual Verification**: Email AND mobile number verification
- ✅ **Real OTP Delivery**: Actual emails via Gmail SMTP and SMS via Twilio
- ✅ **Secure**: bcrypt password hashing, JWT authentication
- ✅ **Rate Limited**: Prevents abuse with configurable rate limits
- ✅ **Auto-Expiration**: OTPs expire after 5 minutes
- ✅ **Status Tracking**: Clear "Verified" / "Not Verified" indicators
- ✅ **Responsive UI**: Beautiful React interface with real-time feedback
- ✅ **Production Ready**: Error handling, validation, and security best practices

## 🎯 Status Indicators

- **Not Verified**: Neither email nor mobile verified
- **Pending**: One of email or mobile verified
- **Verified**: BOTH email AND mobile verified ✓

## 📦 Tech Stack

### Backend
- Node.js + Express.js
- MongoDB with Mongoose
- Nodemailer (Email)
- Twilio (SMS)
- JWT + bcrypt (Authentication)
- Express Rate Limit
- Express Validator

### Frontend
- React.js 18
- React Router v6
- Axios
- React Toastify
- React Icons

## 🚀 Quick Start

### Prerequisites

- Node.js (v18 or higher)
- MongoDB (local or Atlas)
- Gmail account (for email)
- Twilio account (for SMS)

### Installation

1. **Clone/Extract the project**
```bash
cd authenticator-system
```

2. **Install Backend Dependencies**
```bash
cd backend
npm install
```

3. **Install Frontend Dependencies**
```bash
cd ../frontend
npm install
```

4. **Configure Environment Variables**
```bash
cd ../backend
cp ../.env.example .env
```

Edit `.env` file with your credentials:

```env
# Database
MONGODB_URI=mongodb://localhost:27017/otp-authenticator

# JWT
JWT_SECRET=your_super_secret_key_change_this

# Email (Gmail App Password)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

5. **Start Backend Server**
```bash
cd backend
npm start
```
Server runs on `http://localhost:5000`

6. **Start Frontend (in new terminal)**
```bash
cd frontend
npm start
```
Frontend runs on `http://localhost:3000`

## 🔧 Configuration Guide

### MongoDB Setup

**Option 1: Local MongoDB**
```bash
# Install MongoDB
# Ubuntu/Debian:
sudo apt-get install mongodb

# macOS:
brew install mongodb-community

# Start MongoDB
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # macOS

# Use in .env
MONGODB_URI=mongodb://localhost:27017/otp-authenticator
```

**Option 2: MongoDB Atlas (Cloud)**
1. Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Create free account and cluster
3. Get connection string
4. Replace in `.env`:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/otp-authenticator
```

### Gmail Setup (Email OTP)

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Security → 2-Step Verification → Turn On

2. **Generate App Password**
   - Security → App passwords
   - Select app: Mail
   - Select device: Other (Custom name)
   - Click "Generate"
   - Copy 16-character password

3. **Update .env**
```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop  # App password
```

### Twilio Setup (SMS OTP)

1. **Sign Up**
   - Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
   - Create account (get $15 free credit)

2. **Get Credentials**
   - Dashboard: [console.twilio.com](https://console.twilio.com/)
   - Copy: Account SID, Auth Token
   - Get phone number (Phone Numbers → Manage → Buy a number)

3. **Update .env**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

**Note**: Trial accounts can only send SMS to verified numbers. Verify your number first in Twilio console.

## 📡 API Endpoints

### POST `/api/auth/signup`
Register new user and send OTPs

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "mobile": "+1234567890",
  "password": "Password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully. OTP sent to email and mobile.",
  "data": {
    "user": {
      "id": "...",
      "name": "John Doe",
      "email": "john@example.com",
      "mobile": "+1234567890",
      "emailVerified": false,
      "mobileVerified": false,
      "verificationStatus": "Not Verified"
    },
    "token": "jwt_token_here",
    "emailSent": true,
    "smsSent": true
  }
}
```

### POST `/api/auth/verify-otp`
Verify OTP codes

**Request:**
```json
{
  "userId": "user_id_here",
  "emailOTP": "123456",
  "mobileOTP": "789012"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Both email and mobile verified successfully!",
  "data": {
    "user": {
      "id": "...",
      "verificationStatus": "Verified",
      "emailVerified": true,
      "mobileVerified": true
    },
    "verificationResults": {
      "email": { "verified": true, "message": "Email verified successfully" },
      "mobile": { "verified": true, "message": "Mobile verified successfully" }
    }
  }
}
```

### POST `/api/auth/resend-otp`
Resend OTP codes

**Request:**
```json
{
  "userId": "user_id_here",
  "type": "both"  // or "email" or "mobile"
}
```

### GET `/api/auth/status/:userId`
Get verification status

**Response:**
```json
{
  "success": true,
  "data": {
    "emailVerified": true,
    "mobileVerified": true,
    "verificationStatus": "Verified"
  }
}
```

### GET `/api/auth/profile`
Get user profile (requires JWT token)

**Headers:**
```
Authorization: Bearer your_jwt_token
```

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure authentication tokens
- **Rate Limiting**:
  - Signup: 5 requests/hour
  - OTP Requests: 3 requests/hour
  - Verification: 10 attempts/hour
  - General API: 100 requests/15 minutes
- **Input Validation**: Server-side validation with express-validator
- **CORS Protection**: Configured for specific origins
- **Helmet.js**: Security headers
- **OTP Expiration**: Automatic cleanup after 5 minutes
- **Attempt Limits**: Max 5 verification attempts per OTP

## 🎨 Frontend Features

- Clean, modern UI with gradient design
- Real-time OTP input with auto-focus
- Countdown timer for OTP expiration
- Success/error toast notifications
- Responsive design (mobile-friendly)
- Form validation with error messages
- Loading states and disabled buttons
- Status badges (Verified/Not Verified)

## 🐛 Troubleshooting

### "Cannot connect to MongoDB"
- Ensure MongoDB is running: `sudo systemctl status mongodb`
- Check MONGODB_URI in .env
- For Atlas: whitelist your IP in MongoDB Atlas

### "Email not sending"
- Verify Gmail App Password is correct
- Check 2FA is enabled on Google account
- Try different email provider if Gmail blocks

### "SMS not sending"
- Verify Twilio credentials
- Check phone number format: E.164 (+1234567890)
- For trial: verify recipient number in Twilio console
- Check Twilio account balance

### "CORS errors"
- Update FRONTEND_URL in backend/.env
- Ensure frontend and backend ports match

## 📁 Project Structure

```
authenticator-system/
├── backend/
│   ├── config/
│   │   ├── database.js       # MongoDB connection
│   │   ├── email.js          # Nodemailer setup
│   │   └── twilio.js         # Twilio SMS setup
│   ├── models/
│   │   ├── User.js           # User schema
│   │   └── OTP.js            # OTP schema
│   ├── routes/
│   │   └── auth.js           # Auth endpoints
│   ├── middleware/
│   │   ├── auth.js           # JWT verification
│   │   ├── rateLimiter.js    # Rate limiting
│   │   └── validator.js      # Input validation
│   ├── server.js             # Express app
│   └── package.json
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Signup.js     # Registration form
│   │   │   ├── Verify.js     # OTP verification
│   │   │   └── Success.js    # Success page
│   │   ├── services/
│   │   │   └── api.js        # API calls
│   │   ├── App.js            # Main component
│   │   ├── App.css           # Styles
│   │   └── index.js          # Entry point
│   └── package.json
├── docs/
│   └── INTEGRATION.md        # Integration guide
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🚀 Deployment

### Backend (Heroku)

1. Create Heroku app
```bash
heroku create your-app-name
```

2. Set environment variables
```bash
heroku config:set MONGODB_URI=your_mongo_uri
heroku config:set JWT_SECRET=your_secret
heroku config:set EMAIL_USER=your_email
# ... set all variables
```

3. Deploy
```bash
git push heroku main
```

### Frontend (Vercel)

1. Install Vercel CLI
```bash
npm i -g vercel
```

2. Deploy
```bash
cd frontend
vercel
```

3. Set environment variable
```
REACT_APP_API_URL=https://your-backend-url.herokuapp.com/api
```

### Backend (DigitalOcean)

See `docs/INTEGRATION.md` for detailed deployment instructions.

## 📝 License

MIT License - Feel free to use in your projects!

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

## 📧 Support

For issues or questions:
- Open a GitHub issue
- Check `docs/INTEGRATION.md` for detailed integration guide

## 🎉 Acknowledgments

Built with ❤️ using:
- Express.js
- React
- MongoDB
- Nodemailer
- Twilio

---

**Ready to use?** Follow the Quick Start guide above!
