# Coding Rules

## Dependency Injection

- Every dependency (database, external service, logger, clock, config) is injected from outside — never instantiated inside a function or class
- A function or class that creates its own dependencies cannot be tested without side effects
- Inject at the construction boundary: pass dependencies through constructors, function parameters, or a DI container — not via globals or module-level singletons
- Injectable dependencies are expressed as interfaces, not concrete types — the caller decides the implementation

## Testable Structure

- Write code so it can be tested without real infrastructure (no live DB, no network, no file system) by default
- Pure functions — same input always produces same output, no side effects — are the easiest to test; prefer them for business logic
- Side effects (I/O, state mutation, external calls) are isolated at the edges of the system and injected, not embedded in logic
- If a unit of code cannot be tested without spinning up a server or a database, it has too many responsibilities — split it
- Avoid global state and module-level initialization that runs at import time; both make tests order-dependent and fragile

## Single Responsibility

- A function does one thing; if you need "and" to describe what it does, split it
- A module owns one concept; if it changes for two different reasons, split it
- Orchestration (calling A then B then C) is a separate concern from logic (what A, B, C each do)
- An orchestrating function contains only calls to other functions — no inline logic mixed in; if it does, split the logic into a named function
- If a function body needs a comment to divide it into sections, those sections are separate functions waiting to be extracted

## Explicit Over Implicit

- Make dependencies, side effects, and failure modes visible in the function signature
- A function that can fail returns an error or throws a typed exception — it does not silently return null or swallow the error
- Configuration and environment values are passed in, not read from environment variables buried in logic
- Magic — behavior that changes based on hidden global state — is a bug waiting to happen

## Boundaries and Contracts

- Validate data at the entry boundary of each layer; trust data that has already been validated within the same layer
- The contract between layers is the type/interface — if the type is correct, the implementation can change freely
- Do not leak internal representations across layer boundaries; map explicitly at each crossing
