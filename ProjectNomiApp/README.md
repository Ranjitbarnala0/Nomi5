
# Project Nomi

The Psychometric Simulation Engine (Mobile Client).

## Architecture
- **Backend:** Python (FastAPI) + Google Gemini + Supabase (Vector DB)
- **Frontend:** React Native (Expo)
- **State:** React Context + AsyncStorage

## Setup & Run

### 1. Start the Brain (Backend)
Navigate to the backend folder:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Note: `--host 0.0.0.0` is required for the mobile phone to access the server.

### 2. Configure the Body (Frontend)
Open `src/core/config.js` and update the IP:

```javascript
// If using a physical phone, set this to your computer's LAN IP (e.g., 192.168.1.50)
const LOCAL_IP = 'YOUR_IP_HERE'; 
```

### 3. Start the App
Navigate to the frontend folder:

```bash
cd ProjectNomiApp
npx expo start --clear
```

- Press `i` for iOS Simulator.
- Press `a` for Android Emulator.
- Scan QR code with Expo Go on your physical device.

## Features
- **The Oracle:** Psychometric testing engine.
- **The Foundry:** Procedural persona generation.
- **The Cortex:** Director/Actor chat system with long-term memory.
- **Time Machine:** Reset timeline functionality for "Permadeath" scenarios.

## Troubleshooting
- **Network Error?** Check if `LOCAL_IP` in `config.js` matches your computer's Wi-Fi IP. Ensure firewall allows port 8000.
- **Stuck on Loading?** Ensure Supabase credentials in Backend `.env` are correct.
