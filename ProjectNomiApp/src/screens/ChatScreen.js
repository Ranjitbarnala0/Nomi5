
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
    const { simulationId, persona } = useSimulation();
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [sending, setSending] = useState(false);
    const [typing, setTyping] = useState(false);

    // New State for Permadeath
    const [simStatus, setSimStatus] = useState('ACTIVE'); // ACTIVE, BROKEN
    const [trustScore, setTrustScore] = useState(0);
    const [resetting, setResetting] = useState(false);

    const flatListRef = useRef();
    const STORAGE_KEY = `@chat_history_${simulationId}`;

    useEffect(() => {
        loadHistory();
        syncStatus(); // Check server immediately
    }, []);

    useEffect(() => {
        saveHistory();
    }, [messages]);

    const loadHistory = async () => {
        try {
            const stored = await AsyncStorage.getItem(STORAGE_KEY);
            if (stored) {
                setMessages(JSON.parse(stored));
            } else {
                setMessages([{
                    id: 'init',
                    text: `Connection established with ${persona?.name || 'Subject'}.`,
                    type: 'system'
                }]);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const saveHistory = async () => {
        try {
            if (messages.length > 0) {
                await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
            }
        } catch (e) {
            console.error(e);
        }
    };

    // Sync with Server to check for Permadeath/Ghosting
    const syncStatus = async () => {
        try {
            const sims = await NomiService.listSimulations();
            const mySim = sims.find(s => s.id === simulationId);
            if (mySim) {
                setSimStatus(mySim.status);
                setTrustScore(mySim.emotional_bank_account);

                // If broken, ensure we show the breakup status locally
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

        // Guard Clause: Cannot send if broken
        if (simStatus === 'BROKEN') return;

        const userMsg = { id: Date.now().toString(), text: inputText, type: 'user' };

        // Optimistic Update: Show message immediately
        setMessages(prev => [...prev, userMsg]);
        setInputText('');
        setSending(true);
        setTyping(true); // Show typing indicator

        try {
            const response = await NomiService.sendMessage(simulationId, userMsg.text);

            // Hide typing indicator
            setTyping(false);

            // Update our local state based on the response logic
            if (response.new_state) {
                // If the trust drops too low during this chat, update status
                if (response.new_state.emotional_bank_account <= -100) {
                    setSimStatus('BROKEN');
                }
            }

            const newMessages = [];
            if (response.narrative_bridge) {
                newMessages.push({
                    id: Date.now().toString() + '_sys',
                    text: response.narrative_bridge,
                    type: 'system'
                });
            }

            newMessages.push({
                id: Date.now().toString() + '_ai',
                text: response.reply_text,
                type: 'ai'
            });

            setMessages(prev => [...prev, ...newMessages]);

        } catch (error) {
            setTyping(false);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                text: "Error: Connection lost.",
                type: 'system'
            }]);
        } finally {
            setSending(false);
        }
    };

    const handleTimeMachine = async () => {
        Alert.alert(
            "Reset Timeline?",
            "This will wipe all memories of your relationship. She will forget everything. Are you sure? (Cost: 1 Credit)",
            [
                { text: "Cancel", style: "cancel" },
                {
                    text: "Reset",
                    style: "destructive",
                    onPress: async () => {
                        setResetting(true);
                        try {
                            // 1. Call Backend Reset
                            await NomiService.resetSimulation(simulationId);

                            // 2. Wipe Local History
                            await AsyncStorage.removeItem(STORAGE_KEY);
                            setMessages([{
                                id: Date.now().toString(),
                                text: "TIMELINE RESET. CONNECTION RE-ESTABLISHED.",
                                type: 'system'
                            }]);

                            // 3. Reset State
                            setSimStatus('ACTIVE');
                            setTrustScore(0);

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

    return (
        <SafeAreaView style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.headerTitle}>{persona?.name || 'Unknown'}</Text>
                    <Text style={[
                        styles.headerStatus,
                        simStatus === 'BROKEN' ? styles.statusBroken : styles.statusActive
                    ]}>
                        {simStatus === 'BROKEN' ? 'DISCONNECTED' : 'Online'}
                    </Text>
                </View>
                <TouchableOpacity
                    style={styles.menuButton}
                    onPress={() => navigation.navigate('Simulations')}
                >
                    <Ionicons name="albums-outline" size={24} color={THEME.colors.textDim} />
                </TouchableOpacity>
            </View>

            {/* Chat Area */}
            <FlatList
                ref={flatListRef}
                data={messages}
                keyExtractor={item => item.id}
                renderItem={({ item }) => <MessageBubble text={item.text} type={item.type} />}
                contentContainerStyle={styles.listContent}
                onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
                ListFooterComponent={typing ? (
                    <View style={styles.typingContainer}>
                        <Text style={styles.typingText}>{persona?.name || 'Nomi'} is typing...</Text>
                    </View>
                ) : null}
            />

            {/* Input Area OR Permadeath UI */}
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
                        />
                        <TouchableOpacity
                            style={[styles.sendButton, !inputText.trim() && styles.disabled]}
                            onPress={handleSend}
                            disabled={!inputText.trim()}
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

    // Normal Input Styles
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
        paddingTop: 10,
        paddingBottom: 10,
        marginRight: 10,
        maxHeight: 100,
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

    // Permadeath Styles
    brokenContainer: {
        padding: 30,
        backgroundColor: '#1a0000', // Deep red/black
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
