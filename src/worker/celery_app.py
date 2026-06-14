import asyncio
import httpx
from typing import Any, Dict
from celery import Celery
from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.repositories.user import UserRepository

# Initialize the Celery client and route messages to our Redis instance
celery_worker = Celery(
    "enterprise_tasks", 
    broker=settings.CELERY_BROKER_URL, 
    backend=settings.CELERY_BROKER_URL
)

# Apply enterprise task serialization rules
celery_worker.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

async def _poll_external_api_logic() -> Dict[str, Any]:
    """
    Asynchronous internal pipeline executing network I/O and database persistence.
    This runs safely out-of-process from the main FastAPI server execution shell.
    """
    # 1. Simulate pulling telemetry updates from an external corporate API
    async with httpx.AsyncClient() as client:
        # mock_response = await client.get("https://api.external_metrics.com/v1/telemetry")
        # telemetry_data = mock_response.json()
        pass

    # 2. Persist metrics or update database records out-of-process using our decoupled Repository layer
    async with AsyncSessionLocal() as db_session:
        user_repo = UserRepository(db_session)
        # For demonstration: Find a system administrator to flag background run logs
        admin_user = await user_repo.get_by_email("admin@enterprise.com")
        if admin_user:
            # Modify or add operational database state safely here
            await db_session.flush()
        
        await db_session.commit()
    
    return {"status": "success", "processed": True}


@celery_worker.task(name="tasks.poll_and_sync_observer")
def poll_and_sync_observer() -> str:
    """
    Synchronous Celery task wrapper. Bridges the Celery worker engine threads 
    to our asynchronous database configuration cleanly.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Create a clean, separate event loop if one is not bound to the current execution thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # Schedule the coroutine safely from a running thread context
        future = asyncio.run_coroutine_threadsafe(_poll_external_api_logic(), loop)
        result = future.result()
    else:
        # Run the asynchronous loop to completion
        result = loop.run_until_complete(_poll_external_api_logic())

    return f"Observer sync execution tracking code finalized: {result['status']}"