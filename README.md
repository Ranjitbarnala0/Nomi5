# Project Nomi

**The Psychometric Simulation Engine**

Project Nomi is a sophisticated AI interaction platform that simulates distinct personas ("Nomis") with deep psychological profiles, dynamic emotional states, and long-term memory. It uses a "Director/Actor" architecture to manage relationship dynamics and narrative consistency.

## 🏗 System Architecture

### 🧠 The Brain (Backend)
-   **Framework:** FastAPI (Python)
-   **Port:** `10000`
-   **AI Provider:** OpenRouter (NVIDIA Nemotron via `cortex.py`)
-   **Database:** Supabase (PostgreSQL + pgvector)
-   **Key Services:**
    -   **Oracle:** Psychometric profiling engine (The "Liminal Space").
    -   **Foundry:** Procedural persona generation based on user Vibe.
    -   **Cortex:** Main chat loop managing the "Director" (Logic/Strategy) and "Actor" (Dialogue).
    -   **Fluid States:** Real-time tracking of Trust (Emotional Bank Account) and Boredom.

### 📱 The Body (Frontend)
-   **Framework:** React Native (Expo)
-   **State:** React Context
-   **Networking:** Axios (`src/services/api.js`)

## 🚀 Getting Started

### Prerequisites
-   Python 3.10+
-   Node.js & npm
-   Supabase Account (configured with `vector` extension)
-   OpenRouter API Key

### 1. Backend Setup
1.  Navigate to the `backend` directory.
2.  Create a `.env` file with your credentials (`OPENROUTER_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`).
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Start the server:
    ```bash
    # Runs on port 10000 by default
    python3 main.py
    ```

### 2. Frontend Setup
1.  Navigate to the `ProjectNomiApp` directory.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  **CRITICAL CONFIGURATION:**
    Open `src/core/config.js` and update `LOCAL_URL` to match your computer's local IP address:
    ```javascript
    // Example: Replace with YOUR specific LAN IP
    const LOCAL_URL = 'http://192.168.1.X:10000';
    ```
4.  Start the app:
    ```bash
    npx expo start --clear
    ```

## ⚠️ Known Issues / Status
-   **IP Configuration:** The mobile app requires your specific LAN IP in `config.js` to connect to the backend. It will not work out-of-the-box without this change.
-   **AI Provider:** The system is currently tuned for **NVIDIA Nemotron** models via OpenRouter. Using other models may require prompting adjustments in `cortex.py`.

## 📂 Project Structure
```
/
├── backend/
│   ├── app/routers/      # API Endpoints (Oracle, Foundry, Chat)
│   ├── app/services/     # Business Logic (Cortex, World Engine)
│   ├── db_schema.sql     # Database setup script
│   └── main.py           # Application Entry Point
└── ProjectNomiApp/
    ├── src/screens/      # UI Screens
    ├── src/services/     # API Integration
    └── src/core/         # Configuration
```
