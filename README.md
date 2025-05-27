# Backend

## Assistant permission model

```
Assistant 1-* AssistantUserAccess
         1-* AssistantDepartmentAccess
```

Permissions resolve in the following order:
`edit` overrides `use`, which overrides no access.
