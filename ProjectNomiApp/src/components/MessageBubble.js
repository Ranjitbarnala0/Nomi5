
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { THEME } from '../styles/theme';

export default function MessageBubble({ text, type }) {
    const isUser = type === 'user';
    const isSystem = type === 'system';

    if (isSystem) {
        return (
            <View style={styles.systemContainer}>
                <Text style={styles.systemText}>{text ? text.toUpperCase() : ''}</Text>
            </View>
        );
    }

    return (
        <View style={[
            styles.bubble,
            isUser ? styles.userBubble : styles.nomiBubble
        ]}>
            <Text style={styles.text}>{text}</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    systemContainer: {
        alignItems: 'center',
        marginVertical: 12,
        opacity: 0.7,
    },
    systemText: {
        color: THEME.colors.textDim,
        fontSize: 10,
        fontWeight: 'bold',
        letterSpacing: 1,
    },
    bubble: {
        maxWidth: '80%',
        padding: 14,
        borderRadius: 20,
        marginVertical: 2,
    },
    userBubble: {
        alignSelf: 'flex-end',
        backgroundColor: THEME.colors.userBubble,
        borderBottomRightRadius: 4,
    },
    nomiBubble: {
        alignSelf: 'flex-start',
        backgroundColor: THEME.colors.nomiBubble,
        borderBottomLeftRadius: 4,
    },
    text: {
        color: THEME.colors.text,
        fontSize: 16,
        lineHeight: 22,
    }
});
