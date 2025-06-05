from sqlalchemy.orm import Session
from app.models.plugin import Plugin
from app.schemas.plugin import PluginCreate
from app.services.plugin import PluginService


def initialize_plugin_command(db: Session, plugin_data: PluginCreate) -> Plugin:
    plugin = PluginService(db).create_plugin(plugin_data)

    return plugin
