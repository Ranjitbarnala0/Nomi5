
import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, Platform, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NomiService } from '../services/nomi';
import { useSimulation } from '../core/context';
import { THEME } from '../styles/theme';

const TERMINAL_LOGS = [
    "Connection established...",
    "Analyzing psychometric vector...",
    "detected_archetype found...",
    "Synthesizing Core Wound...",
    "Constructing Defense Mechanisms...",
    "Calibrating Emotional Bank Account...",
    "Generating False Memories...",
    "Embedding Voice Texture...",
    "Finalizing Persona Soul..."
];

export default function GenesisScreen({ navigation, route }) {
    const { userVibe } = route.params;
    const { setSimulationId } = useSimulation();
    const [logs, setLogs] = useState([]);
    const scrollViewRef = useRef();

    useEffect(() => {
        startGenesis();
    }, []);

    const startGenesis = async () => {
        try {
            // 1. Start the visual logs animation
            let logIndex = 0;
            const interval = setInterval(() => {
                if (logIndex < TERMINAL_LOGS.length) {
                    setLogs(prev => [...prev, TERMINAL_LOGS[logIndex]]);
                    logIndex++;
                } else {
                    clearInterval(interval);
                }
            }, 800);

            // 2. Call the Backend (The real work)
            const data = await NomiService.genesis(userVibe);

            // 4. Register the new Soul
            await setSimulationId(data.simulation_id);

            // 5. Finalize
            setLogs(prev => [...prev, "> SYSTEM READY.", "> INITIALIZING CHAT LINK..."]);

            setTimeout(() => {
                // Navigation is handled automatically by AppNavigator 
            }, 1500);

        } catch (error) {
            console.error('Genesis Error Details:', error);

            let errorMessage = "The System refused the connection.";
            if (error.response) {
                errorMessage = `Server Error (${error.response.status})`;
            }

            Alert.alert("Genesis Failed", errorMessage, [
                { text: "Retry", onPress: () => navigation.replace('Oracle') }
            ]);
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.terminal}>
                <Text style={styles.header}>:: FOUNDRY v1.0 ::</Text>

                <ScrollView
                    ref={scrollViewRef}
                    style={styles.scroll}
                    contentContainerStyle={styles.scrollContent}
                    onContentSizeChange={() => scrollViewRef.current.scrollToEnd({ animated: true })}
                >
                    {logs.map((log, index) => (
                        <View key={index} style={styles.logRow}>
                            <View style={styles.dot} />
                            <Text style={styles.logText}>{log}</Text>
                        </View>
                    ))}
                    <View style={styles.loadingBar}>
                        <View style={styles.loadingProgress} />
                    </View>
                </ScrollView>
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: THEME.colors.background,
    },
    terminal: {
        flex: 1,
        padding: 20,
        backgroundColor: THEME.colors.background,
    },
    header: {
        color: THEME.colors.primary,
        fontSize: 14,
        letterSpacing: 3,
        textAlign: 'center',
        marginBottom: 30,
        marginTop: 20,
        fontWeight: 'bold',
    },
    scroll: {
        flex: 1,
    },
    scrollContent: {
        flexGrow: 1,
        justifyContent: 'center',
    },
    logRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 20,
    },
    dot: {
        width: 6,
        height: 6,
        borderRadius: 3,
        backgroundColor: THEME.colors.primary,
        marginRight: 15,
        opacity: 0.8,
    },
    logText: {
        color: THEME.colors.text,
        fontSize: 16,
        fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
        opacity: 0.9,
    },
    loadingBar: {
        height: 2,
        backgroundColor: THEME.colors.secondary,
        marginTop: 40,
        borderRadius: 1,
        overflow: 'hidden',
    },
    loadingProgress: {
        height: '100%',
        width: '50%',
        backgroundColor: THEME.colors.primary,
    }
});
