"""Constants for membership roles."""

OWNER_ROLE = "owner"
ADMIN_ROLE = "administrator"
COLLABORATOR_ROLE = "collaborator"

# List of all valid roles
VALID_ROLES = [OWNER_ROLE, ADMIN_ROLE, COLLABORATOR_ROLE]

# Role data for API responses
ROLES_DATA = [
    {"id": OWNER_ROLE, "name": "Owner"},
    {"id": ADMIN_ROLE, "name": "Administrator"},
    {"id": COLLABORATOR_ROLE, "name": "Collaborator"},
]


class MembershipRoles:
    OWNER = "owner"
    ADMIN = "admin"
    COLLABORATOR = "collaborator"

    @classmethod
    def get_all(cls):
        return [cls.OWNER, cls.ADMIN, cls.COLLABORATOR]
