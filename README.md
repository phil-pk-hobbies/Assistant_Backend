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
