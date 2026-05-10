## Structure

Use Arrange-Act-Assert in every test:
- Arrange: set up inputs, mocks, and state
- Act: call the function or endpoint under test
- Assert: verify outputs and side effects

## Naming

`test_<function>_<scenario>_<expected_outcome>` — make the failure message self-explanatory without reading the body.

## What to Mock

Mock at system boundaries only:
- External HTTP APIs, payment gateways, email/SMS services → mock
- Internal DB in unit tests → mock the repository interface
- Internal DB in integration tests → use a real test database, never a mock
- Clock/time → inject; never call `Date.now()` or `time.Now()` directly in logic

Never mock the module under test. Never mock to make a test pass.

## Coverage Targets

- Critical paths (auth, payment, data mutation): 90%+ branch coverage
- Overall: 70%+ line coverage
- Coverage numbers are a floor, not a goal — a test that doesn't assert behavior doesn't count

## Test Types

Use the right type for each scenario:

| Type | When to use |
|---|---|
| Unit | Pure functions, business rules, isolated transformations |
| Integration | Service-to-DB, service-to-external-API boundary, message queue |
| E2E | Full user flows through the UI or public API surface |

Prefer unit tests for speed; add integration tests at every external boundary; limit E2E to the top 3–5 critical user journeys.

## Prohibited Patterns

- No snapshot tests — they fail on irrelevant changes and create false confidence
- No `expect(true).toBe(true)` or empty assertions
- No tests that pass when the implementation is deleted
- No `sleep`/`setTimeout` in tests — use proper async primitives or fake timers

## Execution

Run the full test suite after every implementation change. Do not call a task done until all tests pass.
