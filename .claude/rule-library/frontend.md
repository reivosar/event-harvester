# Frontend Design Rules

## Business Logic Does Not Belong in the Frontend

- Business rules (pricing, eligibility, validation logic, workflows) live on the server — the frontend only renders results
- If the frontend duplicates a business rule, it will diverge from the server and cause inconsistency
- Acceptable in the frontend: UI validation (is this field empty?), display formatting, UX flow — nothing that affects data integrity

## No Direct Connection to Infrastructure

- Components never call APIs directly — all network access goes through an abstraction layer (hooks, service modules)
- No hardcoded URLs, endpoint paths, or environment-specific values in components
- No SDK clients (axios instances, GraphQL clients, WebSocket connections) instantiated inside components
- Connection details are configured once at the application boundary, not scattered through the component tree

## Dependency Direction

- Components depend on abstractions (hooks, interfaces), not on concrete implementations
- A UI component must not import from an API client, a store implementation, or another feature's internals
- Features are independent modules — cross-feature dependencies go through a shared layer, never direct imports
- The direction is always: page → feature → component → hook → service; never the reverse

## Data Transformation at the Boundary

- Raw API responses are transformed into view models at the data layer, before entering the component tree
- Components work with clean, typed, display-ready data — never with raw API shapes
- If the API schema changes, only the transformation layer changes; components are unaffected

## Component Responsibility

- A component does one thing: either composes layout/UI, or manages state and data — not both
- Presentational components receive props and render; they have no knowledge of where data comes from
- If a component has more than one reason to change, split it
- Reusable components have no dependency on application-specific context (routing, auth, global store, feature state)

## Component Boundaries

- Split when: a piece of UI is reused, a section has independent loading/error state, or a component has multiple concerns
- Do not split prematurely — duplication is preferable to a premature abstraction
- Group by feature, not by file type; co-locate everything a feature needs

## State Design

- State lives as close to where it is used as possible; lift only when genuinely shared
- Server state is managed by a data-fetching layer (React Query, SWR, etc.) — not duplicated in local state
- Derived values are computed, not stored; storing derived state introduces sync bugs
- Global state is for truly cross-cutting concerns (auth session, theme, locale) — not a dumping ground for convenience

## Data Flow

- Data flows down through props; events flow up through callbacks
- Side effects belong in hooks or effect layers — never in render functions or event handlers beyond triggering them
- Navigation decisions belong in the routing layer, not inside components

## Authentication & Authorization

- Components do not check auth state or permissions directly
- Access control is enforced at the routing layer or via guard components — not scattered in individual components
- A component that renders conditionally based on auth is a presentation concern; a component that redirects is an auth concern — keep them separate

## Error & Loading Design

- Every async boundary has three explicit states: loading, error, success
- Empty state is a distinct case — design it explicitly, not as a fallback of loading
- Errors must be catchable at a defined boundary (error boundary or equivalent); uncaught errors must not crash the whole page
- Error states must offer a recovery path where possible (retry, go back, fallback content)

## Feature Independence

- A feature owns its own components, hooks, and state — nothing leaks out unless explicitly exported
- Features do not reach into each other's internals
- Shared UI goes into a common component library; shared logic goes into shared hooks or utilities
