import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.commands.invitations.accept_invitation_command import AcceptInvitationCommand
from app.models.invitation import Invitation
from app.models.membership import Membership
from app.constants.membership import MembershipRoles
from app.services.invitation_service import InvitationService


class TestAcceptInvitationCommand:
    """Test cases for AcceptInvitationCommand."""

    def test_accept_invitation_success(
        self, db, setup_workspace, setup_user, setup_invitation
    ):
        """Test successfully accepting an invitation and creating a membership."""
        invitation = setup_invitation
        accepting_user = setup_user

        # Execute command
        command = AcceptInvitationCommand(db)
        membership = command.execute(invitation.id, accepting_user.id)

        # Verify membership was created
        assert membership is not None
        assert membership.user_id == accepting_user.id
        assert membership.workspace_id == setup_workspace.id
        assert membership.role == MembershipRoles.COLLABORATOR
        assert membership.created_by_id == invitation.inviter_id

        # Verify invitation was deleted
        deleted_invitation = InvitationService(db).get_invitation(invitation.id)
        assert deleted_invitation is None

    def test_accept_invitation_not_found(self, db, setup_user):
        """Test accepting a non-existent invitation."""
        accepting_user = setup_user
        non_existent_id = uuid4()

        command = AcceptInvitationCommand(db)

        with pytest.raises(
            Exception, match=f"Invitation with ID {non_existent_id} not found"
        ):
            command.execute(non_existent_id, accepting_user.id)

    def test_accept_expired_invitation(self, db, setup_workspace, setup_user, faker):
        """Test accepting an expired invitation."""
        # Create inviter user
        inviter = setup_user

        # Create expired invitation
        invitation = Invitation(
            id=uuid4(),
            email="test@example.com",
            workspace_id=setup_workspace.id,
            inviter_id=inviter.id,
            role=MembershipRoles.COLLABORATOR,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
            message="Test invitation",
        )
        db.add(invitation)
        db.commit()

        # Create user who will try to accept the invitation
        accepting_user = setup_user
        accepting_user.email = "test@example.com"
        db.commit()

        # Execute command
        command = AcceptInvitationCommand(db)

        with pytest.raises(ValueError, match="Invitation has expired"):
            command.execute(invitation.id, accepting_user.id)

        # Verify invitation still exists (not deleted)
        existing_invitation = (
            db.query(Invitation).filter(Invitation.id == invitation.id).first()
        )
        assert existing_invitation is not None

        # Verify no membership was created
        membership = (
            db.query(Membership)
            .filter(
                Membership.user_id == accepting_user.id,
                Membership.workspace_id == setup_workspace.id,
            )
            .first()
        )
        assert membership is None

    def test_accept_invitation_different_role(
        self, db, setup_workspace, setup_user, faker
    ):
        """Test accepting an invitation with a different membership type."""
        # Create inviter user
        inviter = setup_user

        # Create invitation with OWNER membership type
        invitation = Invitation(
            id=uuid4(),
            email="test@example.com",
            workspace_id=setup_workspace.id,
            inviter_id=inviter.id,
            role=MembershipRoles.OWNER,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            message="Test invitation",
        )
        db.add(invitation)
        db.commit()

        # Create user who will accept the invitation
        accepting_user = setup_user
        accepting_user.email = "test@example.com"
        db.commit()

        # Execute command
        command = AcceptInvitationCommand(db)
        membership = command.execute(invitation.id, accepting_user.id)

        # Verify membership was created with correct type
        assert membership is not None
        assert membership.role == MembershipRoles.OWNER
        assert membership.user_id == accepting_user.id
        assert membership.workspace_id == setup_workspace.id
