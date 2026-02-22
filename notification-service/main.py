import redis
import json
import logging
import os
import time
from datetime import datetime

# ----------------------------
# Logging configuration
# ----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ----------------------------
# Redis connection
# ----------------------------

def get_redis_client() -> redis.Redis:
    return redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        decode_responses=True
    )


# ----------------------------
# Event handlers
# ----------------------------

def handle_task_created(payload: dict) -> None:
    logger.info(f"📋 New task created: '{payload.get('title')}'")
    logger.info(f"   Priority: {payload.get('priority')} | Category: {payload.get('category')}")
    logger.info(f"   Notification sent to user for task: {payload.get('id')}")


def handle_task_updated(payload: dict) -> None:
    logger.info(f"✏️  Task updated: '{payload.get('title')}'")
    logger.info(f"   New status: {payload.get('status')}")


def handle_task_completed(payload: dict) -> None:
    logger.info(f"✅ Task completed: '{payload.get('title')}'")
    logger.info(f"   Completed at: {datetime.utcnow().isoformat()}")
    logger.info(f"   Congratulations notification sent for task: {payload.get('id')}")


# ----------------------------
# Event router
# ----------------------------

def process_event(message: dict) -> None:
    try:
        event = json.loads(message["data"])
        event_type = event.get("event_type")
        payload = event.get("payload", {})

        logger.info(f"Event received: {event_type} - {event.get('event_id')}")

        handlers = {
            "task.created": handle_task_created,
            "task.updated": handle_task_updated,
            "task.completed": handle_task_completed,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(payload)
        else:
            logger.warning(f"No handler found for event type: {event_type}")

    except json.JSONDecodeError:
        logger.error("Could not decode event message")
    except Exception as e:
        logger.error(f"Error processing event: {e}")


# ----------------------------
# Main loop — subscribe to Redis
# ----------------------------

def main():
    logger.info("Starting Notification Service...")
    logger.info("Waiting for Redis to be available...")

    while True:
        try:
            client = get_redis_client()
            pubsub = client.pubsub()
            pubsub.subscribe("tasks")

            logger.info("Subscribed to 'tasks' channel — waiting for events...")

            for message in pubsub.listen():
                if message["type"] == "message":
                    process_event(message)

        except redis.exceptions.ConnectionError:
            logger.error("Redis connection lost — retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e} — retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()