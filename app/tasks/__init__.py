from app.core.celery_app import celery_app
from app.tasks.ingest_tasks import ingest_project_text
from app.tasks.plugin_tasks import inspect_plugin

__all__ = ["celery_app", "inspect_plugin", "ingest_project_text"]
