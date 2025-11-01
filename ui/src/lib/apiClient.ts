import axios from 'axios';

const API_BASE = (import.meta as any).env?.PROD ? '/api' : 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;