"""Constants for membership roles."""

OWNER_ROLE = "owner"
ADMIN_ROLE = "administrator"
MEMBER_ROLE = "member"

# List of all valid roles
VALID_ROLES = [OWNER_ROLE, ADMIN_ROLE, MEMBER_ROLE]

# Role data for API responses
ROLES_DATA = [
    {"id": OWNER_ROLE, "name": "Owner"},
    {"id": ADMIN_ROLE, "name": "Administrator"},
    {"id": MEMBER_ROLE, "name": "Member"},
]
