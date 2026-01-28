import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'react-toastify';
import { authAPI } from '../services/api';
import { FaEnvelope, FaPhone, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

const Verify = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { userId, email, mobile, emailSent, smsSent } = location.state || {};

  const [emailOTP, setEmailOTP] = useState(['', '', '', '', '', '']);
  const [mobileOTP, setMobileOTP] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes in seconds
  const [emailVerified, setEmailVerified] = useState(false);
  const [mobileVerified, setMobileVerified] = useState(false);

  const emailInputRefs = useRef([]);
  const mobileInputRefs = useRef([]);

  // Redirect if no user data
  useEffect(() => {
    if (!userId) {
      navigate('/');
    }
  }, [userId, navigate]);

  // Timer countdown
  useEffect(() => {
    if (timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft]);

  // Format time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle OTP input change
  const handleOTPChange = (index, value, type) => {
    if (!/^\d*$/.test(value)) return;

    const setOTP = type === 'email' ? setEmailOTP : setMobileOTP;
    const inputRefs = type === 'email' ? emailInputRefs : mobileInputRefs;

    setOTP((prev) => {
      const newOTP = [...prev];
      newOTP[index] = value;
      return newOTP;
    });

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  // Handle backspace
  const handleKeyDown = (index, e, type) => {
    const inputRefs = type === 'email' ? emailInputRefs : mobileInputRefs;

    if (e.key === 'Backspace' && !e.target.value && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  // Handle paste
  const handlePaste = (e, type) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    const setOTP = type === 'email' ? setEmailOTP : setMobileOTP;

    if (pastedData.length === 6) {
      setOTP(pastedData.split(''));
    }
  };

  // Verify OTP
  const handleVerify = async () => {
    const emailOTPString = emailOTP.join('');
    const mobileOTPString = mobileOTP.join('');

    if (!emailVerified && emailOTPString.length !== 6) {
      toast.error('Please enter complete email OTP');
      return;
    }

    if (!mobileVerified && mobileOTPString.length !== 6) {
      toast.error('Please enter complete mobile OTP');
      return;
    }

    setLoading(true);

    try {
      const response = await authAPI.verifyOTP({
        userId,
        emailOTP: !emailVerified ? emailOTPString : undefined,
        mobileOTP: !mobileVerified ? mobileOTPString : undefined,
      });

      if (response.success) {
        const { verificationResults } = response.data;

        // Update verification status
        if (verificationResults.email.verified) {
          setEmailVerified(true);
          toast.success('Email verified successfully!');
        } else if (verificationResults.email.message) {
          toast.error(verificationResults.email.message);
        }

        if (verificationResults.mobile.verified) {
          setMobileVerified(true);
          toast.success('Mobile verified successfully!');
        } else if (verificationResults.mobile.message) {
          toast.error(verificationResults.mobile.message);
        }

        // Check if both verified
        if (response.data.user.verificationStatus === 'Verified') {
          setTimeout(() => {
            navigate('/success', {
              state: { user: response.data.user },
            });
          }, 1500);
        }
      }
    } catch (error) {
      console.error('Verification error:', error);
      const errorMessage = error.response?.data?.message || 'Verification failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Resend OTP
  const handleResend = async (type) => {
    setResendLoading(true);

    try {
      const response = await authAPI.resendOTP({
        userId,
        type,
      });

      if (response.success) {
        toast.success('OTP resent successfully!');
        setTimeLeft(300); // Reset timer
        
        // Clear OTP inputs
        if (type === 'email' || type === 'both') {
          setEmailOTP(['', '', '', '', '', '']);
        }
        if (type === 'mobile' || type === 'both') {
          setMobileOTP(['', '', '', '', '', '']);
        }
      }
    } catch (error) {
      console.error('Resend error:', error);
      const errorMessage = error.response?.data?.message || 'Failed to resend OTP. Please try again.';
      toast.error(errorMessage);
    } finally {
      setResendLoading(false);
    }
  };

  if (!userId) {
    return null;
  }

  return (
    <div className="app-container">
      <div className="card">
        <div className="card-header">
          <h1>Verify Your Account</h1>
          <p>Enter the OTP codes sent to your email and mobile</p>
        </div>

        {/* Email Verification */}
        <div className="verification-item">
          <div className="verification-item-label">
            <FaEnvelope size={20} />
            <div>
              <div>Email Verification</div>
              <small style={{ color: '#666' }}>{email}</small>
            </div>
          </div>
          <div className={`verification-item-status ${emailVerified ? 'verified' : 'not-verified'}`}>
            {emailVerified ? (
              <>
                <FaCheckCircle size={20} />
                Verified
              </>
            ) : (
              <>
                <FaTimesCircle size={20} />
                Not Verified
              </>
            )}
          </div>
        </div>

        {!emailVerified && (
          <>
            <div style={{ margin: '20px 0' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: '500' }}>
                Enter Email OTP
              </label>
              <div className="otp-container">
                {emailOTP.map((digit, index) => (
                  <input
                    key={index}
                    ref={(el) => (emailInputRefs.current[index] = el)}
                    type="text"
                    maxLength="1"
                    className="otp-input"
                    value={digit}
                    onChange={(e) => handleOTPChange(index, e.target.value, 'email')}
                    onKeyDown={(e) => handleKeyDown(index, e, 'email')}
                    onPaste={(e) => handlePaste(e, 'email')}
                  />
                ))}
              </div>
            </div>
          </>
        )}

        {/* Mobile Verification */}
        <div className="verification-item" style={{ marginTop: '20px' }}>
          <div className="verification-item-label">
            <FaPhone size={20} />
            <div>
              <div>Mobile Verification</div>
              <small style={{ color: '#666' }}>{mobile}</small>
            </div>
          </div>
          <div className={`verification-item-status ${mobileVerified ? 'verified' : 'not-verified'}`}>
            {mobileVerified ? (
              <>
                <FaCheckCircle size={20} />
                Verified
              </>
            ) : (
              <>
                <FaTimesCircle size={20} />
                Not Verified
              </>
            )}
          </div>
        </div>

        {!mobileVerified && (
          <>
            <div style={{ margin: '20px 0' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: '500' }}>
                Enter Mobile OTP
              </label>
              <div className="otp-container">
                {mobileOTP.map((digit, index) => (
                  <input
                    key={index}
                    ref={(el) => (mobileInputRefs.current[index] = el)}
                    type="text"
                    maxLength="1"
                    className="otp-input"
                    value={digit}
                    onChange={(e) => handleOTPChange(index, e.target.value, 'mobile')}
                    onKeyDown={(e) => handleKeyDown(index, e, 'mobile')}
                    onPaste={(e) => handlePaste(e, 'mobile')}
                  />
                ))}
              </div>
            </div>
          </>
        )}

        {/* Timer */}
        <div className={`timer ${timeLeft < 60 ? 'warning' : ''}`}>
          {timeLeft > 0 ? `OTP expires in ${formatTime(timeLeft)}` : 'OTP expired'}
        </div>

        {/* Verify Button */}
        {(!emailVerified || !mobileVerified) && (
          <button
            onClick={handleVerify}
            className="btn btn-primary"
            disabled={loading || timeLeft === 0}
          >
            {loading ? (
              <>
                <div className="loading-spinner"></div>
                Verifying...
              </>
            ) : (
              'Verify OTP'
            )}
          </button>
        )}

        {/* Resend Options */}
        {(!emailVerified || !mobileVerified) && (
          <div className="resend-container">
            <p style={{ marginBottom: '10px', color: '#666' }}>Didn't receive OTP?</p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
              {!emailVerified && (
                <button
                  onClick={() => handleResend('email')}
                  className="btn-link"
                  disabled={resendLoading}
                >
                  Resend Email OTP
                </button>
              )}
              {!mobileVerified && (
                <button
                  onClick={() => handleResend('mobile')}
                  className="btn-link"
                  disabled={resendLoading}
                >
                  Resend Mobile OTP
                </button>
              )}
              {!emailVerified && !mobileVerified && (
                <button
                  onClick={() => handleResend('both')}
                  className="btn-link"
                  disabled={resendLoading}
                >
                  Resend Both
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Verify;
