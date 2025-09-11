from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.app_setting import AppSetting
from app.schemas.app_setting import AppSettingCreate, AppSettingUpdate
from app.services.soft_delete_service import SoftDeleteService
from app.utils.db.filtering import apply_filters


class AppSettingService(SoftDeleteService[AppSetting]):
    """Service class for managing AppSetting entities."""

    def __init__(self, db: Session):
        super().__init__(db, AppSetting)

    def get_app_setting(self, app_setting_id: UUID) -> Optional[AppSetting]:
        """Get a single app setting by ID."""
        return self.db.query(AppSetting).filter(AppSetting.id == app_setting_id).first()

    def get_app_setting_by_key(self, key: str) -> Optional[AppSetting]:
        """Get an app setting by its key."""
        return self.db.query(AppSetting).filter(AppSetting.key == key).first()

    def get_app_settings(self, skip: int = 0, limit: int = 100) -> List[AppSetting]:
        """Get a list of app settings with pagination."""
        return self.db.query(AppSetting).offset(skip).limit(limit).all()

    def create_app_setting(self, app_setting: AppSettingCreate) -> AppSetting:
        """Create a new app setting."""
        db_app_setting = AppSetting(**app_setting.model_dump())
        self.db.add(db_app_setting)
        self.db.commit()
        self.db.refresh(db_app_setting)
        return db_app_setting

    def update_app_setting(
        self, app_setting_id: UUID, app_setting: AppSettingUpdate
    ) -> Optional[AppSetting]:
        """Update an existing app setting."""
        db_app_setting = (
            self.db.query(AppSetting).filter(AppSetting.id == app_setting_id).first()
        )
        if db_app_setting:
            update_data = app_setting.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_app_setting, key, value)
            self.db.commit()
            self.db.refresh(db_app_setting)
        return db_app_setting

    def delete_app_setting(self, app_setting_id: UUID) -> bool:
        """Soft delete an app setting."""
        return self.delete_record(app_setting_id)

    def search(self, filters: Dict[str, Any]) -> List[AppSetting]:
        """
        Search app settings based on provided filters.

        Args:
            filters: Dictionary of filters where key is the field name and value is either:
                - A direct value (uses = operator)
                - A dictionary with 'operator' and 'value', e.g. {"operator": "ilike", "value": "%key%"}

        Returns:
            List[AppSetting]: List of app settings matching the filter criteria.

        Example:
            filters = {
                "key": {"operator": "ilike", "value": "%theme%"},
                "value": {"operator": "!=", "value": "default"}
            }
        """
        query = self.db.query(AppSetting)
        query = apply_filters(query, AppSetting, filters)
        return query.all()

    def get_setting_value(
        self, key: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Get the value of a setting by key, with optional default."""
        app_setting = self.get_app_setting_by_key(key)
        return app_setting.value if app_setting else default

    def set_setting_value(self, key: str, value: str) -> AppSetting:
        """Set or update a setting value by key."""
        existing_setting = self.get_app_setting_by_key(key)
        if existing_setting:
            existing_setting.value = value
            self.db.commit()
            self.db.refresh(existing_setting)
            return existing_setting
        else:
            # Create new setting
            new_setting = AppSettingCreate(key=key, value=value)
            return self.create_app_setting(new_setting)
