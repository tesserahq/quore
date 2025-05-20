# Quore Data Model Overview

This document outlines the relationships and ownership structure between `Users`, `Workspaces`, `Memberships`, and `Projects` in our system.

## Entities

### Users

Represents a global identity across the system.

- Unique across all workspaces.
- Can belong to multiple workspaces via `Memberships`.
- May be soft-deleted to preserve historical ownership data.

```json
{
  "id": "user_123",
  "email": "alice@example.com",
  "deleted_at": null
}
```

### Workspaces

Top-level collaborative entity.

- Created by a **User**.
- Modified by a **Membership** (workspace-contextual action).
- Users gain access via `Memberships`.

#### Key Fields for Workspaces

| Field                      | Type              | Description                                                      |
| -------------------------- | ----------------- | ---------------------------------------------------------------- |
| `created_by_user_id`       | `UUID`            | Global user ID at creation time. Always present.                 |
| `created_by_user_email`    | `string`          | Snapshot of user's email at time of creation.                    |
| `created_by_membership_id` | `UUID (nullable)` | Optional reference to the membership, backfilled after creation. |
| `updated_by_membership_id` | `UUID`            | Membership that last updated the workspace.                      |

### Memberships

Represents a user's participation in a workspace.

- Contains role/permissions metadata.
- Used to scope actions within a workspace.
- Soft-deletable for audit consistency.

#### Key Fields for Memberships

| Field          | Type                   | Description                                    |
| -------------- | ---------------------- | ---------------------------------------------- |
| `user_id`      | `UUID`                 | Global user reference.                         |
| `workspace_id` | `UUID`                 | Associated workspace.                          |
| `role`         | `string`               | Role within the workspace (e.g. owner, admin). |
| `deleted_at`   | `timestamp (nullable)` | Used for soft-deletion.                        |

### Projects

Resources owned by a workspace.

- Always tied to a `workspace_id`.
- Created and updated via `membership_id`.

#### Key Fields for Projects

| Field                      | Type   | Description                                 |
| -------------------------- | ------ | ------------------------------------------- |
| `workspace_id`             | `UUID` | Parent workspace.                           |
| `created_by_membership_id` | `UUID` | Membership that created this project.       |
| `updated_by_membership_id` | `UUID` | Membership that last modified this project. |

## Ownership and Deletion Handling

- **Users are soft-deleted** using a `deleted_at` column. This preserves `created_by_user_id` and allows denormalized fields like `created_by_user_email` to remain readable.
- **Memberships are soft-deleted** to preserve historical integrity in references like `created_by_membership_id`.
- No hard deletes for users or memberships referenced by `workspaces` or `projects`.
- When a user leaves a workspace:
  - Their membership is soft-deleted.
  - Ownership of projects may be reassigned or left as-is for audit trail.

## Why Both `user_id` and `membership_id`?

We track both for layered context:

- `user_id`: Global identity.
- `membership_id`: Scoped identity within a workspace (includes role & permissions).

This hybrid model supports robust auditing, access control, and consistent data integrity.
