# Virtual Pamudu - AI Personal Assistant

**Virtual Pamudu** is a sophisticated AI agent designed to represent [Pamudu Ranasinghe](https://github.com/pamudu123). Built with **FastAPI** and **LangGraph**, it serves as an interactive interface to Pamudu's "Digital Brain," capable of answering questions about his background, projects, research, and content.

## 🧠 Key Features

*   **Context-Aware Chat:** Maintains conversation history for natural, multi-turn dialogue.
*   **Digital Brain:** Accesses structured personal data (Resume, Bio, Skills).
*   **Tool Integration:**
    *   **Medium:** Fetches and reads Pamudu's latest articles.
    *   **YouTube:** searches and retrieves transcripts from video content.
    *   **GitHub:** Explores repositories and reads code.
    *   **Email:** Can draft and send emails on behalf of the user (approvals required).
*   **Persistent Memory:** Uses Firebase Firestore to save chat sessions.

---

## 🚀 API Usage

The application exposes a RESTful API powered by FastAPI.

### Base URL
*   **Local:** `http://localhost:8000`
*   **Production:** `https://your-vercel-app.vercel.app`

### 1. Check Health
Ensure the API is running.
```bash
GET /health
```

### 2. Create a Session
Start a new conversation to get a `session_id`.
```bash
POST /sessions
```
**Response:**
```json
{
  "session_id": "unique-session-id",
  "created_at": "..."
}
```

### 3. Chat with Agent
Send a message to the agent.
```bash
POST /chat
Content-Type: application/json

{
  "session_id": "unique-session-id",
  "message": "Tell me about your latest research paper."
}
```

### 4. Chat with Streaming (Real-time)
Receive real-time updates ("Thinking...", "Searching...") via Server-Sent Events (SSE).
```bash
POST /chat/stream
Content-Type: application/json

{
  "session_id": "unique-session-id",
  "message": "Search GitHub for my projects"
}
```
**Response Stream:**
```json
data: {"type": "status", "node": "planner", "message": "🔎 Using tools: GitHub..."}

data: {"type": "result", "answer": "...", "citations": [...]}
```

---

## 🛠️ Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/pamudu123/virtual-pamudu.git
    cd virtual-pamudu
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Create a `.env` file with the following keys:
    ```env
    OPENROUTER_API_KEY=sk-...
    FIREBASE_CREDENTIALS_PATH=./virtual-assistant-firebase-adminsdk-1.json
    GITHUB_TOKEN=ghp_...
    ```

4.  **Run the Server:**
    ```bash
    python src/app.py
    ```

---

## ☁️ Deployment (Vercel)

This project is configured for serverless deployment on **Vercel**.

1.  **Install Vercel CLI:** `npm i -g vercel`
2.  **Deploy:** `vercel`
3.  **Environment Variables:** Add the following in your Vercel Project Settings:
    *   `OPENROUTER_API_KEY`
    *   `GITHUB_TOKEN`
    *   `FIREBASE_CREDENTIALS_JSON` (Paste the content of your Firebase JSON file here)

---

## 📂 Project Structure

*   `src/app.py`: FastAPI entry point and API routes.
*   `src/chat.py`: LangGraph agent logic (Planner, Executor, Synthesizer nodes).
*   `src/tools/`: Tool implementations (Brain, GitHub, Medium, YouTube, Email).
*   `digital_brain/`: Static markdown and YAML files representing the knowledge base.
