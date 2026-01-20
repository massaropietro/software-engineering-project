import axios from 'axios';
import router from '@/router'

const apiClient = axios.create({
  // @ts-ignore
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  timeout: 10000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific error codes here if needed (e.g. 500, 404)
    if (error.response && error.response.status === 404) {
      router.push({ name: 'not-found' });
    }
    console.error('API Error:', error.response || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
