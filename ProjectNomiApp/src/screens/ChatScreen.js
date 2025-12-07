
import React, { useState, useEffect, useRef } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, FlatList,
    StyleSheet, KeyboardAvoidingView, Platform, ActivityIndicator, Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';

import MessageBubble from '../components/MessageBubble';
import { NomiService } from '../services/nomi';
import { useSimulation } from '../core/context';
import { THEME } from '../styles/theme';

export default function ChatScreen({ navigation }) {
    const { simulationId, setSimulationId, logout } = useSimulation();

    // Core State
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [sending, setSending] = useState(false);
    const [typing, setTyping] = useState(false);
    const [loading, setLoading] = useState(true);

    // Calibration State
    const [isCalibrated, setIsCalibrated] = useState(false);
    const [personaName, setPersonaName] = useState('The System');

    // Status State
    const [simStatus, setSimStatus] = useState('ACTIVE');
    const [resetting, setResetting] = useState(false);

    const flatListRef = useRef();
    const currentSimId = useRef(simulationId);

    useEffect(() => {
        initializeChat();
    }, []);

    useEffect(() => {
        if (messages.length > 0 && currentSimId.current) {
            saveHistory();
        }
    }, [messages]);

    const initializeChat = async () => {
        try {
            setLoading(true);

            if (simulationId) {
                // Existing simulation - load history
                currentSimId.current = simulationId;
                await loadHistory();
                await syncStatus();
            } else {
                // NEW USER - Start fresh with System calibration
                await startNewSimulation();
            }
        } catch (error) {
            console.error('Init error:', error);
            setMessages([{
                id: 'error',
                text: 'Error connecting. Please restart the app.',
                type: 'system'
            }]);
        } finally {
            setLoading(false);
        }
    };

    const startNewSimulation = async () => {
        try {
            // Call backend to start new calibration
            const response = await NomiService.startNewSimulation();

            if (response.new_state?.simulation_id) {
                const newSimId = response.new_state.simulation_id;
                currentSimId.current = newSimId;

                // Save to context
                await setSimulationId(newSimId);

                // Set initial System message
                setMessages([{
                    id: 'system_init',
                    text: response.reply_text,
                    type: 'ai'
                }]);

                setIsCalibrated(false);
                setPersonaName('The System');
            }
        } catch (error) {
            console.error('Start simulation error:', error);
            setMessages([{
                id: 'error',
                text: 'Could not connect to The System. Please check your connection and restart.',
                type: 'system'
            }]);
        }
    };

    const loadHistory = async () => {
        try {
            const STORAGE_KEY = `@chat_history_${currentSimId.current}`;
            const stored = await AsyncStorage.getItem(STORAGE_KEY);

            if (stored) {
                setMessages(JSON.parse(stored));
            }
        } catch (e) {
            console.error('Load history error:', e);
        }
    };

    const saveHistory = async () => {
        try {
            if (currentSimId.current && messages.length > 0) {
                const STORAGE_KEY = `@chat_history_${currentSimId.current}`;
                await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
            }
        } catch (e) {
            console.error('Save history error:', e);
        }
    };

    const syncStatus = async () => {
        try {
            const sims = await NomiService.listSimulations();
            const mySim = sims.find(s => s.id === currentSimId.current);

            if (mySim) {
                setSimStatus(mySim.status);
                setIsCalibrated(mySim.is_calibrated || false);

                if (mySim.status === 'BROKEN' && simStatus !== 'BROKEN') {
                    setMessages(prev => [...prev, {
                        id: 'sys_break',
                        text: "CONNECTION SEVERED. USER HAS BLOCKED YOU.",
                        type: 'system'
                    }]);
                }
            }
        } catch (e) {
            console.log('Sync failed', e);
        }
    };

    const handleSend = async () => {
        if (!inputText.trim() || sending) return;
        if (simStatus === 'BROKEN') return;

        const userMsg = {
            id: Date.now().toString(),
            text: inputText,
            type: 'user'
        };

        // Optimistic Update
        setMessages(prev => [...prev, userMsg]);
        setInputText('');
        setSending(true);
        setTyping(true);

        try {
            const response = await NomiService.sendMessage(
                currentSimId.current,
                userMsg.text
            );

            setTyping(false);

            // Check if calibration just completed
            if (response.is_calibrated && !isCalibrated) {
                setIsCalibrated(true);

                if (response.persona_name) {
                    setPersonaName(response.persona_name);
                }
            }

            // Update status
            if (response.new_state?.emotional_bank_account <= -100) {
                setSimStatus('BROKEN');
            }

            // Add response messages
            const newMessages = [];

            if (response.narrative_bridge) {
                newMessages.push({
                    id: Date.now().toString() + '_narr',
                    text: response.narrative_bridge,
                    type: 'system'
                });
            }

            if (response.reply_text) {
                newMessages.push({
                    id: Date.now().toString() + '_ai',
                    text: response.reply_text,
                    type: 'ai'
                });
            }

            setMessages(prev => [...prev, ...newMessages]);

        } catch (error) {
            setTyping(false);
            console.error('Send error:', error);

            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                text: "Error: Connection lost. Tap to retry.",
                type: 'system'
            }]);
        } finally {
            setSending(false);
        }
    };

    const handleNewPersona = async () => {
        Alert.alert(
            "Start New Reality?",
            "This will create a completely new persona. Your current chat will be saved.",
            [
                { text: "Cancel", style: "cancel" },
                {
                    text: "New Persona",
                    style: "destructive",
                    onPress: async () => {
                        await logout();
                        setMessages([]);
                        setIsCalibrated(false);
                        setPersonaName('The System');
                        await startNewSimulation();
                    }
                }
            ]
        );
    };

    const handleTimeMachine = async () => {
        Alert.alert(
            "Reset Timeline?",
            "This will wipe all memories. They will forget everything.",
            [
                { text: "Cancel", style: "cancel" },
                {
                    text: "Reset",
                    style: "destructive",
                    onPress: async () => {
                        setResetting(true);
                        try {
                            await NomiService.resetSimulation(currentSimId.current);

                            const STORAGE_KEY = `@chat_history_${currentSimId.current}`;
                            await AsyncStorage.removeItem(STORAGE_KEY);

                            setMessages([{
                                id: Date.now().toString(),
                                text: "TIMELINE RESET. CONNECTION RE-ESTABLISHED.",
                                type: 'system'
                            }]);

                            setSimStatus('ACTIVE');
                        } catch (e) {
                            Alert.alert("Reset Failed", "Could not connect to the Time Machine.");
                        } finally {
                            setResetting(false);
                        }
                    }
                }
            ]
        );
    };

    const handleSettings = () => {
        Alert.alert(
            "Settings",
            null,
            [
                {
                    text: "New Persona",
                    onPress: handleNewPersona
                },
                {
                    text: "Reset Timeline",
                    onPress: handleTimeMachine,
                    style: "destructive"
                },
                {
                    text: "View All Simulations",
                    onPress: () => navigation.navigate('Simulations')
                },
                { text: "Cancel", style: "cancel" }
            ]
        );
    };

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color={THEME.colors.primary} />
                    <Text style={styles.loadingText}>Connecting to The System...</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <View style={styles.headerLeft}>
                    <Text style={styles.headerTitle}>{personaName}</Text>
                    <Text style={[
                        styles.headerStatus,
                        simStatus === 'BROKEN' ? styles.statusBroken :
                            isCalibrated ? styles.statusActive : styles.statusCalibrating
                    ]}>
                        {simStatus === 'BROKEN' ? 'DISCONNECTED' :
                            isCalibrated ? 'Online' : 'Calibrating...'}
                    </Text>
                </View>

                <TouchableOpacity
                    style={styles.settingsButton}
                    onPress={handleSettings}
                >
                    <Ionicons name="settings-outline" size={24} color={THEME.colors.textDim} />
                </TouchableOpacity>
            </View>

            {/* Chat Area */}
            <FlatList
                ref={flatListRef}
                data={messages}
                keyExtractor={item => item.id}
                renderItem={({ item }) => (
                    <MessageBubble
                        text={item.text}
                        type={item.type}
                    />
                )}
                contentContainerStyle={styles.listContent}
                onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                ListFooterComponent={typing ? (
                    <View style={styles.typingContainer}>
                        <Text style={styles.typingText}>
                            {isCalibrated ? personaName : 'The System'} is typing...
                        </Text>
                    </View>
                ) : null}
            />

            {/* Input Area */}
            <KeyboardAvoidingView
                behavior={Platform.OS === "ios" ? "padding" : "height"}
                keyboardVerticalOffset={Platform.OS === "ios" ? 10 : 0}
            >
                {simStatus === 'BROKEN' ? (
                    <View style={styles.brokenContainer}>
                        <Text style={styles.brokenText}>RELATIONSHIP SEVERED</Text>
                        <Text style={styles.brokenSubText}>Trust dropped below critical levels.</Text>
                        <TouchableOpacity
                            style={styles.resetButton}
                            onPress={handleTimeMachine}
                            disabled={resetting}
                        >
                            {resetting ? (
                                <ActivityIndicator color="#000" />
                            ) : (
                                <Text style={styles.resetButtonText}>RESET TIMELINE</Text>
                            )}
                        </TouchableOpacity>
                    </View>
                ) : (
                    <View style={styles.inputContainer}>
                        <TextInput
                            style={styles.input}
                            placeholder="Type a message..."
                            placeholderTextColor={THEME.colors.textDim}
                            value={inputText}
                            onChangeText={setInputText}
                            multiline
                            maxLength={500}
                        />
                        <TouchableOpacity
                            style={[styles.sendButton, !inputText.trim() && styles.disabled]}
                            onPress={handleSend}
                            disabled={!inputText.trim() || sending}
                        >
                            {sending ? (
                                <ActivityIndicator size="small" color="#fff" />
                            ) : (
                                <Ionicons name="arrow-up" size={24} color="#fff" />
                            )}
                        </TouchableOpacity>
                    </View>
                )}
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: THEME.colors.background,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingText: {
        color: THEME.colors.textDim,
        marginTop: 15,
        fontSize: 14,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: THEME.spacing.md,
        paddingVertical: THEME.spacing.md,
        borderBottomWidth: 1,
        borderBottomColor: '#222',
        backgroundColor: THEME.colors.surface,
    },
    headerLeft: {
        flex: 1,
    },
    headerTitle: {
        color: THEME.colors.text,
        fontSize: 18,
        fontWeight: 'bold',
    },
    headerStatus: {
        fontSize: 12,
        marginTop: 2,
    },
    statusActive: { color: '#4CAF50' },
    statusBroken: { color: '#F44336' },
    statusCalibrating: { color: THEME.colors.primary },
    settingsButton: {
        padding: 8,
    },
    listContent: {
        paddingHorizontal: THEME.spacing.md,
        paddingBottom: THEME.spacing.lg,
        paddingTop: THEME.spacing.md,
    },
    typingContainer: {
        marginLeft: 10,
        marginBottom: 10,
    },
    typingText: {
        color: THEME.colors.textDim,
        fontStyle: 'italic',
        fontSize: 12,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        padding: THEME.spacing.md,
        backgroundColor: THEME.colors.surface,
        borderTopWidth: 1,
        borderTopColor: '#222',
    },
    input: {
        flex: 1,
        backgroundColor: THEME.colors.secondary,
        color: THEME.colors.text,
        borderRadius: THEME.borderRadius.lg,
        paddingHorizontal: 15,
        paddingTop: 12,
        paddingBottom: 12,
        marginRight: 10,
        maxHeight: 120,
        fontSize: 16,
    },
    sendButton: {
        width: 45,
        height: 45,
        borderRadius: 22.5,
        backgroundColor: THEME.colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
    },
    disabled: {
        backgroundColor: THEME.colors.secondary,
        opacity: 0.5,
    },
    brokenContainer: {
        padding: 30,
        backgroundColor: '#1a0000',
        borderTopWidth: 1,
        borderTopColor: '#ff3333',
        alignItems: 'center',
    },
    brokenText: {
        color: '#ff3333',
        fontWeight: 'bold',
        fontSize: 18,
        letterSpacing: 2,
        marginBottom: 5,
    },
    brokenSubText: {
        color: '#999',
        marginBottom: 20,
    },
    resetButton: {
        backgroundColor: '#fff',
        paddingVertical: 12,
        paddingHorizontal: 30,
        borderRadius: 25,
    },
    resetButtonText: {
        color: '#000',
        fontWeight: 'bold',
        letterSpacing: 1,
    }
});
