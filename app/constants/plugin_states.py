from enum import Enum
from typing import Dict


class PluginState(Enum):
    REGISTERED = "registered"  # Plugin is registered but not yet started
    INITIALIZING = "initializing"  # Plugin is being initialized (cloning, setup, etc.)
    STARTING = "starting"  # Plugin is in the process of starting up
    RUNNING = "running"  # Plugin is running and ready to accept requests
    STOPPED = "stopped"  # Plugin was stopped (either manually or due to error)
    ERROR = "error"  # Plugin encountered an error during startup or runtime
    IDLE = "idle"  # Plugin is running but hasn't been used for a while


# Dictionary mapping state values to their descriptions
PLUGIN_STATE_DESCRIPTIONS: Dict[str, str] = {
    PluginState.REGISTERED.value: "Plugin is registered but not yet started",
    PluginState.INITIALIZING.value: "Plugin is being initialized (cloning, setup, etc.)",
    PluginState.STARTING.value: "Plugin is in the process of starting up",
    PluginState.RUNNING.value: "Plugin is running and ready to accept requests",
    PluginState.STOPPED.value: "Plugin was stopped (either manually or due to error)",
    PluginState.ERROR.value: "Plugin encountered an error during startup or runtime",
    PluginState.IDLE.value: "Plugin is running but hasn't been used for a while",
}
