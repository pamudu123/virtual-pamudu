# Virtual Pamudu - System Design

## 1. Requirements

### Chat Capability
- Answer questions about Pamudu's professional background, skills, and work.
- Maintain multi-turn conversation context.
- Provide citations for sources used in answers.

### Knowledge Sources
- **Digital Brain**: Resume content (Markdown files)
- **Medium**: Blog articles (via Tool)
- **YouTube**: Video transcripts (via Tool)
- **GitHub**: Repository code and READMEs (via Tool)
- **Email**: Sending capability (via Tool)

### Actions
- Search and retrieval from all sources.
- Send emails/notifications to Pamudu.

---

## 2. System Architecture

### Backend API (FastAPI)
The system exposes a RESTful API built with `FastAPI` (`src/app.py`).

**Endpoints:**
- `POST /sessions`: Create a new chat session.
- `POST /chat`: Send a message to the agent.
- `GET /sessions/{id}`: Retrieve session history.
- `DELETE /sessions/{id}`: Delete a session.

### Persistence Layer (Firebase Firestore)
Conversations are stored in Firebase Firestore for persistence across restarts and for history retrieval.

**Data Structure:**
```json
sessions/{session_id}
{
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "messages": [
    {
      "role": "user",
      "content": "Who are you?",
      "timestamp": "..."
    },
    {
      "role": "assistant",
      "content": "I am Virtual Pamudu...",
      "timestamp": "..."
    }
  ]
}
```

### Agent Core (LangGraph)
The intelligent logic resides in `src/chat.py` using a LangGraph workflow:
1. **Planner Node**: Analyzes query + history to decide on tools.
2. **Executor Node**: Runs tools (Brain, GitHub, Medium, etc.).
3. **Synthesizer Node**: Generates the final answer with citations.

---

## 3. Directory Structure

```
virtual-pamudu/
├── digital_brain/       # Markdown knowledge base (Resume, etc.)
├── src/
│   ├── app.py           # FastAPI entry point
│   ├── chat.py          # LangGraph agent definition
│   ├── agent.py         # (Legacy) CLI agent logic
│   ├── firebase_service.py # Firestore integration
│   ├── tools/           # Tool implementations
│   │   ├── brain_tools.py
│   │   ├── github_tools.py
│   │   ├── medium_tools.py
│   │   └── youtube_tools.py
│   └── utils.py
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── firebase-service-account.json # Firebase credentials
```
