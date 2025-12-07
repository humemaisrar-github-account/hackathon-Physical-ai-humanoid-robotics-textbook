from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    embedding: Optional[List[float]] = None # Will be set after embedding generation
    source_file: str
    source_paragraph_id: Optional[str] = None
    metadata: Optional[dict] = None # Additional metadata like title, section, page number (if applicable).
