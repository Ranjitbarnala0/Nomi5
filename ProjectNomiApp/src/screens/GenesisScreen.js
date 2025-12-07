
import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, Platform, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NomiService } from '../services/nomi';
import { useSimulation } from '../core/context';

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
            // This might take 5-10 seconds depending on Gemini/Nvidia
            const data = await NomiService.genesis(userVibe);

            // 3. Wait for logs to finish visually if API was too fast
            // (Optional polish, but ensures user sees the "magic")

            // 4. Register the new Soul
            // Note: The context provider exposes setSimulationId as 'login', but user requested 'registerSimulation'. 
            // I need to check src/core/context.js.
            // Looking at the previous turn (Step 880), the Provider exposes { simulationId, setSimulationId: login, logout, loading }.
            // The user instruction uses `registerSimulation`.
            // I will assume `registerSimulation` is intended to be the `login` function from context.
            // Wait, let me re-read context.js creation in Step 880.
            // It exports: <SimulationContext.Provider value={{ simulationId, setSimulationId: login, logout, loading }}>
            // So 'setSimulationId' is the function name exposed, which maps to 'login'.
            // The user's provided code for GenesisScreen uses `const { registerSimulation } = useSimulation();`.
            // This means I either need to update Context to expose `registerSimulation` or update GenesisScreen to use `setSimulationId`.
            // STRICT RULE: "Output FULL file contents." 
            // If I use the provided code for GenesisScreen, it will break because `registerSimulation` doesn't exist in Context.
            // I should FIX this by mapping `registerSimulation: login` in the Context Provider OR update the usage here.
            // But I cannot modify Context.js in this turn (instructions say "YOU WILL MODIFY: 1 existing file (AppNavigator.js)").
            // So I must assume the user wants me to use the code provided for GenesisScreen, but it relies on a function name that might be mismatched.
            // Ah, I created context.js in Step 880. Let me check what I actually wrote.
            // `value={{ simulationId, setSimulationId: login, logout, loading }}`
            // The provided GenesisScreen code uses `const { registerSimulation } = useSimulation();`.
            // This IS A BUG in the user's provided snippets vs my previous implementation.
            // However, the instructions say "YOU WILL CREATE: 1 new file" (GenesisScreen).
            // I will Modify `src/core/context.js` as well to fix this mismatch, or I will use `setSimulationId` in GenesisScreen and alias it there?
            // "YOU WILL CREATE: 1 new file YOU WILL MODIFY: 1 existing file (src/navigation/AppNavigator.js)"
            // This puts me in a bind.
            // I will check if I can alias it in the component: `const { setSimulationId: registerSimulation } = useSimulation();`
            // No, because destructuring pulls by key.
            // I will modify `GenesisScreen.js` to use `setSimulationId` instead of `registerSimulation` to match the Context I created. 
            // OR I can just modify Context.js quickly? No, limiting file edits is safer.
            // I'll update GenesisScreen code to destructure `{ setSimulationId }` and then call it `registerSimulation` or just call `setSimulationId(data.simulation_id)`.
            // Actually, the user's snippet for GenesisScreen calls `await registerSimulation(data.simulation_id, data.persona);`.
            // My `login` function in context only takes `id`. `login = async (id) => ...`.
            // The persona data is not saved in context, just ID.
            // So I will adapt GenesisScreen to: `const { setSimulationId } = useSimulation();` and `await setSimulationId(data.simulation_id);`.
            // Wait, is "registerSimulation" supposed to do more? The instructions say "Calls registerSimulation() to save to disk."
            // My `login` does `AsyncStorage.setItem`. That matches.
            // Okay, I will modify the provided GenesisScreen code slightly to match my Context implementation.

            await setSimulationId(data.simulation_id);

            // 5. Finalize
            setLogs(prev => [...prev, "> SYSTEM READY.", "> INITIALIZING CHAT LINK..."]);

            setTimeout(() => {
                // Navigation is handled automatically by AppNavigator 
            }, 1500);

        } catch (error) {
            console.error('Genesis Error Details:', error);
            console.error('Error message:', error.message);
            console.error('Error response:', error.response?.data);
            console.error('Error status:', error.response?.status);

            let errorMessage = "The System refused the connection.";
            if (error.response) {
                errorMessage = `Server Error (${error.response.status}): ${JSON.stringify(error.response.data)}`;
            } else if (error.code === 'ECONNABORTED') {
                errorMessage = "Request timed out. The AI is taking too long.";
            } else if (error.message) {
                errorMessage = error.message;
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
                <View style={styles.divider} />

                <ScrollView
                    ref={scrollViewRef}
                    style={styles.scroll}
                    onContentSizeChange={() => scrollViewRef.current.scrollToEnd({ animated: true })}
                >
                    {logs.map((log, index) => (
                        <Text key={index} style={styles.logText}>
                            <Text style={styles.prefix}>{"> "}</Text>
                            {log}
                        </Text>
                    ))}
                    <Text style={styles.cursor}>_</Text>
                </ScrollView>
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#000',
    },
    terminal: {
        flex: 1,
        padding: 20,
    },
    header: {
        color: '#33ff33', // Terminal Green
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
        textAlign: 'center',
        marginBottom: 10,
        opacity: 0.8,
    },
    divider: {
        height: 1,
        backgroundColor: '#33ff33',
        marginBottom: 20,
        opacity: 0.3,
    },
    scroll: {
        flex: 1,
    },
    logText: {
        color: '#33ff33',
        fontSize: 16,
        fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
        marginBottom: 12,
        lineHeight: 24,
    },
    prefix: {
        opacity: 0.5,
    },
    cursor: {
        color: '#33ff33',
        fontSize: 16,
        fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
        animationDuration: '1s', // Note: RN doesn't support CSS animation directly, simplified for MVP
    }
});
