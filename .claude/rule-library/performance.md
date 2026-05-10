## Database

- No N+1 queries — never issue DB queries inside a loop; use batch queries or eager loading
- All list/search endpoints must be paginated; default page size ≤ 100, max enforced server-side
- Use cursor-based pagination for large or frequently-updated datasets; offset pagination only for small, stable data
- Add indexes for every foreign key and every column used in a `WHERE` or `ORDER BY` clause
- Measure query execution time in staging before shipping; reject queries over 100ms without a plan

## Caching

- Assign an explicit TTL to every cached value — never cache indefinitely
- Set `Cache-Control` headers on all HTTP responses; use `no-store` for user-specific or sensitive data
- Invalidate caches on write, not on read
- Document what is cached, where, and why in a comment near the cache call

## Async & I/O

- Never block the main thread or event loop with synchronous I/O
- Use `async/await` or non-blocking equivalents for all file, network, and DB operations
- Offload CPU-intensive work (image processing, report generation) to a background job queue

## Request Handlers

- No operation inside a request handler that scales with input size (e.g., looping over unbounded user-supplied lists)
- Enforce request body size limits at the HTTP layer
- Set timeouts on all outbound HTTP calls; never wait indefinitely for an external service

## Frontend

- Code-split at the route level; each route chunk should be loadable independently
- Lazy-load heavy components (charts, rich editors, maps) behind dynamic imports
- Avoid layout shifts — reserve space for async-loaded content
- Minimize bundle size: prefer smaller alternatives, tree-shake unused exports, avoid importing entire libraries for one function

## Measurement

- Add metrics or distributed tracing before making performance changes — establish a baseline first
- Do not optimize without a measured bottleneck; premature optimization adds complexity without proven benefit
