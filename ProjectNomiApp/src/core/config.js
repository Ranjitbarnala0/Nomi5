// src/core/config.js

// This is the URL from your screenshot
const CLOUD_URL = 'https://nomi5-1.onrender.com';

const getBaseUrl = () => {
    // This tells the App: "Connect to the Cloud Brain, not the laptop."
    return `${CLOUD_URL}/api/v1`;
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
