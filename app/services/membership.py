from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.membership import Membership
from app.schemas.membership import MembershipCreate, MembershipUpdate
from app.utils.db.filtering import apply_filters

"""
Module providing the MembershipService class for managing Membership entities.
Includes methods for CRUD operations, role management, and workspace membership queries.
"""


class MembershipService:
    def __init__(self, db: Session):
        self.db = db

    def get_membership(self, membership_id: UUID) -> Optional[Membership]:
        """Get a membership by its ID."""
        return self.db.query(Membership).filter(Membership.id == membership_id).first()

    def get_user_memberships(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Membership]:
        """Get all memberships for a specific user."""
        return (
            self.db.query(Membership)
            .filter(Membership.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_workspace_memberships(
        self, workspace_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Membership]:
        """Get all memberships for a specific workspace."""
        return (
            self.db.query(Membership)
            .filter(Membership.workspace_id == workspace_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_workspace_membership(
        self, user_id: UUID, workspace_id: UUID
    ) -> Optional[Membership]:
        """Get a specific user's membership in a workspace."""
        return (
            self.db.query(Membership)
            .filter(
                and_(
                    Membership.user_id == user_id,
                    Membership.workspace_id == workspace_id,
                )
            )
            .first()
        )

    def create_membership(self, membership: MembershipCreate) -> Membership:
        """Create a new membership."""
        db_membership = Membership(**membership.model_dump())
        self.db.add(db_membership)
        self.db.commit()
        self.db.refresh(db_membership)
        return db_membership

    def update_membership(
        self, membership_id: UUID, membership: MembershipUpdate
    ) -> Optional[Membership]:
        """Update a membership's role."""
        db_membership = (
            self.db.query(Membership).filter(Membership.id == membership_id).first()
        )
        if db_membership:
            update_data = membership.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_membership, key, value)
            self.db.commit()
            self.db.refresh(db_membership)
        return db_membership

    def delete_membership(self, membership_id: UUID) -> bool:
        """Delete a membership."""
        db_membership = (
            self.db.query(Membership).filter(Membership.id == membership_id).first()
        )
        if db_membership:
            self.db.delete(db_membership)
            self.db.commit()
            return True
        return False

    def search(self, filters: Dict[str, Any]) -> List[Membership]:
        """
        Search memberships based on provided filters.

        Args:
            filters: Dictionary of filters where key is the field name and value is either:
                - A direct value (uses = operator)
                - A dictionary with 'operator' and 'value', e.g. {"operator": "ilike", "value": "%admin%"}

        Returns:
            List[Membership]: List of memberships matching the filter criteria.

        Example:
            filters = {
                "role": {"operator": "in", "value": ["admin", "owner"]},
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        """
        query = self.db.query(Membership)
        query = apply_filters(query, Membership, filters)
        return query.all()
