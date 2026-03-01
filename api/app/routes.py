from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
import json

from app.models import TaskDB, TaskCreate, TaskUpdate, TaskResponse, Priority, Status, Category
from app.events import publish_task_created, publish_task_updated, publish_task_completed
from app.database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ----------------------------
# POST /tasks — Create task
# ----------------------------

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = TaskDB(
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        status=Status.pending,
        due_date=task.due_date
    )

    db.add(new_task)
    await db.flush()  # Gets the generated ID without committing

    serializable_task = json.loads(
        json.dumps({
            "id": str(new_task.id),
            "title": new_task.title,
            "priority": new_task.priority.value,
            "category": new_task.category.value,
            "status": new_task.status.value,
        })
    )
    publish_task_created(serializable_task)

    return new_task


# ----------------------------
# GET /tasks — List tasks with filters
# ----------------------------

@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    status:   Optional[Status]   = Query(None),
    priority: Optional[Priority] = Query(None),
    category: Optional[Category] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(TaskDB)

    if status:
        query = query.where(TaskDB.status == status)
    if priority:
        query = query.where(TaskDB.priority == priority)
    if category:
        query = query.where(TaskDB.category == category)

    result = await db.execute(query)
    return result.scalars().all()


# ----------------------------
# GET /tasks/{id} — Get single task
# ----------------------------

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return task


# ----------------------------
# PATCH /tasks/{id} — Update task
# ----------------------------

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: UUID, updates: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    if update_data.get("status") == Status.completed:
        publish_task_completed({"id": str(task.id), "title": task.title})
    else:
        publish_task_updated({"id": str(task.id), "title": task.title})

    return task


# ----------------------------
# DELETE /tasks/{id} — Delete task
# ----------------------------

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    await db.delete(task)