from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

class Citation(BaseModel):
    source_file: str
    paragraph_reference: Optional[str] = None
    text_excerpt: Optional[str] = None

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender: str # "user" or "bot"
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    citations: Optional[List[Citation]] = None

class UserMessage(BaseModel):
    conversation_id: str
    message: str
    selected_text: Optional[str] = None

class BotResponse(BaseModel):
    conversation_id: str
    response: str
    citations: Optional[List[Citation]] = None
