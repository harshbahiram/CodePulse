import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 10000,
    headers: {
        "Content-Type": "application/json"
    }
});

export const healthAPI = {
    checkBackend: () => api.get("/health"),

    checkDatabase: () => api.get("/health/db")
};

export default api;