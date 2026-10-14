import * as SecureStore from 'expo-secure-store'
import { fetch as expoFetch } from 'expo/fetch'
import { File } from 'expo-file-system'

const API_BASE =
  process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://10.249.58.190:8000";

async function getToken() {
    return SecureStore.getItemAsync('auth_token')
}

async function request(path, options = {}) {
    const token = await getToken()

    const headers = new Headers(options.headers ?? {})
    headers.set('Accept', 'application/json')

    if (token) {
        headers.set('Authorization', `Bearer ${token}`)
    }

    if (
        options.body !== undefined &&
        options.body !== null &&
        !(options.body instanceof FormData) &&
        !headers.has('Content-Type')
    ) {
        headers.set('Content-Type', 'application/json')
    }

    let response

    try {
        response = await expoFetch(`${API_BASE}${path}`, {
            ...options,
            headers,
        })
    } catch (error) {
        console.error(`[api] Network request failed: ${path}`, error)

        throw new Error(
            'Could not reach the Nayak backend. Check that the backend is running and the phone is on the same network.',
        )
    }

    const data = await response.json().catch(() => null)

    if (!response.ok) {
        const message =
            data?.detail ||
            data?.error ||
            `Request failed (${response.status})`

        throw new Error(message)
    }

    return data
}

async function uploadAudio(uri) {
    const token = await getToken()

    if (!uri) {
        throw new Error('No audio file URI was provided')
    }

    console.log('[api] Uploading audio to /api/transcribe...')
    console.log('[api] Audio URI:', uri)

    try {
        /*
         * Expo SDK 56:
         *
         * The FormData implementation used by expo/fetch expects
         * an actual expo-file-system File object rather than the
         * React-Native { uri, name, type } FormData object.
         */
        const file = new File(uri)

        console.log('[api] Audio file:', {
            uri: file.uri,
            name: file.name,
            type: file.type,
            exists: file.exists,
            size: file.size,
        })

        if (!file.exists) {
            throw new Error(
                'The recorded audio file does not exist anymore.',
            )
        }

        const formData = new FormData()

        /*
         * This name MUST remain "audio".
         * The FastAPI endpoint expects UploadFile = audio.
         */
        formData.append('audio', file)

        const headers = {
            Accept: 'application/json',
        }

        if (token) {
            headers.Authorization = `Bearer ${token}`
        }

        const response = await expoFetch(
            `${API_BASE}/api/transcribe`,
            {
                method: 'POST',
                headers,
                body: formData,
            },
        )

        const data = await response.json().catch(() => null)

        if (!response.ok) {
            const message =
                data?.detail ||
                data?.error ||
                `Audio upload failed (${response.status})`

            console.error(
                '[api] Transcription request failed:',
                response.status,
                message,
            )

            throw new Error(message)
        }

        console.log(
            '[api] Transcription response:',
            data,
        )

        return data
    } catch (error) {
        console.error(
            '[api] Audio upload failed:',
            error,
        )

        throw error instanceof Error
            ? error
            : new Error(String(error))
    }
}

export const api = {
    login: (body) =>
        request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(body),
        }),

    register: (body) =>
        request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(body),
        }),

    guestLogin: () =>
        request('/api/auth/guest-login', {
            method: 'POST',
        }),

    verifyToken: (token) =>
        request('/api/auth/verify', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }),

    createSession: () =>
        request('/api/session', {
            method: 'POST',
        }),

    newChat: () =>
        request('/api/new-chat', {
            method: 'POST',
        }),

    history: (sessionId) =>
        request(
            `/api/history?session_id=${encodeURIComponent(sessionId)}`,
        ),

    command: (body) =>
        request('/api/command', {
            method: 'POST',
            body: JSON.stringify(body),
        }),

    transcribeAudio: uploadAudio,
}