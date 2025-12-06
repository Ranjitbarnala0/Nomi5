
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { CONFIG } from '../core/config';

export default function MessageBubble({ text, type }) {
    // Types: 'user', 'ai', 'system'

    if (type === 'system') {
        return (
            <View style={styles.systemContainer}>
                <Text style={styles.systemText}>{text}</Text>
            </View>
        );
    }

    const isUser = type === 'user';

    return (
        <View style={[
            styles.bubble,
            isUser ? styles.userBubble : styles.aiBubble
        ]}>
            <Text style={[
                styles.text,
                isUser ? styles.userText : styles.aiText
            ]}>
                {text}
            </Text>
        </View>
    );
}

const styles = StyleSheet.create({
    systemContainer: {
        alignItems: 'center',
        marginVertical: 15,
        paddingHorizontal: 20,
    },
    systemText: {
        color: CONFIG.THEME.SYSTEM_MSG,
        fontStyle: 'italic',
        fontSize: 12,
        textAlign: 'center',
    },
    bubble: {
        maxWidth: '80%',
        padding: 12,
        borderRadius: 16,
        marginVertical: 4,
    },
    userBubble: {
        alignSelf: 'flex-end',
        backgroundColor: '#fff', // High contrast for user
        borderBottomRightRadius: 2,
    },
    aiBubble: {
        alignSelf: 'flex-start',
        backgroundColor: '#222',
        borderBottomLeftRadius: 2,
        borderWidth: 1,
        borderColor: '#333',
    },
    text: {
        fontSize: 16,
        lineHeight: 22,
    },
    userText: {
        color: '#000',
    },
    aiText: {
        color: '#eee',
    },
});
