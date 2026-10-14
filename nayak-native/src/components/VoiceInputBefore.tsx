import { Pressable, StyleSheet, Text, View } from 'react-native'
import { Ionicons } from '@expo/vector-icons'

type VoiceInputProps = {
    status: 'sleeping' | 'listening' | 'processing'
    micOn: boolean
    micSupported: boolean
    toggleMic: () => void | Promise<void>
    interimText?: string
    error?: string | null
}

export default function VoiceInput({
    status,
    micOn,
    micSupported,
    toggleMic,
    interimText = '',
    error = null,
}: VoiceInputProps) {
    const disabled =
        !micSupported ||
        status === 'processing'

    async function handlePress() {
        if (disabled) {
            return
        }

        await toggleMic()
    }

    const orbState =
        status === 'processing'
            ? 'processing'
            : micOn
                ? 'listening'
                : 'sleeping'

    return (
        <View style={styles.container}>
            <Pressable
                onPress={handlePress}
                disabled={disabled}
                accessibilityRole="button"
                accessibilityLabel={
                    status === 'processing'
                        ? 'Processing voice input'
                        : micOn
                            ? 'Stop recording'
                            : 'Start voice recording'
                }
                style={({ pressed }) => [
                    styles.button,
                    orbState === 'listening' && styles.buttonListening,
                    pressed &&
                        !disabled &&
                        styles.pressed,
                    disabled &&
                        styles.disabled,
                ]}
            >
                <Ionicons
                    name={
                        orbState === 'listening'
                            ? 'stop'
                            : 'mic'
                    }
                    size={20}
                    color="#FFFFFF"
                />
            </Pressable>

            {status === 'listening' && (
                <Text style={styles.statusText}>
                    Listening… tap to stop
                </Text>
            )}

            {status === 'processing' && (
                <Text style={styles.statusText}>
                    {interimText || 'Transcribing…'}
                </Text>
            )}

            {error ? (
                <Text style={styles.errorText}>
                    {error}
                </Text>
            ) : null}
        </View>
    )
}

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
        justifyContent: 'center',
    },

    button: {
        width: 44,
        height: 44,
        borderRadius: 22,
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#6547D9',
    },

    buttonListening: {
        backgroundColor: '#DC2626',
    },

    pressed: {
        opacity: 0.75,
    },

    disabled: {
        opacity: 0.55,
    },

    statusText: {
        marginTop: 8,
        fontSize: 13,
        color: '#9CA3AF',
    },

    errorText: {
        marginTop: 8,
        paddingHorizontal: 20,
        textAlign: 'center',
        fontSize: 12,
        color: '#F87171',
    },
})
