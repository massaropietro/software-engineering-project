import axios from 'axios';
import ToastEventBus from 'primevue/toasteventbus';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

apiClient.defaults.headers.common["Accept-Language"] = localStorage.getItem('locale') || 'it';

apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        let msg = error.message;

        if (error.response) {
            if (error.response.status === 404) {
                if (error.response.data.detail && error.response.data.detail) {
                    msg = error.response.data.detail;
                }
            }
        }
        ToastEventBus.emit('add', {
              severity: 'error',
              summary: 'Errore API',
              detail: msg,
              life: 5000
        });

        return Promise.reject(error);
    }
);

export default apiClient;
