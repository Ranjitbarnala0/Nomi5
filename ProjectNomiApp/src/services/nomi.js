
import apiClient from './api';

/**
 * The Nomi Service
 * Maps JavaScript functions to Python Backend API endpoints.
 */
export const NomiService = {

    // --- SYSTEM ---
    checkHealth: async () => {
        const response = await apiClient.get('/system/diagnostics');
        return response.data;
    },

    getAppConfig: async () => {
        const response = await apiClient.get('/system/config');
        return response.data;
    },

    // --- NEW: Start New Simulation (Calibration) ---
    startNewSimulation: async () => {
        const response = await apiClient.post('/chat/start');
        return response.data;
    },

    // --- ORACLE (Legacy - kept for compatibility) ---
    initOracle: async () => {
        const response = await apiClient.post('/oracle/init');
        return response.data;
    },

    analyzeReaction: async (scenario, userReaction) => {
        const response = await apiClient.post('/oracle/analyze', {
            scenario,
            user_reaction: userReaction
        });
        return response.data;
    },

    // --- FOUNDRY (Legacy - kept for compatibility) ---
    genesis: async (userVibe) => {
        const response = await apiClient.post('/foundry/genesis', {
            user_vibe: userVibe
        });
        return response.data;
    },

    // --- CHAT (Interaction) ---
    sendMessage: async (simulationId, message) => {
        const response = await apiClient.post('/chat/message', {
            simulation_id: simulationId,
            user_message: message
        });
        return response.data;
    },

    // --- SIMULATIONS (Management) ---
    listSimulations: async () => {
        const response = await apiClient.get('/simulations/list');
        return response.data;
    },

    resetSimulation: async (simulationId) => {
        const response = await apiClient.post('/simulations/reset', {
            simulation_id: simulationId
        });
        return response.data;
    }
};
