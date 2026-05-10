## Branch Naming

Format: `<type>/<short-description>` using kebab-case

| Type | When to use | Example |
|---|---|---|
| `feat/` | New feature or capability | `feat/user-email-verification` |
| `fix/` | Bug fix | `fix/login-redirect-loop` |
| `hotfix/` | Emergency production fix | `hotfix/payment-timeout-crash` |
| `refactor/` | Code restructure with no behavior change | `refactor/extract-auth-middleware` |
| `docs/` | Documentation only | `docs/api-authentication-guide` |
| `chore/` | Tooling, dependencies, CI | `chore/upgrade-node-20` |
| `release/` | Release preparation | `release/v2.3.0` |

- Max 50 characters total; use hyphens, not underscores
- Reference the issue/ticket number if applicable: `fix/123-login-redirect-loop`

## Commit Messages

Follow Conventional Commits format: `<type>(<scope>): <subject>`

- `feat`: new feature (triggers minor version bump)
- `fix`: bug fix (triggers patch version bump)
- `docs`: documentation only
- `refactor`: code change without behavior change
- `test`: adding or correcting tests
- `chore`: tooling, dependencies, CI/CD changes
- `perf`: performance improvement
- `BREAKING CHANGE`: footer note for incompatible API changes (triggers major version bump)

Subject line rules:
- Imperative mood: `"add user login"` not `"added"` or `"adding"`
- 72 characters max
- No period at end
- If a body is needed, separate from subject with a blank line

## Pull Request Workflow

1. Open a draft PR early to signal work-in-progress; remove draft when ready for review
2. PR description must include: what changed, why, and how to test it
3. Self-review the diff (`git diff main...HEAD`) before requesting review
4. Assign at least one reviewer; for security or data changes, assign two
5. Resolve all review comments before merging; do not dismiss without addressing
6. Delete the branch immediately after merge

Merge requirements:
- At least 1 approval (2 for changes to auth, payments, or data migrations)
- All CI checks passing
- No unresolved review comments

## Merge Strategy

- **Default: squash and merge** — one commit per PR on `main`; keeps history linear
- **Exception: merge commit** — for release branches or when commit history detail matters
- **Never rebase `main` onto a feature branch** — only rebase feature branches onto `main`
- Force push is forbidden on `main`; permitted on personal feature branches only

## Branch Lifecycle

- Feature branches live no longer than 3 days; split the work if it takes longer
- Delete merged branches immediately; stale branches are pruned weekly
- Never reuse a branch name after it has been merged

## Emergency Hotfix Procedure

1. Branch from `main` (not a feature branch): `git checkout -b hotfix/<description> main`
2. Apply the minimal fix — no unrelated changes
3. Open a PR marked `[HOTFIX]`; requires 1 approval (on-call engineer)
4. Merge immediately after approval; deploy to production
5. Back-merge `main` into any open long-running branches

## Versioning

- Semantic versioning: `MAJOR.MINOR.PATCH`
- Version is determined by Conventional Commits types: `feat` → minor, `fix` → patch, `BREAKING CHANGE` → major
- Tag releases on `main` after merging the release branch: `git tag v2.3.0`
- Maintain a `CHANGELOG.md`; update it as part of the release PR
