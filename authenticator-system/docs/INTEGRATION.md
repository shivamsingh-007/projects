# 📘 Integration Guide - OTP Authenticator System

This guide explains how to integrate the OTP Authenticator System into your existing application.

## Table of Contents
- [Quick Integration](#quick-integration)
- [API Integration](#api-integration)
- [Frontend Integration](#frontend-integration)
- [Backend Integration](#backend-integration)
- [Custom Branding](#custom-branding)
- [Production Deployment](#production-deployment)
- [Advanced Configuration](#advanced-configuration)

---

## Quick Integration

### Scenario 1: Standalone Use (As Is)

The system is ready to run standalone:

```bash
# Terminal 1 - Backend
cd backend
npm install
cp ../.env.example .env
# Edit .env with your credentials
npm start

# Terminal 2 - Frontend
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` and test the complete flow.

---

## API Integration

### Using REST API from Your Application

The backend exposes REST endpoints that any application can consume.

#### Step 1: Start the Backend

```bash
cd backend
npm install
npm start  # Runs on http://localhost:5000
```

#### Step 2: Call API from Your App

**Example: Signup a User (JavaScript/Fetch)**

```javascript
const signupUser = async (userData) => {
  try {
    const response = await fetch('http://localhost:5000/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: userData.name,
        email: userData.email,
        mobile: userData.mobile,  // E.164 format: +1234567890
        password: userData.password,
      }),
    });

    const data = await response.json();
    
    if (data.success) {
      // Store userId and token
      localStorage.setItem('userId', data.data.user.id);
      localStorage.setItem('token', data.data.token);
      
      // Navigate to verification
      console.log('User registered:', data.data.user);
      console.log('Email sent:', data.data.emailSent);
      console.log('SMS sent:', data.data.smsSent);
      
      return data;
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error('Signup error:', error);
    throw error;
  }
};

// Usage
signupUser({
  name: 'John Doe',
  email: 'john@example.com',
  mobile: '+1234567890',
  password: 'SecurePass123',
});
```

**Example: Verify OTP (Python/Requests)**

```python
import requests

def verify_otp(user_id, email_otp, mobile_otp):
    url = 'http://localhost:5000/api/auth/verify-otp'
    payload = {
        'userId': user_id,
        'emailOTP': email_otp,
        'mobileOTP': mobile_otp
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data['success']:
        user = data['data']['user']
        print(f"Verification Status: {user['verificationStatus']}")
        print(f"Email Verified: {user['emailVerified']}")
        print(f"Mobile Verified: {user['mobileVerified']}")
        
        return data
    else:
        print(f"Error: {data['message']}")
        return None

# Usage
verify_otp(
    user_id='64a1b2c3d4e5f6g7h8i9j0k1',
    email_otp='123456',
    mobile_otp='789012'
)
```

**Example: Check Status (cURL)**

```bash
curl -X GET http://localhost:5000/api/auth/status/USER_ID_HERE
```

---

## Frontend Integration

### Option 1: Use Provided React Components

Copy the React components into your existing React app:

```bash
# Copy components
cp -r frontend/src/components/* YOUR_APP/src/components/
cp frontend/src/services/api.js YOUR_APP/src/services/
cp frontend/src/App.css YOUR_APP/src/
```

**Add to your routes:**

```javascript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Signup from './components/Signup';
import Verify from './components/Verify';
import Success from './components/Success';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/auth/signup" element={<Signup />} />
        <Route path="/auth/verify" element={<Verify />} />
        <Route path="/auth/success" element={<Success />} />
        {/* Your other routes */}
      </Routes>
    </Router>
  );
}
```

**Install dependencies:**

```bash
npm install axios react-toastify react-icons
```

### Option 2: Build Custom UI with API

Create your own components and use the API service:

```javascript
import { authAPI } from './services/api';

const MyCustomSignup = () => {
  const handleSignup = async (formData) => {
    try {
      const response = await authAPI.signup(formData);
      // Handle success
      console.log(response.data.user);
    } catch (error) {
      // Handle error
      console.error(error.response?.data?.message);
    }
  };

  // Your custom UI here
};
```

### Option 3: Vanilla JavaScript/HTML

Use fetch API directly in your HTML pages:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Signup</title>
</head>
<body>
  <form id="signupForm">
    <input type="text" id="name" placeholder="Name" required>
    <input type="email" id="email" placeholder="Email" required>
    <input type="tel" id="mobile" placeholder="Mobile (+1234567890)" required>
    <input type="password" id="password" placeholder="Password" required>
    <button type="submit">Sign Up</button>
  </form>

  <script>
    document.getElementById('signupForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        mobile: document.getElementById('mobile').value,
        password: document.getElementById('password').value,
      };

      try {
        const response = await fetch('http://localhost:5000/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });

        const data = await response.json();
        
        if (data.success) {
          alert('Registration successful! Check your email and mobile for OTP.');
          // Store userId for verification
          localStorage.setItem('userId', data.data.user.id);
          // Redirect to verification page
          window.location.href = '/verify.html';
        } else {
          alert('Error: ' + data.message);
        }
      } catch (error) {
        alert('Network error. Please try again.');
      }
    });
  </script>
</body>
</html>
```

---

## Backend Integration

### Integrating with Existing Node.js/Express App

#### Step 1: Install Dependencies

```bash
npm install express mongoose bcryptjs jsonwebtoken nodemailer twilio dotenv cors express-rate-limit express-validator helmet morgan
```

#### Step 2: Copy Backend Files

```bash
# Copy backend structure into your app
cp -r backend/models YOUR_APP/models/auth/
cp -r backend/config YOUR_APP/config/auth/
cp -r backend/middleware YOUR_APP/middleware/auth/
cp -r backend/routes/auth.js YOUR_APP/routes/
```

#### Step 3: Update Your Server

```javascript
// server.js or app.js
const express = require('express');
const connectDB = require('./config/auth/database');
const authRoutes = require('./routes/auth');

const app = express();

// Connect to database
connectDB();

// Middleware
app.use(express.json());

// Routes
app.use('/api/auth', authRoutes);

// Your other routes...

app.listen(5000, () => {
  console.log('Server running on port 5000');
});
```

#### Step 4: Add Environment Variables

Add to your `.env` file:

```env
MONGODB_URI=your_mongodb_uri
JWT_SECRET=your_jwt_secret
EMAIL_USER=your_email
EMAIL_PASSWORD=your_email_password
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### Using with Different Databases

#### PostgreSQL (Instead of MongoDB)

Replace Mongoose models with Sequelize:

```javascript
// models/User.js (Sequelize version)
const { DataTypes } = require('sequelize');
const bcrypt = require('bcryptjs');

module.exports = (sequelize) => {
  const User = sequelize.define('User', {
    name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    email: {
      type: DataTypes.STRING,
      unique: true,
      allowNull: false,
      validate: { isEmail: true },
    },
    mobile: {
      type: DataTypes.STRING,
      unique: true,
      allowNull: false,
    },
    password: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    emailVerified: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
    },
    mobileVerified: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
    },
    verificationStatus: {
      type: DataTypes.ENUM('Not Verified', 'Pending', 'Verified'),
      defaultValue: 'Not Verified',
    },
  });

  // Hash password before create
  User.beforeCreate(async (user) => {
    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(user.password, salt);
  });

  // Update verification status
  User.beforeSave((user) => {
    if (user.emailVerified && user.mobileVerified) {
      user.verificationStatus = 'Verified';
    } else if (user.emailVerified || user.mobileVerified) {
      user.verificationStatus = 'Pending';
    }
  });

  return User;
};
```

---

## Custom Branding

### Customizing Email Templates

Edit `backend/config/email.js`:

```javascript
// Change colors
const mailOptions = {
  // ...
  html: `
    <style>
      .header { 
        background: linear-gradient(135deg, #YOUR_COLOR1, #YOUR_COLOR2);
      }
      .otp-code { 
        color: #YOUR_BRAND_COLOR;
      }
    </style>
    <!-- Your custom HTML -->
  `,
};
```

### Customizing SMS Messages

Edit `backend/config/twilio.js`:

```javascript
const message = await client.messages.create({
  body: `[YOUR BRAND] Your verification code is: ${otp}. Valid for 5 minutes.`,
  from: process.env.TWILIO_PHONE_NUMBER,
  to: mobile,
});
```

### Customizing Frontend Theme

Edit `frontend/src/App.css`:

```css
/* Change gradient colors */
body {
  background: linear-gradient(135deg, #YOUR_COLOR1, #YOUR_COLOR2);
}

.card-header h1 {
  color: #YOUR_BRAND_COLOR;
}

.btn-primary {
  background: linear-gradient(135deg, #YOUR_COLOR1, #YOUR_COLOR2);
}
```

### Adding Your Logo

```javascript
// In email.js
html: `
  <div class="header">
    <img src="https://your-domain.com/logo.png" alt="Logo" width="120">
    <h1>Email Verification</h1>
  </div>
  ...
`
```

```jsx
// In React components
<div className="card-header">
  <img src="/logo.png" alt="Logo" width="80" />
  <h1>Create Account</h1>
</div>
```

---

## Production Deployment

### Deploy Backend to Heroku

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
cd backend
heroku create your-app-name

# Set environment variables
heroku config:set MONGODB_URI=your_mongo_uri
heroku config:set JWT_SECRET=your_secret
heroku config:set EMAIL_USER=your_email
heroku config:set EMAIL_PASSWORD=your_password
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set TWILIO_AUTH_TOKEN=your_token
heroku config:set TWILIO_PHONE_NUMBER=your_number
heroku config:set NODE_ENV=production

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main

# View logs
heroku logs --tail
```

### Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Set environment variable in Vercel dashboard
REACT_APP_API_URL=https://your-backend.herokuapp.com/api
```

### Deploy Backend to DigitalOcean

1. **Create Droplet**
   - Ubuntu 22.04
   - 1GB RAM minimum

2. **SSH into server**
```bash
ssh root@your_server_ip
```

3. **Install Node.js and MongoDB**
```bash
# Update system
apt update && apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
apt update
apt install -y mongodb-org
systemctl start mongod
systemctl enable mongod
```

4. **Deploy Application**
```bash
# Clone your repo
git clone https://github.com/yourusername/otp-authenticator.git
cd otp-authenticator/backend

# Install dependencies
npm install

# Create .env file
nano .env
# Paste your environment variables

# Install PM2
npm install -g pm2

# Start app with PM2
pm2 start server.js --name otp-auth
pm2 startup
pm2 save

# Setup Nginx reverse proxy
apt install -y nginx

# Configure Nginx
nano /etc/nginx/sites-available/default
```

5. **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

6. **Restart Nginx**
```bash
nginx -t
systemctl restart nginx
```

7. **Setup SSL with Let's Encrypt**
```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your_domain.com
```

### Deploy with Docker

Create `docker-compose.yml` in root:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6
    volumes:
      - mongo-data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - MONGODB_URI=mongodb://admin:password@mongodb:27017/otp-authenticator?authSource=admin
      - JWT_SECRET=${JWT_SECRET}
      - EMAIL_USER=${EMAIL_USER}
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  mongo-data:
```

Create `backend/Dockerfile`:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 5000
CMD ["node", "server.js"]
```

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Run with Docker:

```bash
docker-compose up -d
```

---

## Advanced Configuration

### Customizing OTP Length

Edit `backend/models/OTP.js`:

```javascript
otpSchema.statics.generateOTP = function () {
  // Change to 4-digit OTP
  return Math.floor(1000 + Math.random() * 9000).toString();
  
  // Or 8-digit OTP
  // return Math.floor(10000000 + Math.random() * 90000000).toString();
};
```

### Changing OTP Expiration Time

Edit `backend/models/OTP.js`:

```javascript
expiresAt: {
  type: Date,
  required: true,
  default: () => new Date(Date.now() + 10 * 60 * 1000), // 10 minutes
},
createdAt: {
  type: Date,
  default: Date.now,
  expires: 600, // 10 minutes in seconds
},
```

### Using Different Email Provider (SendGrid)

Replace `backend/config/email.js`:

```javascript
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const sendOTPEmail = async (email, otp, name) => {
  const msg = {
    to: email,
    from: process.env.EMAIL_USER,
    subject: 'Email Verification - OTP Code',
    html: `Your OTP is: <strong>${otp}</strong>`,
  };

  try {
    await sgMail.send(msg);
    return { success: true };
  } catch (error) {
    throw new Error('Failed to send email');
  }
};
```

### Adding Webhook Notifications

Add to `backend/routes/auth.js`:

```javascript
// After successful verification
if (user.verificationStatus === 'Verified') {
  // Call webhook
  await axios.post(process.env.WEBHOOK_URL, {
    event: 'user.verified',
    userId: user._id,
    email: user.email,
    mobile: user.mobile,
    timestamp: new Date(),
  });
}
```

### Integrating with Existing User Model

If you have existing users, modify the signup route:

```javascript
router.post('/signup', async (req, res) => {
  // Check if user exists in your system
  const existingUser = await YourUserModel.findOne({ email });
  
  if (existingUser) {
    // Link to OTP system
    await User.create({
      _id: existingUser._id, // Use existing ID
      name: existingUser.name,
      email: existingUser.email,
      mobile: req.body.mobile,
      password: existingUser.password,
    });
  }
  
  // Continue with OTP flow...
});
```

---

## Testing

### Test with Postman

1. **Import Collection** (create in Postman):

```json
{
  "info": {
    "name": "OTP Authenticator API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Signup",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"Test User\",\n  \"email\": \"test@example.com\",\n  \"mobile\": \"+1234567890\",\n  \"password\": \"Test123\"\n}",
          "options": {
            "raw": {
              "language": "json"
            }
          }
        },
        "url": {
          "raw": "http://localhost:5000/api/auth/signup",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "auth", "signup"]
        }
      }
    }
  ]
}
```

### Unit Testing (Jest)

Create `backend/tests/auth.test.js`:

```javascript
const request = require('supertest');
const app = require('../server');

describe('Auth API', () => {
  it('should register a new user', async () => {
    const response = await request(app)
      .post('/api/auth/signup')
      .send({
        name: 'Test User',
        email: 'test@example.com',
        mobile: '+1234567890',
        password: 'Test123',
      });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
  });
});
```

---

## Support & Troubleshooting

### Common Issues

**1. "Rate limit exceeded"**
- Wait for the cooldown period
- Adjust rate limits in `middleware/rateLimiter.js`

**2. "Invalid mobile number format"**
- Use E.164 format: `+[country code][number]`
- Example: `+1234567890`

**3. "Email not received"**
- Check spam folder
- Verify Gmail App Password
- Check email logs: `heroku logs --tail`

**4. "SMS not received"**
- Verify phone number in Twilio (trial accounts)
- Check Twilio balance
- Verify number format

### Logs and Debugging

Enable detailed logging:

```javascript
// backend/server.js
app.use(morgan('combined'));

// View logs
console.log('Email sent:', emailResult);
console.log('SMS sent:', smsResult);
```

---

## Need Help?

- Check README.md for basic setup
- Review environment variables in .env.example
- Test API endpoints with Postman
- Check server logs for errors

---

**Happy Integrating! 🚀**
