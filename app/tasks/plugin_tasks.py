import asyncio
from uuid import UUID

from app.core.plugin_manager.manager import PluginManager
from app.constants.plugin_states import PluginState
from app.db import SessionLocal
from app.services.plugin_service import PluginService
from app.core.celery_app import celery_app


@celery_app.task
def inspect_plugin(plugin_id: str, access_token: str) -> None:
    """
    Inspect a plugin by listing its tools, prompts, and resources.
    This is an async task that runs in the background.
    """
    db = SessionLocal()
    try:
        plugin_manager = PluginManager(
            db, UUID(str(plugin_id)), access_token=access_token
        )
        plugin_service = PluginService(db)

        try:
            asyncio.run(plugin_manager.refresh())
        except Exception as e:
            plugin_service.update_state(UUID(str(plugin_id)), PluginState.ERROR)
            raise RuntimeError(f"Failed to initialize plugin: {str(e)}")
        finally:
            db.commit()
    finally:
        db.close()
