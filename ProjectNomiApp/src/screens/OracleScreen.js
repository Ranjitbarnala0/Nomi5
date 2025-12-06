
import React, { useEffect, useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity,
    StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform, Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NomiService } from '../services/nomi';
import { CONFIG } from '../core/config';

export default function OracleScreen({ navigation }) {
    const [scenario, setScenario] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(true);
    const [analyzing, setAnalyzing] = useState(false);

    useEffect(() => {
        loadScenario();
    }, []);

    const loadScenario = async () => {
        try {
            const data = await NomiService.initOracle();
            setScenario(data.scenario_text);
            setLoading(false);
        } catch (error) {
            Alert.alert('Connection Error', 'Could not reach the System. Check your server.');
            setLoading(false);
        }
    };

    const handleSubmit = async () => {
        if (!response.trim()) return;

        setAnalyzing(true);
        try {
            // 1. Send reaction to Brain
            const analysis = await NomiService.analyzeReaction(scenario, response);

            // 2. Navigate to Genesis (Foundry) with the calculated "Vibe"
            navigation.replace('Genesis', { userVibe: analysis.user_vibe });
        } catch (error) {
            Alert.alert('Error', 'The System could not process your response.');
            setAnalyzing(false);
        }
    };

    if (loading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" color="#fff" />
                <Text style={styles.loadingText}>Initializing Simulation...</Text>
            </View>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <KeyboardAvoidingView
                behavior={Platform.OS === "ios" ? "padding" : "height"}
                style={styles.keyboardView}
            >
                <View style={styles.content}>
                    <Text style={styles.systemLabel}>SYSTEM MESSAGE</Text>
                    <Text style={styles.scenarioText}>{scenario}</Text>
                </View>

                <View style={styles.inputContainer}>
                    <TextInput
                        style={styles.input}
                        placeholder="What do you do?"
                        placeholderTextColor="#666"
                        value={response}
                        onChangeText={setResponse}
                    />

                    <TouchableOpacity
                        style={[styles.button, (!response.trim() || analyzing) && styles.buttonDisabled]}
                        onPress={handleSubmit}
                        disabled={!response.trim() || analyzing}
                    >
                        {analyzing ? (
                            <ActivityIndicator color="#000" />
                        ) : (
                            <Text style={styles.buttonText}>INITIALIZE</Text>
                        )}
                    </TouchableOpacity>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0a0a0a',
    },
    center: {
        flex: 1,
        backgroundColor: '#0a0a0a',
        alignItems: 'center',
        justifyContent: 'center',
    },
    keyboardView: {
        flex: 1,
        justifyContent: 'space-between',
    },
    content: {
        padding: 24,
        marginTop: 20,
    },
    loadingText: {
        color: '#666',
        marginTop: 20,
        fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    },
    systemLabel: {
        color: CONFIG.THEME.SYSTEM_MSG,
        fontSize: 12,
        letterSpacing: 2,
        marginBottom: 20,
        fontWeight: 'bold',
    },
    scenarioText: {
        color: '#fff',
        fontSize: 22,
        lineHeight: 34,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    },
    inputContainer: {
        padding: 24,
        backgroundColor: '#111',
        borderTopWidth: 1,
        borderTopColor: '#222',
    },
    input: {
        backgroundColor: '#1a1a1a',
        color: '#fff',
        padding: 20,
        borderRadius: 12,
        fontSize: 16,
        minHeight: 100,
        textAlignVertical: 'top',
        borderWidth: 1,
        borderColor: '#333',
    },
    button: {
        backgroundColor: '#fff',
        marginTop: 20,
        padding: 18,
        borderRadius: 30,
        alignItems: 'center',
    },
    buttonDisabled: {
        backgroundColor: '#333',
    },
    buttonText: {
        color: '#000',
        fontWeight: 'bold',
        letterSpacing: 1,
    }
});
