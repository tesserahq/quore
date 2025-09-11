import pytest
from app.models.app_setting import AppSetting


@pytest.fixture(scope="function")
def test_app_setting(db, faker):
    """Create a test app setting for use in tests."""
    app_setting_data = {
        "key": faker.word(),
        "value": faker.word(),
    }

    app_setting = AppSetting(**app_setting_data)
    db.add(app_setting)
    db.commit()
    db.refresh(app_setting)

    return app_setting


@pytest.fixture(scope="function")
def setup_app_setting(db, faker):
    """Create a test app setting for use in tests."""
    app_setting_data = {
        "key": faker.word(),
        "value": faker.word(),
    }

    app_setting = AppSetting(**app_setting_data)
    db.add(app_setting)
    db.commit()
    db.refresh(app_setting)

    return app_setting


@pytest.fixture(scope="function")
def setup_another_app_setting(db, faker):
    """Create another test app setting for use in tests."""
    app_setting_data = {
        "key": faker.word(),
        "value": faker.word(),
    }

    app_setting = AppSetting(**app_setting_data)
    db.add(app_setting)
    db.commit()
    db.refresh(app_setting)

    return app_setting
