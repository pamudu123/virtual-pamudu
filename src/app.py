"""
Virtual Pamudu Chat API - FastAPI Implementation
RESTful API for the chat agent with Firebase Firestore persistence.
"""

# MUST be at the very top - suppress SyntaxWarnings from newspaper3k library
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="newspaper")

import os
import sys
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

import json
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logging

# Initialize logging early
setup_logging()
logger = structlog.get_logger()

load_dotenv()

# Import chat components (lazy to avoid import errors)
from chat import ChatSession, app as langgraph_app
from firebase_service import get_firebase_service, FirebaseService


# --- REQUEST/RESPONSE MODELS ---

class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    session_id: str = Field(..., description="The session ID")
    message: str = Field(..., description="User message")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    session_id: str
    answer: str
    citations: list[dict] = []
    turn_count: int


class SessionResponse(BaseModel):
    """Session info response."""
    session_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    message_count: int = 0
    messages: list[dict] = []


class CreateSessionResponse(BaseModel):
    """Response when creating a new session."""
    session_id: str
    created_at: str


class MessageModel(BaseModel):
    """A single message in conversation history."""
    role: str
    content: str
    timestamp: Optional[str] = None


# --- FIREBASE SESSION-BACKED CHAT SESSION ---

class FirebaseChatSession:
    """
    Chat session that persists to Firebase.
    Wraps the LangGraph chat workflow with Firebase storage.
    """
    
    def __init__(self, session_id: str, firebase: FirebaseService):
        self.session_id = session_id
        self.firebase = firebase
        self.log = logger.bind(session_id=session_id)
    
    def chat(self, user_message: str) -> dict:
        """
        Process a chat message and persist to Firebase.
        
        Returns:
            Dict with 'answer', 'citations', 'turn_count'
        """
        self.log.info("processing_message", message_length=len(user_message))
        
        # Load conversation history from Firebase
        messages = self.firebase.get_messages(self.session_id)
        conversation_history = [
            {"role": m["role"], "content": m["content"]} 
            for m in messages
        ]
        
        # Run the LangGraph agent
        inputs = {
            "query": user_message,
            "conversation_history": conversation_history,
            "results": [],
            "citations": []
        }
        result = langgraph_app.invoke(inputs)
        
        answer = result.get('final_answer', 'No response generated.')
        citations = result.get('citations', [])
        
        # Save the turn to Firebase
        self.firebase.add_turn(self.session_id, user_message, answer)
        
        # Get updated turn count
        updated_messages = self.firebase.get_messages(self.session_id)
        turn_count = len(updated_messages) // 2
        
        self.log.info("message_processed", turn_count=turn_count)
        
        return {
            "turn_count": turn_count
        }

    def chat_stream(self, user_message: str):
        """
        Process a chat message via streaming and persist to Firebase at the end.
        Yields events: status, result
        """
        self.log.info("processing_message_stream")
        
        # Load conversation history from Firebase
        messages = self.firebase.get_messages(self.session_id)
        conversation_history = [
            {"role": m["role"], "content": m["content"]} 
            for m in messages
        ]
        
        # Create a temporary ChatSession (in-memory) with the history loaded
        # We use the raw ChatSession logic but inject history
        temp_session = ChatSession()
        temp_session.conversation_history = conversation_history
        
        # Stream events
        final_answer = ""
        citations = []
        
        for event in temp_session.chat_stream(user_message):
            yield event
            
            if event["type"] == "result":
                final_answer = event["answer"]
                citations = event["citations"]
        
        # Save the turn to Firebase (only after stream completes)
        if final_answer:
            self.firebase.add_turn(self.session_id, user_message, final_answer)
            self.log.info("message_processed_stream_saved")


# --- APP LIFESPAN ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - initialize Firebase on startup."""
    logger.info("startup", service="virtual_pamudu_api")
    try:
        firebase = get_firebase_service()
        logger.info("firebase_connected")
    except Exception as e:
        logger.error("firebase_init_failed", error=str(e))
        logger.warning("firebase_unavailable_warning")
    yield
    logger.info("shutdown")


# --- FASTAPI APP ---

app = FastAPI(
    title="Virtual Pamudu Chat API",
    description="RESTful API for Pamudu's personal AI assistant with persistent conversations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HEALTH CHECK ---

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Virtual Pamudu Chat API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    try:
        firebase = get_firebase_service()
        firebase_status = "connected"
    except Exception as e:
        firebase_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "firebase": firebase_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# --- SESSION ENDPOINTS ---

@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session():
    """Create a new chat session."""
    try:
        firebase = get_firebase_service()
        session_id = firebase.create_session()
        logger.info("session_created", session_id=session_id)
        
        return CreateSessionResponse(
            session_id=session_id,
            created_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error("session_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details and message history."""
    try:
        firebase = get_firebase_service()
        session = firebase.get_session(session_id)
        
        if not session:
            logger.warning("session_not_found", session_id=session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = session.get("messages", [])
        
        return SessionResponse(
            session_id=session_id,
            created_at=session.get("created_at").isoformat() if session.get("created_at") else None,
            updated_at=session.get("updated_at").isoformat() if session.get("updated_at") else None,
            message_count=len(messages),
            messages=messages
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_session_failed", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages."""
    try:
        firebase = get_firebase_service()
        deleted = firebase.delete_session(session_id)
        
        if not deleted:
            logger.warning("delete_session_not_found", session_id=session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info("session_deleted", session_id=session_id)
        return {"message": "Session deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_session_failed", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@app.delete("/sessions/{session_id}/history")
async def clear_session_history(session_id: str):
    """Clear message history for a session (keep session)."""
    try:
        firebase = get_firebase_service()
        cleared = firebase.clear_messages(session_id)
        
        if not cleared:
            logger.warning("clear_history_session_not_found", session_id=session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info("history_cleared", session_id=session_id)
        return {"message": "History cleared", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("clear_history_failed", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")


# --- CHAT ENDPOINT ---

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the chat agent.
    
    Requires an existing session_id. Create one first with POST /sessions.
    """
    try:
        firebase = get_firebase_service()
        
        # Verify session exists
        session = firebase.get_session(request.session_id)
        if not session:
            logger.warning("chat_session_not_found", session_id=request.session_id)
            raise HTTPException(status_code=404, detail="Session not found. Create one with POST /sessions")
        
        # Create Firebase-backed chat session and process message
        chat_session = FirebaseChatSession(request.session_id, firebase)
        result = chat_session.chat(request.message)
        
        return ChatResponse(
            session_id=request.session_id,
            answer=result["answer"],
            citations=result["citations"],
            turn_count=result["turn_count"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("chat_failed", session_id=request.session_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
    
    
@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Send a message and get a streaming response (Server-Sent Events).
    Events:
    - data: {"type": "status", "node": "...", "message": "..."}
    - data: {"type": "result", "answer": "...", "citations": [...]}
    """
    try:
        firebase = get_firebase_service()
        
        # Verify session exists
        session = firebase.get_session(request.session_id)
        if not session:
            logger.warning("chat_session_not_found", session_id=request.session_id)
            raise HTTPException(status_code=404, detail="Session not found.")
        
        async def event_generator():
            try:
                chat_session = FirebaseChatSession(request.session_id, firebase)
                for event in chat_session.chat_stream(request.message):
                    # Format as SSE
                    yield f"data: {json.dumps(event)}\n\n"
            except Exception as e:
                logger.error("stream_error", error=str(e))
                err_event = {"type": "error", "message": f"Stream failed: {str(e)}"}
                yield f"data: {json.dumps(err_event)}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("chat_stream_failed", session_id=request.session_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


# --- MAIN ---
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info("starting_server", host=host, port=port)
    
    uvicorn.run(app, host=host, port=port)
