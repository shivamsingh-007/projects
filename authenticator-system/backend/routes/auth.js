const express = require('express');
const router = express.Router();
const User = require('../models/User');
const OTP = require('../models/OTP');
const { generateToken, protect } = require('../middleware/auth');
const { sendOTPEmail } = require('../config/email');
const { sendOTPSMS } = require('../config/twilio');
const {
  signupValidation,
  otpValidation,
  resendOTPValidation,
  handleValidationErrors,
} = require('../middleware/validator');
const {
  signupLimiter,
  otpLimiter,
  verifyLimiter,
} = require('../middleware/rateLimiter');

// @route   POST /api/auth/signup
// @desc    Register user and send OTP to email and mobile
// @access  Public
router.post('/signup', signupLimiter, signupValidation, handleValidationErrors, async (req, res) => {
  try {
    const { name, email, mobile, password } = req.body;

    // Check if user already exists
    const existingUser = await User.findOne({
      $or: [{ email }, { mobile }],
    });

    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: existingUser.email === email
          ? 'Email already registered'
          : 'Mobile number already registered',
      });
    }

    // Create user
    const user = await User.create({
      name,
      email,
      mobile,
      password,
    });

    // Generate OTPs
    const emailOTP = OTP.generateOTP();
    const mobileOTP = OTP.generateOTP();

    // Save OTPs to database
    await OTP.create({
      userId: user._id,
      email,
      mobile,
      emailOTP,
      mobileOTP,
    });

    // Send OTP via email and SMS
    const emailPromise = sendOTPEmail(email, emailOTP, name);
    const smsPromise = sendOTPSMS(mobile, mobileOTP, name);

    // Wait for both to complete
    const [emailResult, smsResult] = await Promise.allSettled([emailPromise, smsPromise]);

    // Check results
    const emailSent = emailResult.status === 'fulfilled';
    const smsSent = smsResult.status === 'fulfilled';

    if (!emailSent && !smsSent) {
      // Delete user if both failed
      await User.findByIdAndDelete(user._id);
      await OTP.findOneAndDelete({ userId: user._id });
      
      return res.status(500).json({
        success: false,
        message: 'Failed to send OTP. Please try again.',
      });
    }

    // Generate token
    const token = generateToken(user._id);

    res.status(201).json({
      success: true,
      message: 'User registered successfully. OTP sent to email and mobile.',
      data: {
        user: user.getPublicProfile(),
        token,
        emailSent,
        smsSent,
      },
    });
  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error. Please try again.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

// @route   POST /api/auth/verify-otp
// @desc    Verify OTP for email and/or mobile
// @access  Public
router.post('/verify-otp', verifyLimiter, otpValidation, handleValidationErrors, async (req, res) => {
  try {
    const { userId, emailOTP, mobileOTP } = req.body;

    // Find user
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found',
      });
    }

    // Find OTP record
    const otpRecord = await OTP.findOne({ userId });
    if (!otpRecord) {
      return res.status(400).json({
        success: false,
        message: 'OTP expired or not found. Please request a new one.',
      });
    }

    // Check if OTP is expired
    if (otpRecord.isExpired()) {
      await OTP.findByIdAndDelete(otpRecord._id);
      return res.status(400).json({
        success: false,
        message: 'OTP has expired. Please request a new one.',
      });
    }

    // Check attempt limits
    if (otpRecord.emailAttempts >= 5 || otpRecord.mobileAttempts >= 5) {
      return res.status(400).json({
        success: false,
        message: 'Maximum verification attempts exceeded. Please request a new OTP.',
      });
    }

    let emailVerified = user.emailVerified;
    let mobileVerified = user.mobileVerified;
    const verificationResults = {
      email: { verified: false, message: '' },
      mobile: { verified: false, message: '' },
    };

    // Verify email OTP
    if (emailOTP && !user.emailVerified) {
      if (emailOTP === otpRecord.emailOTP) {
        emailVerified = true;
        verificationResults.email = { verified: true, message: 'Email verified successfully' };
      } else {
        await otpRecord.incrementAttempts('email');
        verificationResults.email = { verified: false, message: 'Invalid email OTP' };
      }
    }

    // Verify mobile OTP
    if (mobileOTP && !user.mobileVerified) {
      if (mobileOTP === otpRecord.mobileOTP) {
        mobileVerified = true;
        verificationResults.mobile = { verified: true, message: 'Mobile verified successfully' };
      } else {
        await otpRecord.incrementAttempts('mobile');
        verificationResults.mobile = { verified: false, message: 'Invalid mobile OTP' };
      }
    }

    // Update user verification status
    user.emailVerified = emailVerified;
    user.mobileVerified = mobileVerified;
    await user.save();

    // Delete OTP if both are verified
    if (emailVerified && mobileVerified) {
      await OTP.findByIdAndDelete(otpRecord._id);
    }

    // Determine overall success
    const bothVerified = emailVerified && mobileVerified;
    const anyVerified = emailVerified || mobileVerified;

    res.status(200).json({
      success: anyVerified,
      message: bothVerified
        ? 'Both email and mobile verified successfully!'
        : anyVerified
        ? 'Partial verification successful'
        : 'Verification failed',
      data: {
        user: user.getPublicProfile(),
        verificationResults,
      },
    });
  } catch (error) {
    console.error('OTP verification error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error. Please try again.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

// @route   POST /api/auth/resend-otp
// @desc    Resend OTP to email and/or mobile
// @access  Public
router.post('/resend-otp', otpLimiter, resendOTPValidation, handleValidationErrors, async (req, res) => {
  try {
    const { userId, type } = req.body;

    // Find user
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found',
      });
    }

    // Check if already verified
    if (type === 'email' && user.emailVerified) {
      return res.status(400).json({
        success: false,
        message: 'Email already verified',
      });
    }

    if (type === 'mobile' && user.mobileVerified) {
      return res.status(400).json({
        success: false,
        message: 'Mobile already verified',
      });
    }

    if (type === 'both' && user.emailVerified && user.mobileVerified) {
      return res.status(400).json({
        success: false,
        message: 'Both email and mobile already verified',
      });
    }

    // Delete existing OTP
    await OTP.findOneAndDelete({ userId });

    // Generate new OTPs
    const emailOTP = OTP.generateOTP();
    const mobileOTP = OTP.generateOTP();

    // Save new OTPs
    await OTP.create({
      userId: user._id,
      email: user.email,
      mobile: user.mobile,
      emailOTP,
      mobileOTP,
    });

    // Send OTPs based on type
    const results = { emailSent: false, smsSent: false };

    if (type === 'email' || type === 'both') {
      try {
        await sendOTPEmail(user.email, emailOTP, user.name);
        results.emailSent = true;
      } catch (error) {
        console.error('Email send error:', error);
      }
    }

    if (type === 'mobile' || type === 'both') {
      try {
        await sendOTPSMS(user.mobile, mobileOTP, user.name);
        results.smsSent = true;
      } catch (error) {
        console.error('SMS send error:', error);
      }
    }

    // Check if at least one was sent
    if (!results.emailSent && !results.smsSent) {
      return res.status(500).json({
        success: false,
        message: 'Failed to send OTP. Please try again.',
      });
    }

    res.status(200).json({
      success: true,
      message: 'OTP resent successfully',
      data: results,
    });
  } catch (error) {
    console.error('Resend OTP error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error. Please try again.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

// @route   GET /api/auth/status/:userId
// @desc    Get user verification status
// @access  Public
router.get('/status/:userId', async (req, res) => {
  try {
    const user = await User.findById(req.params.userId);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found',
      });
    }

    res.status(200).json({
      success: true,
      data: {
        emailVerified: user.emailVerified,
        mobileVerified: user.mobileVerified,
        verificationStatus: user.verificationStatus,
      },
    });
  } catch (error) {
    console.error('Status check error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error. Please try again.',
    });
  }
});

// @route   GET /api/auth/profile
// @desc    Get user profile (protected route example)
// @access  Private
router.get('/profile', protect, async (req, res) => {
  try {
    res.status(200).json({
      success: true,
      data: req.user.getPublicProfile(),
    });
  } catch (error) {
    console.error('Profile fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error. Please try again.',
    });
  }
});

module.exports = router;
