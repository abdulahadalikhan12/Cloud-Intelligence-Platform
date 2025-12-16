import axios from 'axios';

// Vite proxy forwards /weather, /predict to http://127.0.0.1:8000
const api = axios.create({
    baseURL: '/',
    timeout: 10000,
});

export default api;
