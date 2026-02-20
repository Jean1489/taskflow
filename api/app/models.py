from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


# ----------------------------
# Enums — valores permitidos
# ----------------------------


class Priority(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'

class Status(str, Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'

class Category(str, Enum):
    work = 'work'
    personal = 'personal'
    shopping = 'shopping'
    others = 'others'


# ----------------------------
# TaskCreate — input del usuario
# ----------------------------

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Priority = Field(default=Priority.medium)
    category: Category = Field(default=Category.others)
    due_date: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Comprar leche",
                "description": "Ir al supermercado y comprar leche",
                "priority": "high",
                "category": "shopping",
                "due_date": "2024-07-01T12:00:00"
            }
        }

# ----------------------------
# TaskUpdate — actualización parcial
# ----------------------------

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[Priority] = None
    category: Optional[Category] = None
    status: Optional[Status] = None
    due_date: Optional[datetime] = None


# ----------------------------
# TaskResponse — output al usuario
# ----------------------------

class TaskResponde(BaseModel):
   id: str
   title: str
   description: Optional[str]
   priority: Priority
   category: Category
   status: Status
   due_date: Optional[datetime]
   created_at: datetime

   class Config:
       from_attributes = True