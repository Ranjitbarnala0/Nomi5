
import apiClient from './api';

/**
 * The Nomi Service
 * Maps JavaScript functions to Python Backend API endpoints.
 */
export const NomiService = {

    // --- SYSTEM ---
    checkHealth: async () => {
        // Calls /api/v1/system/diagnostics
        const response = await apiClient.get('/system/diagnostics');
        return response.data;
    },

    getAppConfig: async () => {
        // Calls /api/v1/system/config
        const response = await apiClient.get('/system/config');
        return response.data;
    },

    // --- ORACLE (The Test) ---
    initOracle: async () => {
        // POST /api/v1/oracle/init
        const response = await apiClient.post('/oracle/init');
        return response.data;
    },

    analyzeReaction: async (scenario, userReaction) => {
        // POST /api/v1/oracle/analyze
        const response = await apiClient.post('/oracle/analyze', {
            scenario,
            user_reaction: userReaction
        });
        return response.data; // Returns { user_vibe: ... }
    },

    // --- FOUNDRY (Genesis) ---
    genesis: async (userVibe) => {
        // POST /api/v1/foundry/genesis
        const response = await apiClient.post('/foundry/genesis', {
            user_vibe: userVibe
        });
        return response.data; // Returns { simulation_id, persona }
    },

    // --- CHAT (Interaction) ---
    sendMessage: async (simulationId, message) => {
        // POST /api/v1/chat/message
        const response = await apiClient.post('/chat/message', {
            simulation_id: simulationId,
            user_message: message
        });
        return response.data; // Returns { reply_text, narrative_bridge, ... }
    },

    // --- SIMULATIONS (Management) ---
    listSimulations: async () => {
        // GET /api/v1/simulations/list
        const response = await apiClient.get('/simulations/list');
        return response.data;
    },

    resetSimulation: async (simulationId) => {
        // POST /api/v1/simulations/reset
        const response = await apiClient.post('/simulations/reset', {
            simulation_id: simulationId
        });
        return response.data;
    }
};
