
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useSimulation } from '../core/context';

// Screens
import ChatScreen from '../screens/ChatScreen';
import SimulationsScreen from '../screens/SimulationsScreen';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
    const { loading } = useSimulation();

    if (loading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" color="#9333EA" />
                <Text style={styles.text}>Loading...</Text>
            </View>
        );
    }

    return (
        <NavigationContainer>
            <Stack.Navigator
                screenOptions={{
                    headerShown: false,
                    animation: 'fade',
                    contentStyle: { backgroundColor: '#0A0A0F' }
                }}
            >
                <Stack.Screen name="Chat" component={ChatScreen} />
                <Stack.Screen name="Simulations" component={SimulationsScreen} />
            </Stack.Navigator>
        </NavigationContainer>
    );
}

const styles = StyleSheet.create({
    center: {
        flex: 1,
        backgroundColor: '#0A0A0F',
        alignItems: 'center',
        justifyContent: 'center',
    },
    text: {
        color: '#888',
        marginTop: 10,
    }
});
