from sqlalchemy.orm import Session
from app.models.plugin import Plugin
from app.schemas.plugin import PluginCreate
from app.tasks.plugin_tasks import clone_repository
from app.services.plugin_registry import PluginRegistryService


def initialize_plugin_command(db: Session, plugin_data: PluginCreate) -> Plugin:
    plugin = PluginRegistryService(db).create_plugin(plugin_data)

    # if plugin.repository_url:
    #     clone_repository.delay(plugin.id)

    return plugin
