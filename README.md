# Backend

## Assistant permission model

```
Assistant 1-* AssistantUserAccess
         1-* AssistantDepartmentAccess
```

Permissions resolve in the following order:
`edit` overrides `use`, which overrides no access.

## Assistant API

All endpoints under `/api/assistants/` require authentication.  The actions
allowed for a user depend on their permission for each assistant.

| Action (HTTP)       | Who may do it                  |
|--------------------|--------------------------------|
| List / Retrieve    | owner, `edit`, or `use`        |
| Create             | any authenticated user (becomes owner) |
| Update / Delete    | owner or `edit`                |
| Chat/Execute       | owner, `edit`, or `use`        |

Example responses when permission checks fail:

```
GET /api/assistants/<id>/        → 404 Not Found (no access)
PATCH /api/assistants/<id>/      → 403 Forbidden (only "use")
```

## Sharing API

Owners (or admins) can share assistants with individual users or entire departments.

```
POST /api/assistants/<id>/shares/users/ {"user": 5, "permission": "use"}
POST /api/assistants/<id>/shares/users/ {"user": 5, "permission": "edit"}  # update
DELETE /api/assistants/<id>/shares/users/5/
```

Department sharing works the same using the `shares/departments/` routes.


## Performance

For details on building and deploying optimized static assets, see [docs/static-assets.md](docs/static-assets.md).

## Chat threads

User conversations are represented by the `Thread` model. File uploads within a
thread are stored in the `ThreadFile` model which tracks the OpenAI `file_id`,
upload status and metadata. Assistant-level uploads use the separate
`AssistantFile` model. A given `file_id` may appear in **either** table but never
both.
