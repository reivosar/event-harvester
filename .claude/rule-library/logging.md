## Log Levels

| Level | When to use | Example |
|---|---|---|
| `ERROR` | Operation failed; requires human attention | Payment processing failed, DB connection lost |
| `WARN` | Degraded state; system continues but something is wrong | Retry succeeded after 2 attempts, cache miss rate elevated |
| `INFO` | Normal flow milestones worth recording | User logged in, order placed, migration started |
| `DEBUG` | Diagnostic detail for development; disabled in production | SQL query, HTTP request body, function entry |

Rules:
- `ERROR` must be actionable — if no one needs to act on it, it's `WARN` or lower
- `DEBUG` is off in production by default; enable per-request via a header flag if needed
- Never use `INFO` for events that happen more than 100 times per second — use metrics instead

## Structured Logging

All log entries must be structured (JSON or key-value pairs) — never concatenated strings.

Required fields on every log line:

| Field | Description | Example |
|---|---|---|
| `timestamp` | ISO 8601 UTC | `2026-05-08T12:34:56.789Z` |
| `level` | Log level string | `"INFO"` |
| `message` | Short, static description (no dynamic values in the message) | `"User login succeeded"` |
| `service` | Service or application name | `"auth-service"` |
| `trace_id` | Distributed trace identifier | `"4bf92f3577b34da6"` |
| `span_id` | Current span within the trace | `"00f067aa0ba902b7"` |

Context fields (add when available): `user_id`, `request_id`, `method`, `path`, `status_code`, `duration_ms`, `error_code`

The `message` field must be static text — dynamic values go in separate fields:
```
✅  message: "Order placed", fields: { order_id: "ord_123", amount_cents: 4999 }
❌  message: "Order ord_123 placed for $49.99"
```

## Sensitive Data

Never log any of the following — mask or omit entirely:
- Passwords, secrets, API keys, tokens, private keys
- Full credit card numbers, CVV, expiry
- Social security / national ID numbers
- Full dates of birth (year only is acceptable)
- IP addresses in combination with user identity
- Raw HTTP request bodies for auth endpoints

Mask partial values when the partial form has diagnostic value (e.g., last 4 digits of a card, first 8 chars of a token).

## Distributed Tracing

- Propagate `trace_id` and `span_id` across all service calls using W3C Trace Context headers (`traceparent`, `tracestate`)
- Create a new child span for every outbound HTTP call, database query, and message queue operation
- Record span status (`ok` / `error`) and duration on every span
- Sampling rate: 100% for errors, 1–10% for success in high-traffic paths

## Performance

- Never perform synchronous log writes in the critical path of a request — use an async log buffer
- Avoid logging in tight loops (per-item in a batch) — log a summary at the end
- Log output must not cause an unhandled exception — wrap log calls defensively if the logger itself can fail
- Measure logging overhead: if structured log serialization adds > 1ms to P99 latency, switch to a faster serializer
