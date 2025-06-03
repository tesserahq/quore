from uuid import UUID
from sqlalchemy.orm import Session
from app.models.plugin import Plugin
from app.services.plugin_registry import PluginRegistryService
from app.tasks.plugin_tasks import inspect_plugin


def inspect_plugin_command(db: Session, plugin_id: str) -> Plugin:
    plugin = PluginRegistryService(db).get_plugin(UUID(plugin_id))

    inspect_plugin.delay(plugin_id)

    return plugin
