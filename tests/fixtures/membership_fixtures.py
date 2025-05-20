import pytest
from app.models.membership import Membership
from app.constants.membership import MEMBER_ROLE


@pytest.fixture
def setup_membership(db, setup_user, setup_workspace):
    """Create a test membership for use in tests."""
    user = setup_user
    workspace = setup_workspace

    membership_data = {
        "user_id": user.id,
        "workspace_id": workspace.id,
        "role": MEMBER_ROLE,
    }

    membership = Membership(**membership_data)
    db.add(membership)
    db.commit()
    db.refresh(membership)

    return membership
