from sqlalchemy.orm import Session
from app.models.plugin import Plugin
from app.schemas.plugin import PluginCreate
from app.services.plugin_registry import PluginRegistryService


def initialize_plugin_command(db: Session, plugin_data: PluginCreate) -> Plugin:
    plugin = PluginRegistryService(db).create_plugin(plugin_data)

    return plugin
