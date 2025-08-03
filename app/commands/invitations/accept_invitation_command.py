from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.invitation_service import InvitationService
from app.services.membership_service import MembershipService
from app.models.membership import Membership
from app.schemas.membership import MembershipCreate


class AcceptInvitationCommand:
    """
    Command to accept an invitation and create a membership for the user.
    """

    def __init__(self, db: Session):
        self.db = db
        self.invitation_service = InvitationService(db)
        self.membership_service = MembershipService(db)

    def execute(
        self, invitation_id: UUID, accepted_by_id: UUID
    ) -> Optional[Membership]:
        """
        Execute the command to accept an invitation and create a membership.

        Args:
            invitation_id: The ID of the invitation to accept
            accepted_by_id: The ID of the user accepting the invitation

        Returns:
            Membership: The created membership, or None if invitation not found

        Raises:
            ValueError: If invitation has expired
            Exception: If invitation acceptance fails
        """
        try:
            # Accept the invitation
            invitation = self.invitation_service.accept_invitation(invitation_id)

            if not invitation:
                raise Exception(f"Invitation with ID {invitation_id} not found")

            # Create membership
            membership_data = MembershipCreate(
                user_id=accepted_by_id,
                workspace_id=invitation.workspace_id,
                role=invitation.role,
                created_by_id=invitation.inviter_id,
            )

            membership = self.membership_service.create_membership(membership_data)

            return membership

        except ValueError as e:
            # Re-raise ValueError (e.g., expired invitation) without rollback
            raise e
        except Exception as e:
            # Rollback the transaction if something goes wrong
            self.db.rollback()
            raise Exception(f"Failed to accept invitation: {str(e)}")
