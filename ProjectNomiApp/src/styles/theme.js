
import { StyleSheet } from 'react-native';
import { CONFIG } from '../core/config';

export const globalStyles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: CONFIG.THEME.BACKGROUND,
        paddingHorizontal: 20,
    },
    text: {
        color: CONFIG.THEME.TEXT_PRIMARY,
        fontSize: 16,
        fontFamily: 'System', // Will replace with custom font later if needed
    },
    header: {
        fontSize: 24,
        fontWeight: 'bold',
        color: CONFIG.THEME.ACCENT,
        marginBottom: 20,
        marginTop: 60,
    },
    input: {
        backgroundColor: '#1a1a1a',
        color: CONFIG.THEME.TEXT_PRIMARY,
        padding: 15,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#333',
        marginBottom: 15,
    },
    button: {
        backgroundColor: CONFIG.THEME.ACCENT,
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        justifyContent: 'center',
    },
    buttonText: {
        color: CONFIG.THEME.BACKGROUND,
        fontWeight: 'bold',
        fontSize: 16,
    }
});
