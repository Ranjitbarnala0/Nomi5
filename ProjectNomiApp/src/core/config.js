// src/core/config.js

// PRODUCTION - Render Cloud Backend
const CLOUD_URL = 'https://nomi5-1.onrender.com';

// LOCAL TESTING - Point to localhost backend
// const LOCAL_URL = 'http://192.168.1.205:10000';

const getBaseUrl = () => {
    // Connect to Render Cloud Backend
    const url = `${CLOUD_URL}/api/v1`;
    console.log('[CONFIG] Base URL:', url);
    return url;
};

export const API_URL = getBaseUrl();
console.log('[CONFIG] Using API_URL:', API_URL);

export const CONFIG = {
    APP_NAME: 'Nomi',
    VERSION: '1.0.0',
    THEME: {
        BACKGROUND: '#0a0a0a',
        TEXT_PRIMARY: '#e0e0e0',
        TEXT_SECONDARY: '#a0a0a0',
        ACCENT: '#ffffff',
        ERROR: '#ff4444',
        SYSTEM_MSG: '#888888',
    }
};
