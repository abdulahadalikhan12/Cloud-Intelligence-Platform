import axios from 'axios';

// In Vercel, the backend is rewritten to /api
// In local dev, Vite proxy forwards /weather etc directly to backend
// Let's settle on a consistent prefix '/api' and proxy it in dev.
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    timeout: 10000,
});

export default api;
