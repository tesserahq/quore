from sqlalchemy.orm import Session
from app.models.plugin import Plugin
from app.schemas.plugin import PluginCreate
from app.services.plugin_service import PluginService
from app.tasks.plugin_tasks import inspect_plugin


def initialize_plugin_command(
    db: Session, plugin_data: PluginCreate, access_token: str
) -> Plugin:
    plugin = PluginService(db).create_plugin(plugin_data)

    # TODO: Make sure the access token is not being logged
    inspect_plugin.delay(plugin.id, access_token)

    return plugin
