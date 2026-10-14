import { useCallback, useEffect, useRef, useState } from 'react'
import {
    AudioModule,
    RecordingPresets,
    setAudioModeAsync,
    useAudioRecorder,
    useAudioRecorderState,
} from 'expo-audio'
import { api } from '../lib/api.js'

export function useNayak({ onExchange, sessionId } = {}) {
    const [status, setStatus] = useState('sleeping')
    const [micOn, setMicOn] = useState(false)
    const [interimText, setInterimText] = useState('')
    const [micLevel, setMicLevel] = useState(0)
    const [error, setError] = useState(null)

    const recorder = useAudioRecorder(
        RecordingPresets.HIGH_QUALITY,
    )

    const recorderState = useAudioRecorderState(recorder)

    const mountedRef = useRef(true)
    const processingRef = useRef(false)

    const micSupported = true

    const sendCommand = useCallback(
        async (text) => {
            const cleanText = text?.trim()

            if (!cleanText || processingRef.current) {
                return
            }

            processingRef.current = true

            setStatus('processing')
            setInterimText('')
            setError(null)

            try {
                const data = await api.command({
                    text: cleanText,
                    session_id: sessionId,
                })

                const reply =
                    data?.response ??
                    data?.reply ??
                    data?.content ??
                    '(backend reply had no recognizable text field)'

                onExchange?.({
                    userText: cleanText,
                    assistantText: reply,
                })

                if (
                    data?.session_id &&
                    data.session_id !== sessionId
                ) {
                    console.log(
                        '[useNayak] backend returned session:',
                        data.session_id,
                    )
                }

                if (mountedRef.current) {
                    setStatus('sleeping')
                    setError(null)
                }
            } catch (err) {
                console.error(
                    '[useNayak] command failed:',
                    err,
                )

                if (mountedRef.current) {
                    setError(
                        `Could not reach the Nayak backend: ${err.message}`,
                    )

                    setStatus('sleeping')

                    onExchange?.({
                        userText: cleanText,
                        assistantText:
                            `Could not reach the backend (${err.message}).`,
                        isError: true,
                    })
                }
            } finally {
                processingRef.current = false
            }
        },
        [onExchange, sessionId],
    )

    const stopRecording = useCallback(async () => {
        if (!recorderState.isRecording) {
            return
        }

        try {
            setStatus('processing')
            setMicOn(false)

            await recorder.stop()

            const uri = recorder.uri

            if (!uri) {
                throw new Error(
                    'Recording stopped but no audio file was created',
                )
            }

            console.log(
                '[useNayak] recording:',
                uri,
            )

            setInterimText('Transcribing…')

            const transcription =
                await api.transcribeAudio(uri)

            const transcript =
                transcription?.text?.trim()

            if (!transcript) {
                throw new Error(
                    'The backend returned an empty transcript',
                )
            }

            console.log(
                '[useNayak] transcript:',
                transcript,
            )

            setInterimText(transcript)

            await sendCommand(transcript)
        } catch (err) {
            console.error(
                '[useNayak] voice pipeline failed:',
                err,
            )

            if (mountedRef.current) {
                setMicOn(false)
                setStatus('sleeping')
                setInterimText('')
                setError(
                    `Voice input failed: ${err.message}`,
                )
            }
        }
    }, [
        recorder,
        recorderState.isRecording,
        sendCommand,
    ])

    const startRecording = useCallback(async () => {
        if (
            processingRef.current ||
            recorderState.isRecording
        ) {
            return
        }

        setError(null)
        setInterimText('')

        try {
            const permission =
                await AudioModule.requestRecordingPermissionsAsync()

            if (!permission.granted) {
                throw new Error(
                    'Microphone permission was denied',
                )
            }

            await setAudioModeAsync({
                allowsRecording: true,
                playsInSilentMode: true,
            })

            await recorder.prepareToRecordAsync()

            recorder.record()

            setMicOn(true)
            setStatus('listening')

            console.log(
                '[useNayak] recording started',
            )
        } catch (err) {
            console.error(
                '[useNayak] could not start recording:',
                err,
            )

            setMicOn(false)
            setStatus('sleeping')
            setInterimText('')

            setError(
                `Could not start microphone: ${err.message}`,
            )
        }
    }, [
        recorder,
        recorderState.isRecording,
    ])

    const toggleMic = useCallback(async () => {
        if (processingRef.current) {
            return
        }

        if (recorderState.isRecording) {
            await stopRecording()
        } else {
            await startRecording()
        }
    }, [
        recorderState.isRecording,
        startRecording,
        stopRecording,
    ])

    const sendTextCommand = useCallback(
        async (text) => {
            await sendCommand(text)
        },
        [sendCommand],
    )

    useEffect(() => {
        mountedRef.current = true

        return () => {
            mountedRef.current = false

            if (recorderState.isRecording) {
                try {
                    recorder.stop()
                } catch {
                    // Recording cleanup during unmount.
                }
            }
        }
    }, [
        recorder,
        recorderState.isRecording,
    ])

    return {
        status,
        micOn,
        micSupported,
        micLevel,
        interimText,
        error,
        toggleMic,
        sendTextCommand,
    }
}