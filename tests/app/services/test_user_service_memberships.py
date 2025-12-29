import pytest
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import DetachedInstanceError
from app.models.user import User
from app.models.membership import Membership
from app.models.workspace import Workspace
from app.schemas.user import UserOnboard
from app.services.user_service import UserService
from app.constants.membership import MembershipRoles


@pytest.fixture
def user_with_membership(db: Session, faker):
    """Create a user with a workspace membership."""
    # Create user with external_id (required for get_user_by_external_id)
    external_id = f"auth0|{faker.uuid4()}"
    user = User(
        email=faker.email(),
        username=faker.user_name(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        provider="auth0",
        external_id=external_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create workspace
    workspace = Workspace(
        name=faker.company(),
        description=faker.text(100),
        created_by_id=user.id,
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Create membership
    membership = Membership(
        user_id=user.id,
        workspace_id=workspace.id,
        role=MembershipRoles.OWNER,
        created_by_id=user.id,
    )
    db.add(membership)
    db.commit()

    return user, workspace, membership


def test_get_user_by_external_id_eager_loads_memberships(db: Session, user_with_membership):
    """
    Test that get_user_by_external_id eagerly loads the memberships relationship.
    This prevents DetachedInstanceError when accessing memberships after session is closed.
    """
    user, workspace, _ = user_with_membership
    user_service = UserService(db)

    # Fetch user by external_id
    fetched_user = user_service.get_user_by_external_id(user.external_id)
    assert fetched_user is not None

    # Expire the session to simulate what happens in verify_token_dependency
    db.expire_all()

    # This should NOT raise DetachedInstanceError because memberships are eagerly loaded
    memberships = fetched_user.memberships
    assert len(memberships) == 1
    assert memberships[0].workspace_id == workspace.id


def test_get_user_by_external_id_memberships_accessible_after_expunge(db: Session, user_with_membership):
    """
    Test that memberships are accessible even after the user is expunged from session.
    This simulates the auth flow where session is closed after loading user.
    """
    user, workspace, _ = user_with_membership
    user_service = UserService(db)

    # Fetch user by external_id
    fetched_user = user_service.get_user_by_external_id(user.external_id)
    assert fetched_user is not None

    # Expunge the user from the session (similar to what happens when session closes)
    db.expunge(fetched_user)

    # This should NOT raise DetachedInstanceError
    memberships = fetched_user.memberships
    assert len(memberships) == 1
    assert memberships[0].workspace_id == workspace.id


def test_get_user_by_external_id_returns_empty_memberships_for_new_user(db: Session, faker):
    """
    Test that a user without memberships returns an empty list, not None.
    """
    # Create user without any memberships
    external_id = f"auth0|{faker.uuid4()}"
    user = User(
        email=faker.email(),
        username=faker.user_name(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        provider="auth0",
        external_id=external_id,
    )
    db.add(user)
    db.commit()

    user_service = UserService(db)
    fetched_user = user_service.get_user_by_external_id(external_id)

    # Expire session to simulate closed session
    db.expire_all()

    # Should return empty list, not raise error
    assert fetched_user.memberships == []


def test_onboard_user_returns_user_with_accessible_memberships(db: Session, faker):
    """
    Test that onboard_user returns a user with memberships relationship loaded.
    """
    user_service = UserService(db)

    user_onboard = UserOnboard(
        id=faker.uuid4(),
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        external_id=f"auth0|{faker.uuid4()}",
    )

    # Onboard the user
    new_user = user_service.onboard_user(user_onboard)
    assert new_user is not None

    # Expire session
    db.expire_all()

    # Should NOT raise DetachedInstanceError - memberships should be loaded (empty for new user)
    assert new_user.memberships == []


def test_user_workspace_ids_accessible_after_session_expired(db: Session, user_with_membership):
    """
    Test the exact pattern used in prompt.py and credential.py routers:
    accessing workspace_ids from memberships after session is no longer active.
    """
    user, workspace, _ = user_with_membership
    user_service = UserService(db)

    # Fetch user (as done in auth verification)
    fetched_user = user_service.get_user_by_external_id(user.external_id)

    # Expire session (simulates session.close() in verify_token_dependency)
    db.expire_all()

    # This is the exact pattern from the routers that was failing:
    user_workspace_ids = [m.workspace_id for m in fetched_user.memberships]

    assert len(user_workspace_ids) == 1
    assert workspace.id in user_workspace_ids


def test_membership_check_pattern_works_after_session_expired(db: Session, user_with_membership):
    """
    Test the credential.py pattern: checking if user has membership in a workspace.
    """
    user, workspace, _ = user_with_membership
    user_service = UserService(db)

    # Fetch user
    fetched_user = user_service.get_user_by_external_id(user.external_id)

    # Expire session
    db.expire_all()

    # This is the pattern from credential.py that was failing:
    has_access = any(m.workspace_id == workspace.id for m in fetched_user.memberships)

    assert has_access is True

