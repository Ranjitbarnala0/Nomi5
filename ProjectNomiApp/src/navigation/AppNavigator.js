
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, StyleSheet } from 'react-native';
import { useSimulation } from '../core/context';

// Screens
import OracleScreen from '../screens/OracleScreen';
import GenesisScreen from '../screens/GenesisScreen';
import ChatScreen from '../screens/ChatScreen';
import SimulationsScreen from '../screens/SimulationsScreen'; // NEW

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
    const { simulationId, loading } = useSimulation();

    if (loading) {
        return (
            <View style={styles.center}>
                <Text style={styles.text}>Loading Memory...</Text>
            </View>
        );
    }

    return (
        <NavigationContainer>
            <Stack.Navigator screenOptions={{ headerShown: false, animation: 'fade' }}>
                {simulationId ? (
                    // If User has an ID, Main Stack
                    <>
                        <Stack.Screen name="Chat" component={ChatScreen} />
                        <Stack.Screen name="Simulations" component={SimulationsScreen} />
                    </>
                ) : (
                    // If No ID, Auth Stack
                    <>
                        <Stack.Screen name="Oracle" component={OracleScreen} />
                        <Stack.Screen name="Genesis" component={GenesisScreen} />
                        <Stack.Screen name="Chat" component={ChatScreen} />
                        <Stack.Screen name="Simulations" component={SimulationsScreen} />
                    </>
                )}
            </Stack.Navigator>
        </NavigationContainer>
    );
}

const styles = StyleSheet.create({
    center: {
        flex: 1,
        backgroundColor: '#000',
        alignItems: 'center',
        justifyContent: 'center',
    },
    text: {
        color: '#fff',
    }
});
