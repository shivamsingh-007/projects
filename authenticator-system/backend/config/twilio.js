const twilio = require('twilio');

// Initialize Twilio client
const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

// Send OTP via SMS
const sendOTPSMS = async (mobile, otp, name) => {
  try {
    const message = await client.messages.create({
      body: `Hello ${name || 'User'}! Your OTP verification code is: ${otp}. This code will expire in 5 minutes. Do not share this code with anyone. - ${process.env.APP_NAME || 'OTP Authenticator'}`,
      from: process.env.TWILIO_PHONE_NUMBER,
      to: mobile, // Must be in E.164 format (e.g., +1234567890)
    });

    console.log('SMS sent: %s', message.sid);
    return { success: true, messageSid: message.sid };
  } catch (error) {
    console.error('Error sending SMS:', error);
    throw new Error('Failed to send SMS');
  }
};

// Verify Twilio configuration
const verifyTwilioConfig = () => {
  if (!process.env.TWILIO_ACCOUNT_SID || !process.env.TWILIO_AUTH_TOKEN || !process.env.TWILIO_PHONE_NUMBER) {
    console.warn('Twilio credentials not fully configured');
    return false;
  }
  console.log('Twilio configuration found');
  return true;
};

module.exports = { sendOTPSMS, verifyTwilioConfig };
