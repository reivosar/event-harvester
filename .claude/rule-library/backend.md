# Backend Design Rules

## Business Logic Belongs in the Service Layer

- Controllers/handlers handle only HTTP concerns: parse input, call a service, format the response
- Business rules (calculations, workflows, eligibility, state transitions) live in the service/domain layer
- A controller that contains an `if` checking a business condition is doing too much
- The service layer must be callable without HTTP — it knows nothing about request/response objects

## Dependency Direction

- Outer layers depend on inner layers; inner layers never depend on outer layers
- Direction: handler → service → repository → database; never the reverse
- The service layer does not import from the HTTP framework, the database driver, or external SDKs directly
- Infrastructure (DB, email, storage, queues) adapts to the domain through interfaces — the domain does not adapt to infrastructure

## Data Transformation at the Boundary

- Raw input (HTTP request, message body) is validated and mapped to domain objects at the entry boundary
- Internal domain models never leak into API responses — map to response DTOs at the exit boundary
- If the DB schema changes, only the repository layer changes; services are unaffected
- If the API contract changes, only the controller layer changes; services are unaffected

## Layering Responsibilities

- **Handler/Controller**: authenticate, validate input shape, call one service method, map result to response
- **Service/Use Case**: business logic, orchestration of repositories and external adapters, transaction boundary
- **Repository**: data access only — no business logic, no HTTP concerns
- **Domain Model**: entities and value objects expressing business concepts — no framework dependencies

## Domain-Driven Source Organization

- Organize source code by domain (e.g. `users/`, `orders/`, `billing/`), not by technical layer (e.g. `controllers/`, `services/`, `models/`)
- Each domain owns its handlers, services, repositories, and models — all co-located under its directory
- A domain's internal files are private; only explicitly exported interfaces, query functions, and events are accessible to other domains
- Design each domain so it could be extracted into a separate service without restructuring — avoid assumptions that domains share a process or a database forever

## Cross-Domain Data Access

- A domain never reads another domain's database tables or internal repositories directly
- Cross-domain data access goes through the owning domain's published query interface (a service method, a query function, or a read model)
- The consuming domain depends on the interface, not the implementation — the owning domain can change its storage freely
- If a domain frequently needs data from another domain, consider whether an event-driven approach (the owning domain publishes events, the consumer maintains a local read model) is more appropriate than synchronous queries
- Circular dependencies between domains are a design error — resolve by extracting a shared domain or inverting the dependency through events

## Transaction Boundaries

- A single service method represents a single unit of work — it either fully succeeds or fully rolls back
- Transactions are managed at the service layer, not in the repository or controller
- Never spread a transaction across multiple service calls — caller cannot know what to roll back

## External Dependencies Through Interfaces

- External services (email, payment, storage, push notifications) are accessed through interfaces defined by the domain
- The service layer depends on the interface; the concrete implementation is injected
- This keeps business logic testable and allows swapping implementations without touching service code
- Never call an external service SDK directly from a service — wrap it in an adapter

## Zero Trust — Never Trust Request Content

- Every request is untrusted by default, regardless of origin — internal services, authenticated users, and trusted IPs are not exceptions
- Validate all input at every layer independently; do not assume upstream validation was correct or complete
- Never use client-supplied values to construct queries, file paths, shell commands, or redirect URLs without strict validation and sanitization
- Never trust client-supplied IDs to determine ownership — always verify that the authenticated user has permission to access the requested resource
- Reject requests that contain unexpected fields, malformed data, or values outside defined ranges; do not silently ignore them
- Never rely on a single security check — apply defense in depth: validate at the boundary, enforce authorization in the service, and constrain at the data layer
- Treat data from your own database as untrusted when it will be rendered or executed — stored XSS, second-order injection, and deserialization attacks originate from trusted storage
- Secrets (tokens, keys, passwords) in a request body or header must be treated as potentially compromised — rotate on any suspicion, do not log them

## Authentication and Authorization

- Authentication (who is this?) is handled at the middleware layer before the handler is reached
- Authorization (can they do this?) is checked at the start of the service method, before any business logic runs
- Services assume the caller is authenticated — they do not re-verify identity
- Permission checks are explicit and close to the operation they protect, not buried in business logic

## API Contract Design

- APIs are designed for consumers, not for internal convenience
- Request and response shapes are stable contracts — internal refactoring must not change them
- Breaking changes require versioning; additive changes (new optional fields) are non-breaking
- Internal domain concepts (table names, internal IDs, implementation details) do not appear in the API

## Error Design

- Domain errors are first-class: define specific error types for each failure mode (NotFound, Conflict, Unauthorized)
- The controller maps domain errors to HTTP status codes — the service does not know about HTTP
- Infrastructure errors (DB failure, network timeout) are caught, logged in full, and wrapped into safe domain errors before propagating
- Never let a raw database error or stack trace reach the API response

## State Transitions

- Mutating operations must validate that the current state permits the transition before executing
- Illegal state transitions are rejected with a domain error, not silently ignored or partially applied
- Side effects (emails, events, notifications) triggered by a state change happen after the transaction commits, not inside it

## External System Connections

- Treat every external system (database, cache, third-party API, internal service, message broker) as unreliable by default — it can be slow, unavailable, or return unexpected errors at any time
- Every call to an external system must have retry logic; absence of retry is a design defect, not an acceptable default
- Retry only on transient failures (network timeout, connection refused, 429, 503) — never retry on permanent failures (400, 401, 403, 404, 422)
- Use exponential backoff with jitter on all retries; tight retry loops amplify load on an already struggling system
- Set a maximum retry count and a total timeout budget — unbounded retries cause cascading failures across the call chain
- Log each retry attempt with the failure reason and attempt number; silent retries make incidents invisible

## Idempotency and Retry Safety

- Classify every write operation as idempotent or non-idempotent before designing it
- GET, DELETE, and PUT must be idempotent by design — repeating them produces the same result
- POST operations that create resources should accept a client-supplied idempotency key to allow safe retries
- Non-idempotent operations (charge a card, send an email, publish an event) must not be retried without deduplication — use idempotency keys or at-least-once delivery with dedup logic

## Resilience

- Every call to an external service (DB, cache, third-party API, internal microservice) has a defined timeout — never rely on the default
- Design for partial failure: if a non-critical dependency is unavailable, degrade gracefully rather than failing the entire request
- Apply the circuit breaker pattern for external dependencies that are prone to prolonged failure — fail fast instead of accumulating waiting threads
- Distinguish between read and write paths: read degradation (stale cache, reduced data) is often acceptable; write degradation must be explicit and safe
- Isolate failure domains — a failure in one subsystem (search, notifications, analytics) must not propagate to core workflows
- When a operation cannot complete due to a transient failure, return a retriable error code (503 with Retry-After) so callers know they can try again safely
