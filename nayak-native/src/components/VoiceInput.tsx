import { Pressable, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'

type VoiceInputProps = {
    status: 'sleeping' | 'listening' | 'processing'
    micOn: boolean
    micSupported: boolean
    toggleMic: () => void | Promise<void>
    disabled?: boolean
}

// Compact mic/stop button meant to sit inline inside the composer row
// (see chat.tsx). Status text, interim transcript, and error surfacing
// now live in the composer itself so they aren't duplicated here.
export default function VoiceInput({
    status,
    micOn,
    micSupported,
    toggleMic,
    disabled: externallyDisabled = false,
}: VoiceInputProps) {
    const disabled =
        !micSupported ||
        status === 'processing' ||
        externallyDisabled

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
                pressed && !disabled && styles.pressed,
                disabled && styles.disabled,
            ]}
        >
            <Ionicons
                name={orbState === 'listening' ? 'stop' : 'mic'}
                size={19}
                color="#FFFFFF"
            />
        </Pressable>
    )
}

const styles = StyleSheet.create({
    button: {
        width: 42,
        height: 42,
        borderRadius: 21,
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
        opacity: 0.4,
    },
})
