## Merge Policy

- Never merge directly to `main` — all changes require a PR
- PR merge requires: at least one approval + all CI checks passing
- Branch protection on `main`: no force push, no direct commits

## PR Gates (CI must enforce all of these)

Tests pass — specifically:
- Unit tests: zero failures; run on every PR
- Integration tests: zero failures; run on every PR (may be parallelized by module)
- End-to-end tests: zero failures against the staging environment after merge, not on PR (too slow for PR gates)
- Flaky test failures are treated as real failures — fix or quarantine the test; do not re-run to pass

Other gates:
- Type checking passes (`tsc --noEmit`, `mypy`, `go vet`) — zero errors
- Coverage meets threshold: critical paths (auth, payments, data mutations) 90%+; overall 70%+
- Lint clean: zero errors; warnings treated as errors in CI (`eslint --max-warnings=0`, `flake8`, `golangci-lint`)
- No secrets detected in diff (run `gitleaks detect --source .` or `detect-secrets scan`)
- Dependency audit passes (`npm audit --audit-level=high`, `pip audit`, `govulncheck`)

## Deploy Flow

- Deploy to staging before production — no exceptions
- Staging must be a functional replica of production (same config shape, same infra)
- Validate the feature in staging before promoting the deploy
- Never deploy on Fridays or before holidays without an on-call engineer available

## Rollback

- Every deploy must have a documented rollback procedure before it is promoted
- Rollback must be executable in under 5 minutes
- Database migrations must be backward-compatible with the previous deploy so rollback does not require a schema revert

## Secrets in CI

- Never put secrets in `.env` files checked into the repository
- Use the CI platform's secrets manager (GitHub Actions secrets, GitLab CI variables, etc.)
- Rotate secrets after any suspected exposure; treat exposure as an incident

## Dependency Scanning

- Run a dependency vulnerability scan on every deploy pipeline run
- Block deploys with high or critical CVEs unless explicitly approved and tracked

## Emergency Deploy (Hotfix)

For production incidents requiring an immediate fix:
1. Branch from `main`: `git checkout -b hotfix/<description> main`
2. Apply the minimal fix; do not bundle unrelated changes
3. Open a PR marked `[HOTFIX]`; CI gates still run — they may not be skipped
4. Requires 1 approval from an on-call or senior engineer (normal 2-approval requirement is waived)
5. Deploy directly to production after merge; staging validation is still required but may be abbreviated (5 min smoke test)
6. Create a post-mortem ticket immediately after the incident is resolved
