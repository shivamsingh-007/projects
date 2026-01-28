const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please provide a name'],
    trim: true,
  },
  email: {
    type: String,
    required: [true, 'Please provide an email'],
    unique: true,
    lowercase: true,
    trim: true,
    match: [
      /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
      'Please provide a valid email',
    ],
  },
  mobile: {
    type: String,
    required: [true, 'Please provide a mobile number'],
    unique: true,
    trim: true,
    match: [
      /^\+?[1-9]\d{1,14}$/,
      'Please provide a valid mobile number in E.164 format',
    ],
  },
  password: {
    type: String,
    required: [true, 'Please provide a password'],
    minlength: 6,
    select: false,
  },
  emailVerified: {
    type: Boolean,
    default: false,
  },
  mobileVerified: {
    type: Boolean,
    default: false,
  },
  verificationStatus: {
    type: String,
    enum: ['Not Verified', 'Verified', 'Pending'],
    default: 'Not Verified',
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Update verification status based on email and mobile verification
userSchema.pre('save', function (next) {
  if (this.emailVerified && this.mobileVerified) {
    this.verificationStatus = 'Verified';
  } else if (this.emailVerified || this.mobileVerified) {
    this.verificationStatus = 'Pending';
  } else {
    this.verificationStatus = 'Not Verified';
  }
  this.updatedAt = Date.now();
  next();
});

// Hash password before saving
userSchema.pre('save', async function (next) {
  if (!this.isModified('password')) {
    next();
  }
  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
});

// Compare password method
userSchema.methods.matchPassword = async function (enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

// Get public profile
userSchema.methods.getPublicProfile = function () {
  return {
    id: this._id,
    name: this.name,
    email: this.email,
    mobile: this.mobile,
    emailVerified: this.emailVerified,
    mobileVerified: this.mobileVerified,
    verificationStatus: this.verificationStatus,
    createdAt: this.createdAt,
  };
};

module.exports = mongoose.model('User', userSchema);
