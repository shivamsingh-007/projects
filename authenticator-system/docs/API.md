# API Documentation - OTP Authenticator System

## Base URL
```
http://localhost:5000/api
```

## Authentication
Most endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## Endpoints

### 1. User Signup

Register a new user and send OTP to email and mobile.

**Endpoint:** `POST /auth/signup`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "mobile": "+1234567890",
  "password": "SecurePass123"
}
```

**Validation Rules:**
- `name`: Required, 2-50 characters
- `email`: Required, valid email format
- `mobile`: Required, E.164 format (+1234567890)
- `password`: Required, min 6 chars, must contain uppercase, lowercase, and number

**Success Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully. OTP sent to email and mobile.",
  "data": {
    "user": {
      "id": "64a1b2c3d4e5f6g7h8i9j0k1",
      "name": "John Doe",
      "email": "john@example.com",
      "mobile": "+1234567890",
      "emailVerified": false,
      "mobileVerified": false,
      "verificationStatus": "Not Verified",
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "emailSent": true,
    "smsSent": true
  }
}
```

**Error Responses:**

400 - Validation Error:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Please provide a valid email"
    }
  ]
}
```

400 - User Exists:
```json
{
  "success": false,
  "message": "Email already registered"
}
```

429 - Rate Limit:
```json
{
  "success": false,
  "message": "Too many signup attempts. Please try again after an hour."
}
```

---

### 2. Verify OTP

Verify email and/or mobile OTP codes.

**Endpoint:** `POST /auth/verify-otp`

**Request Body:**
```json
{
  "userId": "64a1b2c3d4e5f6g7h8i9j0k1",
  "emailOTP": "123456",
  "mobileOTP": "789012"
}
```

**Note:** You can verify email and mobile separately or together. Omit `emailOTP` if email is already verified, and vice versa for `mobileOTP`.

**Success Response (200):**
```json
{
  "success": true,
  "message": "Both email and mobile verified successfully!",
  "data": {
    "user": {
      "id": "64a1b2c3d4e5f6g7h8i9j0k1",
      "name": "John Doe",
      "email": "john@example.com",
      "mobile": "+1234567890",
      "emailVerified": true,
      "mobileVerified": true,
      "verificationStatus": "Verified",
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "verificationResults": {
      "email": {
        "verified": true,
        "message": "Email verified successfully"
      },
      "mobile": {
        "verified": true,
        "message": "Mobile verified successfully"
      }
    }
  }
}
```

**Partial Verification (200):**
```json
{
  "success": true,
  "message": "Partial verification successful",
  "data": {
    "user": {
      "emailVerified": true,
      "mobileVerified": false,
      "verificationStatus": "Pending"
    },
    "verificationResults": {
      "email": {
        "verified": true,
        "message": "Email verified successfully"
      },
      "mobile": {
        "verified": false,
        "message": "Invalid mobile OTP"
      }
    }
  }
}
```

**Error Responses:**

400 - OTP Expired:
```json
{
  "success": false,
  "message": "OTP has expired. Please request a new one."
}
```

400 - Max Attempts:
```json
{
  "success": false,
  "message": "Maximum verification attempts exceeded. Please request a new OTP."
}
```

404 - User Not Found:
```json
{
  "success": false,
  "message": "User not found"
}
```

---

### 3. Resend OTP

Request new OTP codes for email and/or mobile.

**Endpoint:** `POST /auth/resend-otp`

**Request Body:**
```json
{
  "userId": "64a1b2c3d4e5f6g7h8i9j0k1",
  "type": "both"
}
```

**Type Options:**
- `"email"` - Resend only email OTP
- `"mobile"` - Resend only mobile OTP
- `"both"` - Resend both OTPs

**Success Response (200):**
```json
{
  "success": true,
  "message": "OTP resent successfully",
  "data": {
    "emailSent": true,
    "smsSent": true
  }
}
```

**Error Responses:**

400 - Already Verified:
```json
{
  "success": false,
  "message": "Email already verified"
}
```

429 - Rate Limit:
```json
{
  "success": false,
  "message": "Too many OTP requests. Please try again after an hour."
}
```

---

### 4. Get Verification Status

Check current verification status of a user.

**Endpoint:** `GET /auth/status/:userId`

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "emailVerified": true,
    "mobileVerified": false,
    "verificationStatus": "Pending"
  }
}
```

**Verification Status Values:**
- `"Not Verified"` - Neither email nor mobile verified
- `"Pending"` - One of email or mobile verified
- `"Verified"` - Both email and mobile verified

**Error Response:**

404 - User Not Found:
```json
{
  "success": false,
  "message": "User not found"
}
```

---

### 5. Get User Profile

Get authenticated user's profile (protected route).

**Endpoint:** `GET /auth/profile`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "64a1b2c3d4e5f6g7h8i9j0k1",
    "name": "John Doe",
    "email": "john@example.com",
    "mobile": "+1234567890",
    "emailVerified": true,
    "mobileVerified": true,
    "verificationStatus": "Verified",
    "createdAt": "2024-01-01T00:00:00.000Z"
  }
}
```

**Error Responses:**

401 - No Token:
```json
{
  "success": false,
  "message": "Not authorized, no token"
}
```

401 - Invalid Token:
```json
{
  "success": false,
  "message": "Not authorized, token failed"
}
```

---

## Rate Limits

- **Signup:** 5 requests per hour per IP
- **OTP Requests:** 3 requests per hour per email/mobile
- **Verification:** 10 attempts per hour per IP
- **General API:** 100 requests per 15 minutes per IP

When rate limit is exceeded, you'll receive a `429` status code with a message indicating when you can try again.

---

## Error Handling

All error responses follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error (development only)"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created (user registered)
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `404` - Not Found (user/resource not found)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

---

## Testing with cURL

### Signup
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "mobile": "+1234567890",
    "password": "Test123"
  }'
```

### Verify OTP
```bash
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "USER_ID_HERE",
    "emailOTP": "123456",
    "mobileOTP": "789012"
  }'
```

### Resend OTP
```bash
curl -X POST http://localhost:5000/api/auth/resend-otp \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "USER_ID_HERE",
    "type": "both"
  }'
```

### Get Status
```bash
curl -X GET http://localhost:5000/api/auth/status/USER_ID_HERE
```

### Get Profile (with token)
```bash
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Postman Collection

Import this JSON to Postman for easy testing:

```json
{
  "info": {
    "name": "OTP Authenticator API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:5000/api"
    }
  ],
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
          "raw": "{{baseUrl}}/auth/signup",
          "host": ["{{baseUrl}}"],
          "path": ["auth", "signup"]
        }
      }
    }
  ]
}
```

---

## WebSocket Support (Future Enhancement)

Real-time verification status updates can be added using Socket.io:

```javascript
// Client-side
socket.on('verification-status', (data) => {
  console.log('Status updated:', data.verificationStatus);
});
```

---

## Security Best Practices

1. **Always use HTTPS in production**
2. **Store JWT secret securely**
3. **Never expose API keys in frontend code**
4. **Implement request signing for sensitive operations**
5. **Monitor rate limit violations**
6. **Regularly rotate JWT secrets**
7. **Use environment-specific configurations**

---

For integration examples and advanced usage, see `docs/INTEGRATION.md`.
