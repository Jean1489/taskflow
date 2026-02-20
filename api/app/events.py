import redis
import json
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

logger = logging.getLogger(__name__)

# ----------------------------
# Redis connection
# ----------------------------
_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host= os.environ.get("REDIS_HOST", "localhost"),
            port= int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses = True,
            max_connections = 10
        )
        logger.info("Initialized Redis client")
    return _redis_client

def close_redis_client()-> None:
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        logger.info("Closed Redis client")
    

# ----------------------------
# Event envelope builder
# ----------------------------

def build_event(event_type: str, payload:dict) -> dict:
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "producer": "api-service",
        "payload": payload
    }


# ----------------------------
# Publishers
# ----------------------------

def publish_task_created(task: dict) -> None:
    event = build_event("task.created", task)
    _publish("tasks", event)


def publish_task_updated(task: dict) -> None:
    event = build_event("task.updated", task)
    _publish("tasks", event)


def publish_task_completed(task: dict) -> None:
    event = build_event("task.completed", task)
    _publish("tasks", event)


# ----------------------------
# Internal publisher
# ----------------------------
def _publish(channel: str, event: dict) -> None:
    try:
        client = get_redis_client()
        client.publish(channel, json.dumps(event))
        logger.info(f"Event published: {event['event_type']} - {event['event_id']}")
    except redis.exceptions.ConnectionError:
        logger.error("Could not connect to Redis - event not published")
    except Exception as e:
        logger.error(f"Unexpected error publishing event: {e}")