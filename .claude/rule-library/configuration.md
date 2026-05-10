## Environment Variables

Naming convention: `APP_<SERVICE>_<KEY>` in SCREAMING_SNAKE_CASE

| Rule | Rationale |
|---|---|
| All caps, underscores only | Shell portability; avoid ambiguity |
| Prefix with app/service name | Prevents collision in shared environments |
| Boolean values: `"true"` / `"false"` | Consistent parsing across languages |
| Numeric values: plain integer or decimal | No units in the value; encode units in the key name (`TIMEOUT_SECONDS`) |

Examples:
```
AUTH_SERVICE_JWT_SECRET=...
PAYMENT_STRIPE_API_KEY=...
DB_MAX_CONNECTIONS=20
HTTP_SERVER_TIMEOUT_SECONDS=30
```

## Secret Management

- Secrets are: API keys, passwords, private keys, OAuth client secrets, database credentials, signing keys
- Secrets must never appear in: source code, config files in the repo, CI logs, or error messages
- Store secrets in a dedicated secrets manager (HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, GitHub Actions Secrets)
- Inject secrets as environment variables at runtime — never bake them into container images
- Rotate secrets on a schedule: annual minimum; immediately after any suspected exposure
- Each service uses its own credentials — never share API keys or DB passwords across services

## Configuration Files

- Use YAML for human-authored config (clear, supports comments); use JSON only for machine-generated config
- Provide a `config/default.yaml` with safe non-secret defaults; overlay with `config/<environment>.yaml`
- Every configuration key must have a comment explaining its purpose and valid range
- Validate configuration at startup — fail fast with a clear error if required values are missing or out of range

## Environment Management

- Named environments: `development`, `test`, `staging`, `production`
- `development`: permissive defaults; external services may be mocked
- `test`: deterministic; no external network calls; uses test doubles
- `staging`: mirrors production config shape; uses separate data and credentials
- `production`: all secrets from secrets manager; strictest validation

Config loading order (later overrides earlier):
1. `config/default.yaml`
2. `config/<environment>.yaml`
3. Environment variables (highest priority)

## Feature Flags

- Feature flags control rollout of incomplete or experimental behavior
- Each flag must have: name, description, owner, and a removal date or condition
- Flags are boolean by default; use percentage rollout only when gradual rollout is required
- Remove flags within 30 days of full rollout — flags that outlive their purpose become hidden config
- Never use feature flags to hide broken features in production; fix the feature first

## Configuration Documentation

- Maintain a `docs/configuration.md` listing every environment variable with: type, default, required/optional, description
- Update the documentation as part of any PR that adds or changes a configuration key
- Provide `.env.example` with placeholder values and inline comments for local development setup
