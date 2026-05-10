## Metrics: RED Method

Instrument every service using the RED method:

| Metric | What to measure | Example |
|---|---|---|
| **Rate** | Requests per second | `http_requests_total{service, method, status}` |
| **Errors** | Failed requests per second | `http_errors_total{service, method, error_code}` |
| **Duration** | Latency distribution (P50, P95, P99) | `http_request_duration_seconds{service, method}` |

Additional required metrics:
- Saturation: CPU %, memory %, queue depth, connection pool usage
- Business events: orders placed, users registered, payments processed
- External dependency health: DB query latency, downstream service latency, error rates

## SLO / SLI Definitions

Define SLOs before writing alerting rules.

| Term | Definition | Example |
|---|---|---|
| **SLI** | The specific metric being measured | 99th-percentile latency of `/api/checkout` |
| **SLO** | The target value for the SLI | P99 latency < 500ms over a 28-day window |
| **Error Budget** | Allowed failure headroom (1 - SLO) | 1% of requests may exceed 500ms |

Rules:
- Define at least one latency SLO and one availability SLO per user-facing service
- SLOs must be agreed with product stakeholders — do not set them unilaterally
- Alert when error budget burn rate exceeds 2× (fast burn) or 0.1× sustained (slow burn)

## Alert Design

- **Page only when a human must act immediately** — alert fatigue kills on-call effectiveness
- Every alert must have a runbook link in the alert description
- Alert on symptoms (user impact), not causes (high CPU)
- Alert thresholds:

| Priority | Condition | Response |
|---|---|---|
| P1 (page) | Availability < 99% or P99 > 3× SLO | Immediate; wake on-call |
| P2 (notify) | Error budget burn rate > 2× for 1 hour | Respond within 4 hours |
| P3 (ticket) | Slow trend degradation | Schedule fix within the sprint |

## Dashboard Structure

Organize dashboards in three layers:

1. **Overview dashboard** — service health at a glance: availability, error rate, P99 latency, active alerts
2. **Service dashboard** — per-endpoint RED metrics, dependency health, queue depths
3. **Component dashboard** — infrastructure detail: DB connection pools, cache hit rates, JVM/GC stats

Rules:
- Time range default: 1 hour; allow switching to 24h / 7d / 28d
- Use the same color conventions across all dashboards: green = healthy, yellow = degraded, red = failing
- Dashboard-as-code: store dashboard definitions in the repo alongside the service code

## Incident Response

1. **Detect** — alert fires; on-call acknowledges within 5 minutes
2. **Assess** — determine user impact (who is affected? how many? how badly?)
3. **Communicate** — post status update within 10 minutes of detection; update every 30 minutes
4. **Mitigate** — restore service (rollback, feature flag, scaling) before root cause analysis
5. **Resolve** — root cause fixed; monitor for 30 minutes before closing the incident
6. **Post-mortem** — blameless post-mortem within 5 business days; include timeline, root cause, and action items

Incident severity levels:
- **SEV1**: full outage or data loss; all hands; CEO-level communication
- **SEV2**: major feature unavailable; on-call + lead engineer
- **SEV3**: degraded performance; on-call handles; notify team async
