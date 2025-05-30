from enum import Enum


class PluginState(Enum):
    REGISTERED = "registered"  # Plugin is registered but not yet started
    INITIALIZING = "initializing"  # Plugin is being initialized (cloning, setup, etc.)
    STARTING = "starting"  # Plugin is in the process of starting up
    RUNNING = "running"  # Plugin is running and ready to accept requests
    STOPPED = "stopped"  # Plugin was stopped (either manually or due to error)
    ERROR = "error"  # Plugin encountered an error during startup or runtime
    IDLE = "idle"  # Plugin is running but hasn't been used for a while
