from app.tasks import celery_app
from app.core.logging_config import get_logger

logger = get_logger()


@celery_app.task(name="example_task")
def example_task(x: int, y: int) -> int:
    """Example task that adds two numbers."""
    logger.info(f"Running example task with x={x}, y={y}")
    return x + y
