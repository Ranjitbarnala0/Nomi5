
import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SimulationContext = createContext();

export const SimulationProvider = ({ children }) => {
    const [simulationId, setSimulationId] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkSimulation();
    }, []);

    const checkSimulation = async () => {
        try {
            const id = await AsyncStorage.getItem('simulation_id');
            setSimulationId(id);
        } catch (e) {
            console.error("Failed to load simulation ID", e);
        } finally {
            setLoading(false);
        }
    };

    const login = async (id) => {
        try {
            await AsyncStorage.setItem('simulation_id', id);
            setSimulationId(id);
        } catch (e) {
            console.error("Failed to save simulation ID", e);
        }
    };

    const logout = async () => {
        try {
            await AsyncStorage.removeItem('simulation_id');
            setSimulationId(null);
        } catch (e) {
            console.error("Failed to remove simulation ID", e);
        }
    };

    return (
        <SimulationContext.Provider value={{ simulationId, setSimulationId: login, logout, loading }}>
            {children}
        </SimulationContext.Provider>
    );
};

export const useSimulation = () => useContext(SimulationContext);
