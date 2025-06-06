from sqlalchemy.orm import Session
from app.models.plugin import Plugin
from app.schemas.plugin import PluginCreate
from app.services.plugin import PluginService
from app.tasks.plugin_tasks import inspect_plugin


def initialize_plugin_command(db: Session, plugin_data: PluginCreate) -> Plugin:
    plugin = PluginService(db).create_plugin(plugin_data)

    inspect_plugin.delay(plugin.id)

    return plugin
