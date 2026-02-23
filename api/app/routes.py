import json
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4

from app.models import TaskCreate, TaskUpdate, TaskResponde, Priority, Status, Category
from app.events import publish_task_completed, publish_task_updated, publish_task_created

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# ----------------------------
# In-memory storage
# Temporary solution — will be replaced with a database
# ----------------------------

tasks_db: dict[str, dict] = {}

# ----------------------------
# POST /tasks — Create task
# ----------------------------

@router.post("/", response_model=TaskResponde, status_code=201)
def create_task(task: TaskCreate):
    task_id = str(uuid4())
    now = datetime.now(timezone.utc)
    new_task = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": Status.pending,
        "category": task.category,
        "created_at": now,
        "due_date": task.due_date
    }
    tasks_db[task_id] = new_task
    # Serialize for Redis — convert datetime and enums to strings
    serializable_task = json.loads(
        json.dumps(new_task, default=str)
    )
    publish_task_created(serializable_task) 
    return new_task


# ----------------------------
# GET /tasks — List tasks with filters
# ----------------------------

@router.get("/", response_model=list[TaskResponde])
def list_tasks(
    status: Optional[Status] = Query(None),
    priority: Optional[Priority] = Query(None),
    category: Optional[Category] = Query(None)
):
    results = list(tasks_db.values())
    if status:
        results = [task for task in results if task["status"] == status]
    if priority:
        results = [task for task in results if task["priority"] == priority]
    if category:
        results = [task for task in results if task["category"] == category]
    
    return results

# ----------------------------
# GET /tasks/{id} — Get single task
# ----------------------------
@router.get("/{task_id}", response_model=TaskResponde)
def get_task(task_id: str):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

# ----------------------------
# PATCH /tasks/{id} — Update task
# ----------------------------
@router.patch("/{task_id}", response_model=TaskResponde)
def update_task(task_id: str, updates: TaskUpdate):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    #Only update fields that were actually sent
    update_data = updates.model_dump(exclude_unset=True)
    task.update(update_data)

    #If status changed to completed, publidh specific event
    if update_data.get("status") == Status.completed:
        publish_task_completed(task)
    else:
        publish_task_updated(task)
    
    return task


# ----------------------------
# DELETE /tasks/{id} — Delete task
# ----------------------------

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str):
    task = tasks_db.get(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    del tasks_db[task_id]
