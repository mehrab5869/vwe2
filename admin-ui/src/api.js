import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://vwe2.sliplane.app';

// Configure axios to include ADMIN_SECRET_KEY for all admin requests
const adminApi = axios.create({
  baseURL: API_URL,
  headers: {
    'ADMIN_SECRET_KEY': 'change-this-in-production-min-32-chars-required'
  }
});

// Regular axios for non-admin requests
const api = axios.create({
  baseURL: API_URL
});

export { adminApi, api, API_URL };