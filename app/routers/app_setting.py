from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.db import get_db
from app.schemas.app_setting import AppSetting, AppSettingCreate, AppSettingUpdate
from app.services.app_setting_service import AppSettingService
from app.schemas.common import ListResponse

router = APIRouter(
    prefix="/app-settings",
    tags=["app-settings"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=AppSetting, status_code=status.HTTP_201_CREATED)
def create_app_setting(app_setting: AppSettingCreate, db: Session = Depends(get_db)):
    """Create a new app setting."""
    app_setting_service = AppSettingService(db)

    # Check if key already exists
    if app_setting_service.get_app_setting_by_key(app_setting.key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="App setting with this key already exists",
        )

    return app_setting_service.create_app_setting(app_setting)


@router.get("", response_model=ListResponse[AppSetting])
def list_app_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all app settings."""
    app_settings = AppSettingService(db).get_app_settings(skip=skip, limit=limit)
    return ListResponse(data=app_settings)


@router.get("/{id_or_key}", response_model=AppSetting)
def get_app_setting(id_or_key: str, db: Session = Depends(get_db)):
    """Get an app setting by ID (UUID) or key."""
    app_setting_service = AppSettingService(db)

    # Try to parse as UUID first
    try:
        app_setting_id = UUID(id_or_key)
        app_setting = app_setting_service.get_app_setting(app_setting_id)
    except ValueError:
        # If not a valid UUID, treat as key
        app_setting = app_setting_service.get_app_setting_by_key(id_or_key)

    if not app_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="App setting not found"
        )
    return app_setting


@router.put("/{app_setting_id}", response_model=AppSetting)
def update_app_setting(
    app_setting_id: UUID, app_setting: AppSettingUpdate, db: Session = Depends(get_db)
):
    """Update an app setting."""
    app_setting_service = AppSettingService(db)

    # Check if key is being updated and already exists
    if app_setting.key:
        existing_app_setting = app_setting_service.get_app_setting_by_key(
            app_setting.key
        )
        if existing_app_setting and existing_app_setting.id != app_setting_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="App setting with this key already exists",
            )

    updated_app_setting = app_setting_service.update_app_setting(
        app_setting_id, app_setting
    )
    if not updated_app_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="App setting not found"
        )
    return updated_app_setting


@router.delete("/{app_setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_app_setting(app_setting_id: UUID, db: Session = Depends(get_db)):
    """Delete an app setting."""
    if not AppSettingService(db).delete_app_setting(app_setting_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="App setting not found"
        )
