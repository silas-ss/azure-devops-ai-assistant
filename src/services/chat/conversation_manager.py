from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

from src.services.chat.prompt_engineer import ChatContext
from src.utils.logger import logger

@dataclass
class Message:
    """Represents a single message in the conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationSession:
    """Represents a conversation session"""
    session_id: str
    user_id: str
    organization: str
    project: str
    created_at: datetime
    messages: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, storage_dir: str = "conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.max_history_length = 50  # Maximum messages per session
        self.max_context_length = 4000  # Maximum context length for LLM
    
    def create_session(self, user_id: str, organization: str, project: str) -> str:
        """Create a new conversation session"""
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            organization=organization,
            project=project,
            created_at=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Created conversation session: {session_id}")
        
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> bool:
        """Add a message to a conversation session"""
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return False
        
        session = self.active_sessions[session_id]
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        
        # Trim history if too long
        if len(session.messages) > self.max_history_length:
            # Keep system messages and recent messages
            system_messages = [msg for msg in session.messages if msg.role == 'system']
            recent_messages = session.messages[-self.max_history_length//2:]
            session.messages = system_messages + recent_messages
        
        logger.debug(f"Added {role} message to session {session_id}")
        return True
    
    def add_user_message(self, session_id: str, content: str, metadata: Dict = None) -> bool:
        """Add a user message to a conversation session"""
        return self.add_message(session_id, 'user', content, metadata)

    def add_assistant_message(self, session_id: str, content: str, metadata: Dict = None) -> bool:
        """Add an assistant message to a conversation session"""
        return self.add_message(session_id, 'assistant', content, metadata)
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get a conversation session"""
        return self.active_sessions.get(session_id)
    
    def get_chat_context(self, session_id: str) -> Optional[ChatContext]:
        """Get chat context for a session"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Convert messages to format expected by ChatContext
        conversation_history = []
        for message in session.messages:
            conversation_history.append({
                'role': message.role,
                'content': message.content
            })
        
        # Get last command and response
        last_command = None
        last_response = None
        
        for message in reversed(session.messages):
            if message.role == 'user' and not last_command:
                last_command = message.content
            elif message.role == 'assistant' and not last_response:
                last_response = message.content
            
            if last_command and last_response:
                break
        
        return ChatContext(
            conversation_history=conversation_history,
            current_user=session.user_id,
            organization=session.organization,
            project=session.project,
            last_command=last_command,
            last_response=last_response
        )
    
    def get_conversation_for_llm(self, session_id: str, max_length: int = None) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Convert messages to LLM format
        llm_messages = []
        total_length = 0
        max_length = max_length or self.max_context_length
        
        # Start with system messages
        for message in session.messages:
            if message.role == 'system':
                llm_messages.append({
                    'role': 'system',
                    'content': message.content
                })
                total_length += len(message.content)
        
        # Add recent messages (most recent first, then reverse)
        recent_messages = [msg for msg in session.messages if msg.role != 'system']
        for message in reversed(recent_messages[-10:]):  # Last 10 messages
            content_length = len(message.content)
            if total_length + content_length > max_length:
                break
            
            llm_messages.append({
                'role': message.role,
                'content': message.content
            })
            total_length += content_length
        
        # Reverse to get chronological order
        return list(reversed(llm_messages))
    
    def update_context(self, session_id: str, key: str, value: Any) -> bool:
        """Update session context"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.context[key] = value
        logger.debug(f"Updated context for session {session_id}: {key} = {value}")
        return True
    
    def get_context(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get value from session context"""
        session = self.get_session(session_id)
        if not session:
            return default
        
        return session.context.get(key, default)
    
    def end_session(self, session_id: str) -> bool:
        """End a conversation session"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.is_active = False
        
        # Save session to file
        self._save_session(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Ended conversation session: {session_id}")
        return True
    
    def _save_session(self, session: ConversationSession):
        """Save session to file"""
        try:
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'organization': session.organization,
                'project': session.project,
                'created_at': session.created_at.isoformat(),
                'is_active': session.is_active,
                'context': session.context,
                'messages': [
                    {
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat(),
                        'metadata': msg.metadata
                    }
                    for msg in session.messages
                ]
            }
            
            file_path = self.storage_dir / f"{session.session_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved session to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")
    
    def load_session(self, session_id: str) -> Optional[ConversationSession]:
        """Load session from file"""
        try:
            file_path = self.storage_dir / f"{session_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Convert messages back to Message objects
            messages = []
            for msg_data in session_data['messages']:
                message = Message(
                    role=msg_data['role'],
                    content=msg_data['content'],
                    timestamp=datetime.fromisoformat(msg_data['timestamp']),
                    metadata=msg_data.get('metadata', {})
                )
                messages.append(message)
            
            session = ConversationSession(
                session_id=session_data['session_id'],
                user_id=session_data['user_id'],
                organization=session_data['organization'],
                project=session_data['project'],
                created_at=datetime.fromisoformat(session_data['created_at']),
                messages=messages,
                context=session_data.get('context', {}),
                is_active=session_data.get('is_active', False)
            )
            
            logger.info(f"Loaded session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_sessions.keys())
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old inactive sessions"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    created_at = datetime.fromisoformat(session_data['created_at']).timestamp()
                    
                    if created_at < cutoff_time and not session_data.get('is_active', False):
                        file_path.unlink()
                        logger.debug(f"Cleaned up old session: {file_path.name}")
                        
                except Exception as e:
                    logger.error(f"Failed to process session file {file_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        user_messages = len([msg for msg in session.messages if msg.role == 'user'])
        assistant_messages = len([msg for msg in session.messages if msg.role == 'assistant'])
        system_messages = len([msg for msg in session.messages if msg.role == 'system'])
        
        total_chars = sum(len(msg.content) for msg in session.messages)
        
        return {
            'session_id': session_id,
            'user_id': session.user_id,
            'organization': session.organization,
            'project': session.project,
            'created_at': session.created_at.isoformat(),
            'is_active': session.is_active,
            'total_messages': len(session.messages),
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'system_messages': system_messages,
            'total_characters': total_chars,
            'context_keys': list(session.context.keys())
        } 