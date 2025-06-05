from uuid import UUID
from app.core.plugin_manager.manager import PluginManager
from app.constants.plugin_states import PluginState
from app.db import SessionLocal
from app.services.plugin import PluginService
from app.tasks import celery_app


@celery_app.task
def inspect_plugin(plugin_id: str) -> None:
    """
    Inspect a plugin by listing its tools, prompts, and resources.
    This is an async task that runs in the background.
    """
    db = SessionLocal()
    try:
        plugin_manager = PluginManager(db, UUID(str(plugin_id)))
        plugin_service = PluginService(db)

        try:
            plugin_manager.inspect()
            plugin_service.update_state(UUID(str(plugin_id)), PluginState.RUNNING)
        except Exception as e:
            plugin_service.update_state(UUID(str(plugin_id)), PluginState.ERROR)
            raise RuntimeError(f"Failed to initialize plugin: {str(e)}")
        finally:
            db.commit()
    finally:
        db.close()
