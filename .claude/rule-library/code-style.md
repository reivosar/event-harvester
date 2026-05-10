## Universal Rules

- Indent: 2 spaces for JS/TS/JSON/YAML/HTML; 4 spaces for Python; tabs for Go
- Max line length: 120 characters (100 for Python)
- No trailing whitespace; single blank line at end of file
- Comments explain *why*, not *what* — the code speaks for itself
- No commented-out code — delete it; git history preserves it

## Naming Conventions

| Context | Style | Example |
|---|---|---|
| Variables / functions | camelCase (JS/TS/Java), snake_case (Python/Go) | `fetchUserData`, `fetch_user_data` |
| Classes / types | PascalCase | `UserService`, `PaymentRequest` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| File names | kebab-case (JS/TS), snake_case (Python/Go/Java) | `user-service.ts`, `user_service.py` |
| Booleans | Prefix with `is`, `has`, `can`, `should` | `isActive`, `hasPermission` |
| Interfaces (TS) | No `I` prefix — PascalCase only | `UserRepository` not `IUserRepository` |

Names must be self-documenting — if a reader needs a comment to understand a name, rename it.

**Method / function names** — use verb + noun that state the purpose precisely:
- Good: `calculateInvoiceTotal`, `sendPasswordResetEmail`, `validateShippingAddress`
- Bad: `process`, `handle`, `manage`, `execute`, `run`, `doStuff` — too vague to understand without reading the body

**Class / module names** — include the domain concept, not just the role:
- Good: `InvoiceCalculator`, `PasswordResetMailer`, `ShippingAddressValidator`
- Bad: `InvoiceService`, `UserManager`, `DataHelper`, `CommonUtil` — generic suffixes carry no meaning; name what the class *does*, not what kind of thing it is

**Self-documenting structure** — the code is the documentation:
- A reader should understand what any function does from its name and signature alone
- If understanding requires reading the body, the name is wrong or the function does too much
- Intermediate variables with names beat inline expressions: `const discountedTotal = basePrice * (1 - discountRate)` over `return price * (1 - r)`

## Type Annotations

- TypeScript: always annotate function parameters and return types; avoid `any`; use `unknown` + narrowing when the type is genuinely unknown
- Python: annotate all function signatures with type hints; use `from __future__ import annotations` for forward references
- Go: types are inferred by the compiler; annotate exported APIs clearly
- Java: generics required where applicable; avoid raw types

## Import Ordering

Group imports in this order, separated by blank lines:
1. Standard library / runtime
2. Third-party packages
3. Internal modules (absolute paths)
4. Relative imports (`./`, `../`)

Alphabetize within each group. Let the auto-formatter handle this where available.

## Formatter Enforcement

Always use the language's canonical formatter — do not leave formatting as a manual concern:

| Language | Formatter | Config location |
|---|---|---|
| TypeScript / JavaScript | Prettier | `.prettierrc` |
| Python | Black + isort | `pyproject.toml` |
| Go | gofmt / goimports | built-in; no config |
| Java | google-java-format | enforced via CI |
| YAML / JSON | Prettier | `.prettierrc` |

Treat formatter output as authoritative. Never fight the formatter — change the rule or suppress a specific line with a comment explaining why.

## Language-Specific Rules

### TypeScript / JavaScript

- Prefer `const`; use `let` only when reassignment is required; never `var`
- Use optional chaining (`?.`) and nullish coalescing (`??`) over manual null checks
- Async/await over raw `.then()` chains; always `await` in `try/catch`
- `===` for equality; never `==`
- Avoid `Object.assign` in favor of spread syntax (`{ ...a, ...b }`)
- Use named exports; avoid default exports except for pages/routes

### Python

- Follow PEP 8 strictly; Black enforces it automatically
- Use f-strings over `.format()` or `%` formatting
- Prefer dataclasses or Pydantic models over plain dicts for structured data
- Use `pathlib.Path` over `os.path` for filesystem operations
- `with` statements for all resource management (files, connections)

### Go

- Return errors as values; never ignore an `error` return
- Use `errors.Is` / `errors.As` for error inspection; never compare error strings
- Exported identifiers must have godoc comments
- Avoid global state; pass dependencies via function arguments or struct fields
- `defer` for cleanup; place `defer` immediately after the resource is acquired

### Java

- Immutable over mutable; use `final` for fields where possible
- Use `Optional<T>` for nullable return values; never return `null` from public methods
- Stream API for collection operations; avoid imperative loops where streams are clearer
- Constructor injection for dependencies; avoid field injection (`@Autowired` on fields)

## Error Message Style

- User-facing messages: lowercase, no trailing period, actionable (`"email address is required"`)
- Log messages: sentence case, past tense for events (`"User login failed"`, `"Payment processed"`)
- Never expose internal stack traces or system details in user-facing messages
- Never use error messages as control flow identifiers — use error codes or types

## Logging Style

- Use structured logging (key-value pairs / JSON); never concatenate log strings
- Include context fields: `user_id`, `request_id`, `operation`
- `INFO` for normal flow milestones; `WARN` for degraded but recoverable state; `ERROR` for failures requiring attention
- Never log secrets, PII, or credentials — mask or omit them
