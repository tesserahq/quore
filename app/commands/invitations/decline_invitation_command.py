from uuid import UUID
from sqlalchemy.orm import Session

from app.services.invitation_service import InvitationService


class DeclineInvitationCommand:
    """
    Command to decline an invitation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.invitation_service = InvitationService(db)

    def execute(self, invitation_id: UUID, invited_user_email: str) -> bool:
        """
        Execute the command to decline an invitation.

        Args:
            invitation_id: The ID of the invitation to decline
            user_email: The email of the user declining the invitation

        Returns:
            bool: True if invitation was successfully declined, False if not found

        Raises:
            ValueError: If invitation has expired or user is not authorized
            Exception: If invitation decline fails
        """
        try:
            # Decline the invitation
            success = self.invitation_service.decline_invitation(
                invitation_id, invited_user_email
            )

            return success

        except ValueError as e:
            # Re-raise ValueError (e.g., expired invitation, unauthorized user) without rollback
            raise e
        except Exception as e:
            # Rollback the transaction if something goes wrong
            self.db.rollback()
            raise Exception(f"Failed to decline invitation: {str(e)}")
