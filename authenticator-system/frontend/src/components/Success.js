import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FaCheckCircle } from 'react-icons/fa';

const Success = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = location.state || {};

  if (!user) {
    navigate('/');
    return null;
  }

  return (
    <div className="app-container">
      <div className="card">
        <div className="success-icon">
          <FaCheckCircle size={80} />
        </div>

        <div className="card-header">
          <h1>Verification Complete!</h1>
          <p>Your account has been successfully verified</p>
        </div>

        <div style={{ background: '#f9f9f9', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
          <div style={{ marginBottom: '15px' }}>
            <strong>Name:</strong>
            <div style={{ color: '#666', marginTop: '5px' }}>{user.name}</div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong>Email:</strong>
            <div style={{ color: '#666', marginTop: '5px' }}>{user.email}</div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong>Mobile:</strong>
            <div style={{ color: '#666', marginTop: '5px' }}>{user.mobile}</div>
          </div>

          <div>
            <strong>Status:</strong>
            <div style={{ marginTop: '8px' }}>
              <span className="status-badge verified">
                <FaCheckCircle />
                {user.verificationStatus}
              </span>
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'center', color: '#666', fontSize: '14px', marginBottom: '20px' }}>
          Both your email and mobile number have been verified. You can now access all features of your account.
        </div>

        <button
          onClick={() => navigate('/')}
          className="btn btn-primary"
        >
          Continue to Dashboard
        </button>
      </div>
    </div>
  );
};

export default Success;
