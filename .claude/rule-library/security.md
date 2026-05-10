## Secrets

Secrets are: API keys, passwords, database credentials, private keys (RSA/EC/SSH), OAuth client secrets, signing keys, JWT secrets, session encryption keys, and webhook verification tokens. Usernames, email addresses, and non-secret config values are not secrets.

- Never hardcode secrets in source code, config files, or Dockerfiles — use environment variables injected at runtime
- Never commit `.env` files containing real secrets; always provide `.env.example` with placeholder values and comments
- Never log secrets, passwords, tokens, or PII — scrub or omit before logging
- Rotate secrets after any suspected exposure; treat exposure as a SEV1 incident

## Input Validation

- Validate and sanitize all input at system boundaries (HTTP request, message queue, file upload)
- Reject unknown fields; validate type, length, format, and range
- Trust nothing from outside the process boundary — including data from your own DB if it was once external input

## File Upload

- Enforce a maximum file size (e.g., 10MB default; adjust per use case) — reject oversized uploads before processing
- Validate MIME type by inspecting file headers (magic bytes), not just the `Content-Type` header or file extension
- Store uploaded files outside the web root; never execute uploaded files
- Use a random UUID as the stored filename — never use the client-supplied filename
- Scan uploads with an antivirus/malware scanner if files will be shared or executed
- Prevent path traversal: normalize all paths and reject any containing `..` or absolute paths

## Injection (OWASP A03)

- SQL: parameterized queries or ORM only — never string concatenation or interpolation
- Command injection: never pass user input to shell commands
- Template injection: use template engines with auto-escaping enabled

## XSS (OWASP A03)

- Escape all user-controlled output in HTML templates
- Set `Content-Security-Policy` headers; forbid `unsafe-inline`
- Use `HttpOnly` and `Secure` flags on session cookies

## CSRF (OWASP A01)

- Require CSRF tokens on all state-changing requests (POST, PUT, PATCH, DELETE)
- Verify `Origin` / `Referer` headers on sensitive endpoints

## Rate Limiting

- Apply rate limits to all authentication endpoints: max 5 failed attempts per IP per 15 minutes, then 15-minute lockout
- Apply rate limits to user-triggered actions that have cost or abuse potential (email sending, SMS, payment attempts)
- Apply rate limits to all outbound external API calls — stay within provider quotas and protect against runaway loops
- Return `429 Too Many Requests` with a `Retry-After` header; never return `400` or `503` for rate limit responses

## Authentication (OWASP A07)

- Never store plaintext passwords — use bcrypt, argon2, or scrypt with appropriate work factor
- Use short-lived JWTs (15 min access token); rotate refresh tokens on each use
- Invalidate all sessions on password change
- Rate-limit and lock accounts after repeated failed login attempts (see Rate Limiting above)

## Authorization (OWASP A01)

- Check authorization on every request — do not rely on UI hiding to enforce access control
- Use deny-by-default: explicitly grant access, never assume it
- Enforce row-level ownership checks (user can only access their own data)

## Sensitive Data (OWASP A02)

- Encrypt sensitive data at rest (PII, payment data, health records)
- Use HTTPS only in production; reject HTTP
- Set `Strict-Transport-Security` header

## Dependencies (OWASP A06)

- Run `npm audit` / `pip audit` / `bundle audit` before every deploy
- Pin dependency versions; review lock file changes in PR
- Remove unused dependencies
