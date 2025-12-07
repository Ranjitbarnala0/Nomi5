
import React, { useEffect, useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity,
    StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform, Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NomiService } from '../services/nomi';
import { THEME } from '../styles/theme';

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
                <ActivityIndicator size="large" color={THEME.colors.primary} />
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
                        placeholderTextColor={THEME.colors.textDim}
                        value={response}
                        onChangeText={setResponse}
                        multiline
                    />

                    <TouchableOpacity
                        style={[styles.button, (!response.trim() || analyzing) && styles.buttonDisabled]}
                        onPress={handleSubmit}
                        disabled={!response.trim() || analyzing}
                    >
                        {analyzing ? (
                            <ActivityIndicator color={THEME.colors.text} />
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
        backgroundColor: THEME.colors.background,
    },
    center: {
        flex: 1,
        backgroundColor: THEME.colors.background,
        alignItems: 'center',
        justifyContent: 'center',
    },
    keyboardView: {
        flex: 1,
        justifyContent: 'space-between',
    },
    content: {
        padding: THEME.spacing.lg,
        marginTop: 20,
    },
    loadingText: {
        color: THEME.colors.textDim,
        marginTop: 20,
    },
    systemLabel: {
        color: THEME.colors.primary,
        fontSize: 12,
        letterSpacing: 2,
        marginBottom: 20,
        fontWeight: 'bold',
    },
    scenarioText: {
        color: THEME.colors.text,
        fontSize: 22,
        lineHeight: 34,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    },
    inputContainer: {
        padding: THEME.spacing.lg,
        backgroundColor: THEME.colors.surface,
        borderTopWidth: 1,
        borderTopColor: '#222',
    },
    input: {
        backgroundColor: THEME.colors.secondary,
        color: THEME.colors.text,
        padding: 20,
        borderRadius: THEME.borderRadius.lg,
        fontSize: 16,
        minHeight: 120,
        textAlignVertical: 'top',
        borderWidth: 1,
        borderColor: '#333',
    },
    button: {
        backgroundColor: THEME.colors.primary,
        marginTop: 20,
        padding: 18,
        borderRadius: THEME.borderRadius.xl,
        alignItems: 'center',
    },
    buttonDisabled: {
        backgroundColor: THEME.colors.secondary,
        opacity: 0.5,
    },
    buttonText: {
        color: '#fff',
        fontWeight: 'bold',
        letterSpacing: 1,
    }
});
