import axios from 'axios';

// Create axios instance with base URL
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  // Register user
  signup: async (userData) => {
    const response = await API.post('/auth/signup', userData);
    return response.data;
  },

  // Verify OTP
  verifyOTP: async (otpData) => {
    const response = await API.post('/auth/verify-otp', otpData);
    return response.data;
  },

  // Resend OTP
  resendOTP: async (data) => {
    const response = await API.post('/auth/resend-otp', data);
    return response.data;
  },

  // Get verification status
  getStatus: async (userId) => {
    const response = await API.get(`/auth/status/${userId}`);
    return response.data;
  },

  // Get user profile
  getProfile: async () => {
    const response = await API.get('/auth/profile');
    return response.data;
  },
};

export default API;
