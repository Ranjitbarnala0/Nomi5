// src/core/config.js

// PRODUCTION - Render Cloud Backend
const CLOUD_URL = 'https://nomi5-1.onrender.com';

// LOCAL TESTING - Uncomment to use local backend
// const LOCAL_URL = 'http://192.168.1.205:10000';

const getBaseUrl = () => {
    // Using Render Cloud Backend
    return `${CLOUD_URL}/api/v1`;

    // Uncomment below for local testing:
    // return `${LOCAL_URL}/api/v1`;
};

export const API_URL = getBaseUrl();

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
