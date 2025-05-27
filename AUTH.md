# Authentication

This backend uses JSON Web Tokens issued by [djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt).

## Obtain a token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "<user>", "password": "<pass>"}'
```

Response contains `access` and `refresh` tokens. The access token lasts 15 minutes and refresh tokens last one day.

## Refresh the access token

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh>"}'
```

## Verify a token

```bash
curl -X POST http://localhost:8000/api/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "<any-token>"}'
```

## Current user endpoint

`GET /api/users/me/` returns the authenticated user's details when an `Authorization: Bearer <access>` header is provided.

All other endpoints remain open for now. Global locking will be added in a later story.

## Department API

`GET /api/departments/` is public:

```bash
curl http://localhost:8000/api/departments/
```

Write operations require an admin token:

```bash
curl -X POST http://localhost:8000/api/departments/ \
  -H "Authorization: Bearer $ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Research"}'

curl -X PATCH http://localhost:8000/api/departments/1/ \
  -H "Authorization: Bearer $ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'

curl -X DELETE http://localhost:8000/api/departments/1/ \
  -H "Authorization: Bearer $ADMIN" 
```

Write-locking of the entire API will arrive in a later ticket.
