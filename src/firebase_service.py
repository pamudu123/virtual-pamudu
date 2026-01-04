"""
Firebase Service - Firestore integration for conversation persistence.
Handles session and message storage for the Virtual Pamudu chat.
"""

import os
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()


class FirebaseService:
    """
    Firebase Firestore service for managing chat sessions and conversations.
    
    Deployment options for credentials:
    1. Local dev: Set FIREBASE_CREDENTIALS_PATH to JSON file path
    2. Production: Set FIREBASE_CREDENTIALS_JSON with the JSON content directly
       (base64 encode if needed for your deployment platform)
    """
    
    _instance = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern to ensure single Firebase initialization."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase Admin SDK."""
        if firebase_admin._apps:
            # Already initialized
            self._db = firestore.client()
            return
        
        # Try credentials from JSON content (for deployment)
        creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if creds_json:
            try:
                cred_dict = json.loads(creds_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                print("✅ Firebase initialized from FIREBASE_CREDENTIALS_JSON")
                return
            except Exception as e:
                print(f"⚠️ Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
        
        # Try credentials from file path (for local dev)
        creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if creds_path and os.path.exists(creds_path):
            try:
                cred = credentials.Certificate(creds_path)
                firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                print(f"✅ Firebase initialized from {creds_path}")
                return
            except Exception as e:
                print(f"⚠️ Failed to load credentials from {creds_path}: {e}")
        
        raise ValueError(
            "Firebase credentials not found. Set either:\n"
            "  - FIREBASE_CREDENTIALS_PATH (path to JSON file) for local dev\n"
            "  - FIREBASE_CREDENTIALS_JSON (JSON content string) for deployment"
        )
    
    @property
    def db(self):
        """Get Firestore client."""
        return self._db
    
    # --- SESSION OPERATIONS ---
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new chat session.
        
        Args:
            session_id: Optional custom session ID. Auto-generated if not provided.
            
        Returns:
            The session ID.
        """
        sessions_ref = self.db.collection("sessions")
        
        session_data = {
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        }
        
        if session_id:
            sessions_ref.document(session_id).set(session_data)
            return session_id
        else:
            doc_ref = sessions_ref.add(session_data)
            return doc_ref[1].id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get a session by ID.
        
        Returns:
            Session data dict or None if not found.
        """
        doc = self.db.collection("sessions").document(session_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["session_id"] = session_id
            return data
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session entirely.
        
        Returns:
            True if deleted, False if not found.
        """
        doc_ref = self.db.collection("sessions").document(session_id)
        if doc_ref.get().exists:
            doc_ref.delete()
            return True
        return False
    
    # --- MESSAGE OPERATIONS ---
    
    def get_messages(self, session_id: str) -> list[dict]:
        """
        Get all messages for a session.
        
        Returns:
            List of message dicts: [{"role": "user/assistant", "content": "..."}]
        """
        session = self.get_session(session_id)
        if session:
            return session.get("messages", [])
        return []
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Add a message to a session.
        
        Args:
            session_id: The session ID.
            role: "user" or "assistant"
            content: The message content.
            
        Returns:
            True if successful, False if session not found.
        """
        doc_ref = self.db.collection("sessions").document(session_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        doc_ref.update({
            "messages": firestore.ArrayUnion([message]),
            "updated_at": datetime.utcnow()
        })
        return True
    
    def add_turn(self, session_id: str, user_message: str, assistant_message: str) -> bool:
        """
        Add a complete turn (user + assistant) to a session.
        
        Returns:
            True if successful.
        """
        doc_ref = self.db.collection("sessions").document(session_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        now = datetime.utcnow().isoformat()
        messages = [
            {"role": "user", "content": user_message, "timestamp": now},
            {"role": "assistant", "content": assistant_message, "timestamp": now}
        ]
        
        doc_ref.update({
            "messages": firestore.ArrayUnion(messages),
            "updated_at": datetime.utcnow()
        })
        return True
    
    def clear_messages(self, session_id: str) -> bool:
        """
        Clear all messages from a session (keep session).
        
        Returns:
            True if successful, False if session not found.
        """
        doc_ref = self.db.collection("sessions").document(session_id)
        if doc_ref.get().exists:
            doc_ref.update({
                "messages": [],
                "updated_at": datetime.utcnow()
            })
            return True
        return False


# Singleton instance
def get_firebase_service() -> FirebaseService:
    """Get the Firebase service singleton."""
    return FirebaseService()
