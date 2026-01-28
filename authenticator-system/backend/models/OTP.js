const mongoose = require('mongoose');

const otpSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  email: {
    type: String,
    required: true,
  },
  mobile: {
    type: String,
    required: true,
  },
  emailOTP: {
    type: String,
    required: true,
  },
  mobileOTP: {
    type: String,
    required: true,
  },
  emailAttempts: {
    type: Number,
    default: 0,
  },
  mobileAttempts: {
    type: Number,
    default: 0,
  },
  expiresAt: {
    type: Date,
    required: true,
    default: () => new Date(Date.now() + 5 * 60 * 1000), // 5 minutes
  },
  createdAt: {
    type: Date,
    default: Date.now,
    expires: 300, // Document will be automatically deleted after 5 minutes
  },
});

// Index for automatic cleanup
otpSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// Generate random 6-digit OTP
otpSchema.statics.generateOTP = function () {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

// Verify if OTP is expired
otpSchema.methods.isExpired = function () {
  return Date.now() > this.expiresAt;
};

// Increment attempt counter
otpSchema.methods.incrementAttempts = function (type) {
  if (type === 'email') {
    this.emailAttempts += 1;
  } else if (type === 'mobile') {
    this.mobileAttempts += 1;
  }
  return this.save();
};

module.exports = mongoose.model('OTP', otpSchema);
