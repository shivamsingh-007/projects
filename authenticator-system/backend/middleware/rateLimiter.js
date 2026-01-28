const rateLimit = require('express-rate-limit');

// Rate limiter for OTP requests - 3 requests per hour per IP
const otpLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 3,
  message: {
    success: false,
    message: 'Too many OTP requests. Please try again after an hour.',
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Use custom key generator based on email or mobile
  keyGenerator: (req) => {
    return req.body.email || req.body.mobile || req.ip;
  },
});

// Rate limiter for signup - 5 requests per hour per IP
const signupLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5,
  message: {
    success: false,
    message: 'Too many signup attempts. Please try again after an hour.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Rate limiter for verification - 10 attempts per hour
const verifyLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 10,
  message: {
    success: false,
    message: 'Too many verification attempts. Please try again after an hour.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// General API rate limiter - 100 requests per 15 minutes
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: {
    success: false,
    message: 'Too many requests from this IP. Please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

module.exports = {
  otpLimiter,
  signupLimiter,
  verifyLimiter,
  apiLimiter,
};
