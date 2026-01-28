const { body, validationResult } = require('express-validator');

// Validation rules for signup
const signupValidation = [
  body('name')
    .trim()
    .notEmpty()
    .withMessage('Name is required')
    .isLength({ min: 2, max: 50 })
    .withMessage('Name must be between 2 and 50 characters'),
  
  body('email')
    .trim()
    .notEmpty()
    .withMessage('Email is required')
    .isEmail()
    .withMessage('Please provide a valid email')
    .normalizeEmail(),
  
  body('mobile')
    .trim()
    .notEmpty()
    .withMessage('Mobile number is required')
    .matches(/^\+?[1-9]\d{1,14}$/)
    .withMessage('Please provide a valid mobile number in E.164 format (e.g., +1234567890)'),
  
  body('password')
    .trim()
    .notEmpty()
    .withMessage('Password is required')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, and one number'),
];

// Validation rules for OTP verification
const otpValidation = [
  body('userId')
    .trim()
    .notEmpty()
    .withMessage('User ID is required')
    .isMongoId()
    .withMessage('Invalid user ID'),
  
  body('emailOTP')
    .optional()
    .trim()
    .isLength({ min: 6, max: 6 })
    .withMessage('Email OTP must be 6 digits')
    .isNumeric()
    .withMessage('Email OTP must contain only numbers'),
  
  body('mobileOTP')
    .optional()
    .trim()
    .isLength({ min: 6, max: 6 })
    .withMessage('Mobile OTP must be 6 digits')
    .isNumeric()
    .withMessage('Mobile OTP must contain only numbers'),
];

// Validation rules for resend OTP
const resendOTPValidation = [
  body('userId')
    .trim()
    .notEmpty()
    .withMessage('User ID is required')
    .isMongoId()
    .withMessage('Invalid user ID'),
  
  body('type')
    .trim()
    .notEmpty()
    .withMessage('Type is required')
    .isIn(['email', 'mobile', 'both'])
    .withMessage('Type must be either "email", "mobile", or "both"'),
];

// Middleware to handle validation errors
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array().map(err => ({
        field: err.path,
        message: err.msg,
      })),
    });
  }
  next();
};

module.exports = {
  signupValidation,
  otpValidation,
  resendOTPValidation,
  handleValidationErrors,
};
