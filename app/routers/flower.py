from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from flower.app import Flower
from app.core.celery_app import celery_app
from app.config import get_settings
import secrets

settings = get_settings()

# Create security scheme
security = HTTPBasic()

# Create Flower application
flower_app = Flower(
    celery_app=celery_app,
    broker_api=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    address="0.0.0.0",
    port=5555,
    basic_auth=None,  # We'll handle auth at the FastAPI level
)

# Create FastAPI router
router = APIRouter(prefix="/flower", tags=["flower"])


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify the basic auth credentials."""
    correct_username = settings.flower_username
    correct_password = settings.flower_password

    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), correct_username.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), correct_password.encode("utf8")
    )

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


# Mount the Flower application with authentication
@router.get("/")
async def flower_root(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """Root endpoint that redirects to the Flower dashboard."""
    return RedirectResponse(url="/flower/dashboard")


# Mount the Flower application at /dashboard
router.mount("/dashboard", WSGIMiddleware(flower_app))
