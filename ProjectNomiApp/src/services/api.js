
import axios from 'axios';
import { API_URL } from '../core/config';

/**
 * Core API Client
 * Configures the connection to the Python Backend.
 */
const apiClient = axios.create({
    baseURL: API_URL,
    timeout: 10000, // 10 seconds timeout
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

// Interceptor for logging (Optional: Helps debug connection issues)
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Server responded with a status other than 2xx
            console.error('API Error:', error.response.status, error.response.data);
        } else if (error.request) {
            // Request was made but no response received (Network Error)
            console.error('Network Error: Is the backend running? Check config.js IP.');
        } else {
            console.error('Error:', error.message);
        }
        return Promise.reject(error);
    }
);

export default apiClient;
