
import { Platform } from 'react-native';

/**
 * CONFIGURATION RULES:
 * 1. If running on Android Emulator, use '10.0.2.2'.
 * 2. If running on iOS Simulator, use 'localhost'.
 * 3. If running on Physical Device, YOU MUST use your Computer's LAN IP (e.g., 192.168.1.X).
 */

// REPLACE '192.168.1.X' WITH YOUR COMPUTER'S LOCAL IP ADDRESS IF TESTING ON REAL PHONE
const LOCAL_IP = '192.168.1.50';

const API_PORT = '8000';

const getBaseUrl = () => {
    if (__DEV__) {
        if (Platform.OS === 'android') {
            // Android Emulator special loopback
            return `http://10.0.2.2:${API_PORT}/api/v1`;
        } else if (Platform.OS === 'ios') {
            // iOS Simulator
            return `http://localhost:${API_PORT}/api/v1`;
        } else {
            // Physical Device (Fallback)
            return `http://${LOCAL_IP}:${API_PORT}/api/v1`;
        }
    }
    // Production URL (Placeholder)
    return 'https://api.projectnomi.com/api/v1';
};

export const API_URL = getBaseUrl();

export const CONFIG = {
    APP_NAME: 'Project Nomi',
    VERSION: '1.0.0',
    THEME: {
        BACKGROUND: '#0a0a0a', // Deep Noir Black
        TEXT_PRIMARY: '#e0e0e0', // Soft White
        TEXT_SECONDARY: '#a0a0a0', // Grey
        ACCENT: '#ffffff', // Stark White
        ERROR: '#ff4444',
        SYSTEM_MSG: '#888888', // For "Time Skips"
    }
};
