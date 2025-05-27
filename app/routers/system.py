from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.system_setup import SystemSetup
from app.schemas.system import SystemSetupResponse, ValidationStatus
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/system",
    tags=["system"],
    responses={404: {"description": "Not found"}},
)


@router.post("/setup", response_model=SystemSetupResponse)
def setup_system(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Perform system setup and validation.
    This endpoint runs all system-level validations and setup procedures.
    """
    validation_steps = SystemSetup.validate()
    success = all(step.status == ValidationStatus.OK for step in validation_steps)

    return SystemSetupResponse(
        success=success,
        message=(
            "System setup completed successfully" if success else "System setup failed"
        ),
        details=validation_steps,
    )
