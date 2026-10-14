# Nayak Native — Startup Guide

This guide explains how to start the FastAPI backend and the Expo React Native frontend, and how to configure the backend IP address for testing on a physical Android phone.

## 1. Prerequisites

Install or have available:

- Node.js and npm
- Expo-compatible Android phone with Expo Go for SDK 56, or an Android emulator
- Python and `uv` for the backend
- The Nayak backend project and `nayak-native` project

Keep the phone and development computer on the **same Wi-Fi network** when testing on a physical phone.

## 2. Configure the backend IP in the mobile app

Open this file in the **`nayak-native` project**:

```text
nayak-native/src/lib/api.js
```

Find the `API_BASE` constant. Set it to your development computer's current LAN IP address and port `8000`.

Example:

```js
const API_BASE = "http://192.168.1.10:8000";
```

Use your own current IP; `192.168.1.10` is only an example from previous testing. Do not use `localhost` or `127.0.0.1` when the app runs on a physical phone, because those addresses refer to the phone itself.

### Find your computer's LAN IP (Linux)

Run this in a terminal on the computer:

```bash
hostname -I
```

Choose the IPv4 address for the same network as your phone. If multiple addresses appear, verify which one belongs to the active Wi-Fi/LAN connection.

Update `API_BASE` whenever your computer's IP changes, then save the file.

## 3. Start the backend

Open a terminal in the **backend project directory** (the directory containing the `app/` package), then run:

```bash
uv run uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

Leave this terminal running. Binding to `0.0.0.0` allows devices on your local network to reach the backend.

Check the backend from the development computer:

- API base: `http://localhost:8000`
- Swagger API docs: `http://localhost:8000/docs`

From the phone, open the matching LAN URL in a browser, replacing the example IP with your computer's current IP:

```text
http://192.168.1.10:8000/docs
```

If the docs load on the phone, the phone can reach the backend over the LAN. If they do not load, check that both devices are on the same network and that the computer firewall allows incoming connections on port `8000`.

## 4. Start the Expo frontend

Open a **second terminal** in the `nayak-native` directory:

```bash
cd /path/to/nayak-native
npm install
npx expo start
```

Replace `/path/to/nayak-native` with the actual path to your project. `npm install` is normally needed only after a fresh checkout or dependency changes.

Then:

- Open Expo Go on the Android phone and scan the QR code shown by Expo.
- Keep the Expo terminal running while using the app.
- If the phone cannot connect to Metro over the local network, try:

```bash
npx expo start --tunnel
```

The tunnel option helps the phone reach the Expo development server; it does **not** replace the LAN IP configuration required for the phone to call your backend.

## 5. Recommended startup order

1. Connect the computer and phone to the same Wi-Fi network.
2. Find the computer's current IP using `hostname -I`.
3. Update `API_BASE` in `nayak-native/src/lib/api.js`.
4. Start the backend and leave it running.
5. Confirm the backend docs are reachable at `http://<COMPUTER_LAN_IP>:8000/docs`.
6. Start Expo from the `nayak-native` directory.
7. Open the app in Expo Go and test guest authentication, session creation, and chat.

## 6. Quick troubleshooting

### The app says network request failed

- Confirm the backend terminal is still running.
- Check that `API_BASE` uses the computer's current LAN IP and port `8000`.
- Do not use `localhost` for a physical phone.
- Confirm the phone and computer are on the same Wi-Fi network.
- Open `http://<COMPUTER_LAN_IP>:8000/docs` in the phone's browser.
- Check the computer firewall for port `8000`.

### The computer's IP changed

Run:

```bash
hostname -I
```

Update the `API_BASE` value in `nayak-native/src/lib/api.js`, then reload/restart the Expo app if the change is not picked up.

### Expo cannot connect to the phone

Try restarting Expo with cache cleared:

```bash
npx expo start --clear
```

If LAN discovery is the issue, try:

```bash
npx expo start --tunnel
```

### Check whether the backend receives requests

Watch the backend terminal while opening the app, sending a message, or tapping New Chat. Requests should appear in the server logs. You can also inspect the available endpoints in Swagger at `/docs`.

## 7. Important notes

- The mobile frontend and backend are separate projects and run in separate terminals.
- Use the backend's actual project directory when starting Uvicorn; do not run the command from `nayak-native`.
- The frontend is the **Expo React Native app**, not the old Vite web frontend.
- Keep Expo SDK 56 for the current Expo Go SDK 56 setup; do not upgrade the project to SDK 57 as part of normal startup.
- `API_BASE` is a development setting. For production, use a stable HTTPS backend URL rather than a private LAN IP.

