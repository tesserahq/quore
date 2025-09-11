import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.app_setting import AppSetting
from app.schemas.app_setting import AppSettingCreate, AppSettingUpdate
from app.services.app_setting_service import AppSettingService


@pytest.fixture
def sample_app_setting_data():
    return {
        "key": "test_setting",
        "value": "test_value",
    }


@pytest.fixture
def sample_app_setting(db: Session, sample_app_setting_data):
    app_setting = AppSetting(**sample_app_setting_data)
    db.add(app_setting)
    db.commit()
    db.refresh(app_setting)
    return app_setting


def test_create_app_setting(db: Session, sample_app_setting_data):
    """Test creating a new app setting."""
    # Create app setting
    app_setting_create = AppSettingCreate(**sample_app_setting_data)
    app_setting = AppSettingService(db).create_app_setting(app_setting_create)

    # Assertions
    assert app_setting.id is not None
    assert app_setting.key == sample_app_setting_data["key"]
    assert app_setting.value == sample_app_setting_data["value"]
    assert app_setting.created_at is not None
    assert app_setting.updated_at is not None


def test_get_app_setting(db: Session, sample_app_setting):
    """Test getting a single app setting by ID."""
    # Get app setting
    retrieved_app_setting = AppSettingService(db).get_app_setting(sample_app_setting.id)

    # Assertions
    assert retrieved_app_setting is not None
    assert retrieved_app_setting.id == sample_app_setting.id
    assert retrieved_app_setting.key == sample_app_setting.key
    assert retrieved_app_setting.value == sample_app_setting.value


def test_get_app_setting_by_key(db: Session, sample_app_setting):
    """Test getting an app setting by key."""
    # Get app setting by key
    retrieved_app_setting = AppSettingService(db).get_app_setting_by_key(
        sample_app_setting.key
    )

    # Assertions
    assert retrieved_app_setting is not None
    assert retrieved_app_setting.id == sample_app_setting.id
    assert retrieved_app_setting.key == sample_app_setting.key
    assert retrieved_app_setting.value == sample_app_setting.value


def test_get_app_settings(db: Session, sample_app_setting):
    """Test getting all app settings with pagination."""
    # Get all app settings
    app_settings = AppSettingService(db).get_app_settings()

    # Assertions
    assert len(app_settings) >= 1
    assert any(a.id == sample_app_setting.id for a in app_settings)


def test_get_app_settings_with_pagination(db: Session, sample_app_setting):
    """Test getting app settings with pagination parameters."""
    # Create additional app settings
    for i in range(5):
        app_setting = AppSetting(key=f"key_{i}", value=f"value_{i}")
        db.add(app_setting)
    db.commit()

    # Test pagination
    app_settings = AppSettingService(db).get_app_settings(skip=2, limit=3)
    assert len(app_settings) <= 3


def test_update_app_setting(db: Session, sample_app_setting):
    """Test updating an existing app setting."""
    # Update data
    update_data = {
        "key": "updated_setting",
        "value": "updated_value",
    }
    app_setting_update = AppSettingUpdate(**update_data)

    # Update app setting
    updated_app_setting = AppSettingService(db).update_app_setting(
        sample_app_setting.id, app_setting_update
    )

    # Assertions
    assert updated_app_setting is not None
    assert updated_app_setting.id == sample_app_setting.id
    assert updated_app_setting.key == update_data["key"]
    assert updated_app_setting.value == update_data["value"]


def test_update_app_setting_partial(db: Session, sample_app_setting):
    """Test updating an app setting with partial data."""
    # Update only the value
    update_data = {"value": "new_value_only"}
    app_setting_update = AppSettingUpdate(**update_data)

    # Update app setting
    updated_app_setting = AppSettingService(db).update_app_setting(
        sample_app_setting.id, app_setting_update
    )

    # Assertions
    assert updated_app_setting is not None
    assert updated_app_setting.id == sample_app_setting.id
    assert updated_app_setting.key == sample_app_setting.key  # Should remain unchanged
    assert updated_app_setting.value == update_data["value"]


def test_delete_app_setting(db: Session, sample_app_setting):
    """Test soft deleting an app setting."""
    app_setting_service = AppSettingService(db)

    # Delete app setting
    success = app_setting_service.delete_app_setting(sample_app_setting.id)

    # Assertions
    assert success is True
    deleted_app_setting = app_setting_service.get_app_setting(sample_app_setting.id)
    assert deleted_app_setting is None


def test_app_setting_not_found_cases(db: Session):
    """Test various not found cases."""
    app_setting_service = AppSettingService(db)
    non_existent_id = uuid4()

    # Get non-existent app setting
    assert app_setting_service.get_app_setting(non_existent_id) is None

    # Get by non-existent key
    assert app_setting_service.get_app_setting_by_key("nonexistent_key") is None

    # Update non-existent app setting
    update_data = {"value": "updated_value"}
    app_setting_update = AppSettingUpdate(**update_data)
    assert (
        app_setting_service.update_app_setting(non_existent_id, app_setting_update)
        is None
    )

    # Delete non-existent app setting
    assert app_setting_service.delete_app_setting(non_existent_id) is False


def test_search_app_settings_with_filters(db: Session, sample_app_setting):
    """Test search method with dynamic filters."""
    # Search using ilike filter on key
    filters = {"key": {"operator": "ilike", "value": "%test%"}}
    results = AppSettingService(db).search(filters)

    assert isinstance(results, list)
    assert any(app_setting.id == sample_app_setting.id for app_setting in results)

    # Search using exact match
    filters = {"key": sample_app_setting.key}
    results = AppSettingService(db).search(filters)

    assert len(results) == 1
    assert results[0].id == sample_app_setting.id

    # Search with no match
    filters = {"key": {"operator": "==", "value": "nonexistent_key"}}
    results = AppSettingService(db).search(filters)

    assert len(results) == 0


def test_get_setting_value(db: Session, sample_app_setting):
    """Test getting setting value by key with default."""
    app_setting_service = AppSettingService(db)

    # Get existing setting value
    value = app_setting_service.get_setting_value(sample_app_setting.key)
    assert value == sample_app_setting.value

    # Get non-existent setting with default
    default_value = "default_value"
    value = app_setting_service.get_setting_value("nonexistent_key", default_value)
    assert value == default_value

    # Get non-existent setting without default
    value = app_setting_service.get_setting_value("nonexistent_key")
    assert value is None


def test_set_setting_value_existing(db: Session, sample_app_setting):
    """Test setting value for existing setting."""
    app_setting_service = AppSettingService(db)
    new_value = "new_value"

    # Set value for existing setting
    updated_app_setting = app_setting_service.set_setting_value(
        sample_app_setting.key, new_value
    )

    # Assertions
    assert updated_app_setting is not None
    assert updated_app_setting.id == sample_app_setting.id
    assert updated_app_setting.key == sample_app_setting.key
    assert updated_app_setting.value == new_value


def test_set_setting_value_new(db: Session):
    """Test setting value for new setting."""
    app_setting_service = AppSettingService(db)
    new_key = "new_setting"
    new_value = "new_value"

    # Set value for new setting
    created_app_setting = app_setting_service.set_setting_value(new_key, new_value)

    # Assertions
    assert created_app_setting is not None
    assert created_app_setting.key == new_key
    assert created_app_setting.value == new_value
    assert created_app_setting.id is not None
    assert created_app_setting.created_at is not None
    assert created_app_setting.updated_at is not None


def test_app_setting_timestamps(db: Session, sample_app_setting_data):
    """Test that created_at and updated_at timestamps are properly set."""
    app_setting_service = AppSettingService(db)

    # Create app setting
    app_setting_create = AppSettingCreate(**sample_app_setting_data)
    app_setting = app_setting_service.create_app_setting(app_setting_create)

    # Check timestamps
    assert isinstance(app_setting.created_at, datetime)
    assert isinstance(app_setting.updated_at, datetime)
    assert app_setting.created_at <= datetime.now()
    assert app_setting.updated_at <= datetime.now()


def test_app_setting_soft_delete_behavior(db: Session, sample_app_setting):
    """Test that soft delete works correctly."""
    app_setting_service = AppSettingService(db)

    # Verify app setting exists
    assert app_setting_service.get_app_setting(sample_app_setting.id) is not None

    # Soft delete
    success = app_setting_service.delete_app_setting(sample_app_setting.id)
    assert success is True

    # Verify it's soft deleted (not found via normal query)
    assert app_setting_service.get_app_setting(sample_app_setting.id) is None

    # Verify it's still in database but marked as deleted
    # Use the soft delete service method to get the record regardless of deletion status
    db_app_setting = app_setting_service.get_record_any_status(sample_app_setting.id)
    assert db_app_setting is not None
    assert db_app_setting.deleted_at is not None
