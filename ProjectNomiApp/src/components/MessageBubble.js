
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { THEME } from '../styles/theme';

/**
 * Parses text with *italics* markers and returns styled components
 */
const parseItalics = (text) => {
    if (!text) return null;

    const parts = text.split(/(\*[^*]+\*)/g);

    return parts.map((part, index) => {
        if (part.startsWith('*') && part.endsWith('*')) {
            // Remove the asterisks and render as italic
            return (
                <Text key={index} style={styles.italic}>
                    {part.slice(1, -1)}
                </Text>
            );
        }
        return <Text key={index}>{part}</Text>;
    });
};

export default function MessageBubble({ text, type }) {
    const isUser = type === 'user';
    const isSystem = type === 'system';

    if (isSystem) {
        return (
            <View style={styles.systemContainer}>
                <Text style={styles.systemText}>{text}</Text>
            </View>
        );
    }

    return (
        <View style={[
            styles.bubble,
            isUser ? styles.userBubble : styles.aiBubble
        ]}>
            <Text style={[styles.text, isUser && styles.userText]}>
                {isUser ? text : parseItalics(text)}
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
        color: THEME.colors.textDim,
        fontSize: 12,
        textAlign: 'center',
        lineHeight: 18,
    },
    bubble: {
        maxWidth: '85%',
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderRadius: 20,
        marginVertical: 4,
    },
    userBubble: {
        alignSelf: 'flex-end',
        backgroundColor: THEME.colors.primary,
        borderBottomRightRadius: 6,
    },
    aiBubble: {
        alignSelf: 'flex-start',
        backgroundColor: THEME.colors.surface,
        borderWidth: 1,
        borderColor: '#333',
        borderBottomLeftRadius: 6,
    },
    text: {
        color: THEME.colors.text,
        fontSize: 16,
        lineHeight: 24,
    },
    userText: {
        color: '#fff',
    },
    italic: {
        fontStyle: 'italic',
        color: THEME.colors.textDim,
    }
});
