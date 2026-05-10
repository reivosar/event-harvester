## Error Classification

Define four error categories and handle each consistently:

| Category | Cause | Retry? | HTTP range |
|---|---|---|---|
| **Validation** | Invalid client input | No — client must fix the request | 400, 422 |
| **Business** | Valid input but rule violated (e.g., insufficient balance) | No — state must change first | 409, 422 |
| **Infrastructure** | DB, network, external service failure | Yes (with backoff) | 503, 502 |
| **Unexpected** | Bugs, unhandled states | No | 500 |

Never mix categories — an input validation error must not become a 500.

## HTTP Status Code Mapping

| Situation | Status |
|---|---|
| Malformed request / missing required field | `400 Bad Request` |
| Missing or invalid auth credentials | `401 Unauthorized` |
| Valid credentials but insufficient permission | `403 Forbidden` |
| Resource not found | `404 Not Found` |
| Business rule violated (conflict with current state) | `409 Conflict` |
| Semantic validation failure (correct format, invalid value) | `422 Unprocessable Entity` |
| Client rate limit exceeded | `429 Too Many Requests` |
| Unexpected server-side error | `500 Internal Server Error` |
| Upstream dependency unavailable | `503 Service Unavailable` |
| Upstream returned an invalid response | `502 Bad Gateway` |

## Error Response Format

All error responses must follow RFC 7807 Problem Details:

```json
{
  "type": "https://errors.example.com/validation/invalid-email",
  "title": "Validation Error",
  "status": 422,
  "detail": "The email address provided is not a valid format.",
  "instance": "/api/users/register",
  "trace_id": "4bf92f3577b34da6"
}
```

Rules:
- `type`: a stable URI identifying the error class (not an individual occurrence)
- `detail`: human-readable; safe to show to end users; no stack traces
- `trace_id`: always include for server-side errors to enable log correlation
- Never expose internal stack traces, SQL errors, or file paths to API consumers

## Error Propagation

- Catch errors at the layer that can handle them; let all others propagate
- Convert infrastructure errors to domain errors at the boundary — callers should not know whether the failure was a timeout or a 503
- Never swallow errors silently — if you catch an error and choose not to re-throw, log it at `WARN` or higher with context
- Wrap errors with context as they propagate: `"failed to fetch user profile: db timeout after 5s"`

## Retry Logic

Retry only `Infrastructure` category errors. Rules:
- Verify the operation is idempotent before retrying — retrying a non-idempotent write can create duplicates
- Use exponential backoff with jitter: start at 100ms, cap at 30s, multiply by 2 per attempt
- Max 3 retries; after exhaustion, escalate to the caller as a `503`
- Do not retry `400`, `401`, `403`, `404`, `409`, `422` — these are deterministic failures

## Error Types in Code

- Define a typed error hierarchy — do not throw raw strings or generic `Error` objects
- Include an `error_code` (machine-readable, stable across versions) alongside a human `message`
- Error codes must not change once published — deprecate and add a new code instead
