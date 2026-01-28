require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const connectDB = require('./config/database');
const { verifyEmailConfig } = require('./config/email');
const { verifyTwilioConfig } = require('./config/twilio');
const { apiLimiter } = require('./middleware/rateLimiter');

// Initialize express app
const app = express();

// Connect to database
connectDB();

// Verify configurations
verifyEmailConfig();
verifyTwilioConfig();

// Middleware
app.use(helmet()); // Security headers
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}));
app.use(express.json()); // Body parser
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev')); // Logging

// Apply rate limiting to all routes
app.use('/api/', apiLimiter);

// Routes
app.use('/api/auth', require('./routes/auth'));

// Health check route
app.get('/health', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'Server is running',
    timestamp: new Date().toISOString(),
  });
});

// Root route
app.get('/', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'OTP Authenticator API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      signup: 'POST /api/auth/signup',
      verifyOTP: 'POST /api/auth/verify-otp',
      resendOTP: 'POST /api/auth/resend-otp',
      status: 'GET /api/auth/status/:userId',
      profile: 'GET /api/auth/profile',
    },
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found',
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err : undefined,
  });
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`
  ╔═══════════════════════════════════════════════════════════╗
  ║                                                           ║
  ║         🚀 OTP Authenticator Server Running 🚀           ║
  ║                                                           ║
  ║   Server: http://localhost:${PORT}                         ║
  ║   Environment: ${process.env.NODE_ENV || 'development'}                                  ║
  ║   Database: ${process.env.MONGODB_URI ? 'Connected' : 'Not configured'}                                 ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
  `);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('Unhandled Promise Rejection:', err);
  // Close server & exit process
  process.exit(1);
});
