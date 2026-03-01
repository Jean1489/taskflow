from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4
import enum
import uuid

from app.database import Base

# ----------------------------
# Enums
# ----------------------------

class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Status(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class Category(str, enum.Enum):
    personal = "personal"
    work = "work"
    study = "study"
    other = "other"

# ----------------------------
# SQLAlchemy Model — DB table
# ----------------------------

class TaskDB(Base):
    __tablename__ = "tasks"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title         = Column(String(100), nullable=False)
    description   = Column(String(500), nullable=True)
    priority      = Column(SQLEnum(Priority), nullable=False, default=Priority.medium)
    status        = Column(SQLEnum(Status), nullable=False, default=Status.pending)
    category      = Column(SQLEnum(Category), nullable=False, default=Category.other)
    due_date      = Column(DateTime(timezone=True), nullable=True)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# ----------------------------
# Pydantic Models — API contract
# ----------------------------

class TaskCreate(BaseModel):
    title:       str            = Field(..., min_length=1, max_length=100)
    description: Optional[str]  = Field(None, max_length=500)
    priority:    Priority       = Priority.medium
    category:    Category       = Category.other
    due_date:    Optional[datetime] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Complete project documentation",
                "description": "Write the README and API docs",
                "priority": "high",
                "category": "work",
                "due_date": "2026-03-01T10:00:00"
            }
        }
    }

class TaskUpdate(BaseModel):
    title:       Optional[str]      = Field(None, min_length=1, max_length=100)
    description: Optional[str]      = Field(None, max_length=500)
    priority:    Optional[Priority] = None
    status:      Optional[Status]   = None
    category:    Optional[Category] = None
    due_date:    Optional[datetime] = None

class TaskResponse(BaseModel):
    id:          uuid.UUID
    title:       str
    description: Optional[str]
    priority:    Priority
    status:      Status
    category:    Category
    due_date:    Optional[datetime]
    created_at:  datetime

    model_config = {"from_attributes": True}