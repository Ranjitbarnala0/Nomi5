
import React, { useEffect, useState } from 'react';
import {
    View, Text, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator, Alert, Platform
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { NomiService } from '../services/nomi';
import { useSimulation } from '../core/context';
import { THEME } from '../styles/theme';

export default function SimulationsScreen({ navigation }) {
    // Aliasing context methods to match the requested variable names while maintaining compatibility with context.js
    const { setSimulationId: registerSimulation, logout: clearSimulation } = useSimulation();
    const [sims, setSims] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadSimulations();
    }, []);

    const loadSimulations = async () => {
        try {
            const data = await NomiService.listSimulations();
            setSims(data);
        } catch (error) {
            Alert.alert('Error', 'Could not fetch universes.');
        } finally {
            setLoading(false);
        }
    };

    const handleSwitch = async (sim) => {
        // 1. Update Global Context
        await registerSimulation(sim.id /*, { name: sim.name, avatar: sim.avatar } */);

        // 2. Go back to Chat (Context update will trigger re-render of content)
        navigation.navigate('Chat');
    };

    const handleNew = async () => {
        // Clear current context so Navigator sees "No ID" and renders Oracle
        await clearSimulation();
        // Navigation happens automatically via AppNavigator logic
    };

    const renderItem = ({ item }) => {
        const isBroken = item.status === 'BROKEN';
        return (
            <TouchableOpacity
                style={[styles.card, isBroken && styles.cardBroken]}
                onPress={() => handleSwitch(item)}
            >
                <View style={styles.cardHeader}>
                    <Text style={[styles.name, isBroken && styles.textBroken]}>{item.name}</Text>
                    <Text style={[styles.status, isBroken ? styles.statusBroken : styles.statusActive]}>
                        {isBroken ? 'DISCONNECTED' : 'ACTIVE'}
                    </Text>
                </View>

                <Text style={styles.detail}>
                    Trust Score: <Text style={item.emotional_bank_account < 0 ? styles.negative : styles.positive}>
                        {item.emotional_bank_account}
                    </Text>
                </Text>

                <Text style={styles.id}>ID: {item.id.substring(0, 8)}...</Text>
            </TouchableOpacity>
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
                    <Ionicons name="arrow-back" size={24} color={THEME.colors.text} />
                </TouchableOpacity>
                <Text style={styles.headerTitle}>YOUR UNIVERSES</Text>
                <View style={{ width: 24 }} />
            </View>

            {loading ? (
                <ActivityIndicator size="large" color={THEME.colors.primary} style={{ marginTop: 50 }} />
            ) : (
                <FlatList
                    data={sims}
                    renderItem={renderItem}
                    keyExtractor={item => item.id}
                    contentContainerStyle={styles.list}
                    ListEmptyComponent={
                        <Text style={styles.emptyText}>No active realities found.</Text>
                    }
                />
            )}

            <TouchableOpacity style={styles.fab} onPress={handleNew}>
                <Ionicons name="add" size={30} color="#fff" />
            </TouchableOpacity>
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
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: THEME.spacing.lg,
        borderBottomWidth: 1,
        borderBottomColor: '#222',
        backgroundColor: THEME.colors.surface,
    },
    headerTitle: {
        color: THEME.colors.text,
        fontSize: 16,
        fontWeight: 'bold',
        letterSpacing: 2,
    },
    list: {
        padding: THEME.spacing.lg,
    },
    card: {
        backgroundColor: THEME.colors.surface,
        padding: THEME.spacing.lg,
        borderRadius: THEME.borderRadius.lg,
        marginBottom: 15,
        borderWidth: 1,
        borderColor: '#333',
    },
    cardBroken: {
        borderColor: '#550000',
        backgroundColor: '#1a0000',
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 10,
    },
    name: {
        color: THEME.colors.text,
        fontSize: 18,
        fontWeight: 'bold',
    },
    textBroken: {
        color: THEME.colors.error,
    },
    status: {
        fontSize: 12,
        fontWeight: 'bold',
    },
    statusActive: { color: '#4CAF50' },
    statusBroken: { color: THEME.colors.error },
    detail: {
        color: THEME.colors.textDim,
        marginBottom: 5,
    },
    positive: { color: '#4CAF50' },
    negative: { color: THEME.colors.error },
    id: {
        color: '#444',
        fontSize: 10,
        fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    },
    emptyText: {
        color: THEME.colors.textDim,
        textAlign: 'center',
        marginTop: 50,
    },
    fab: {
        position: 'absolute',
        bottom: 30,
        right: 30,
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: THEME.colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
        elevation: 5,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 5,
    }
});
