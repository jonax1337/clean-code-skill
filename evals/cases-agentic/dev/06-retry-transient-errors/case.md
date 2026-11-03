# Retrying a flaky carrier API (Python)

Tests whether an agent adds retries to an API client the way a careful engineer would: only transient failures (timeouts, connection errors, 502/503) are retried, 4xx answers and unexpected exceptions are not, the number of attempts is bounded, and the final error is raised with its cause instead of being swallowed. The repository's README documents that `POST /shipments` is only deduplicated when an `Idempotency-Key` is sent and that `POST /pickups` is never deduplicated, so a create without a key and a pickup must not be repeated, while a keyed create may be. The client already takes an injectable `sleep` (used by the label polling), which is where the waits between attempts belong, so tests never really sleep. The change belongs in the client; the sync job, the CLI and the dependency list stay as they are.

## Prompt

The nightly shipment sync has been dying a couple of times a week. It's always the same kind of thing in the logs: a timeout, a connection reset, or the carrier answering 502/503 for a minute. One blip and the whole job is gone, and someone has to re-run it by hand in the morning. Can you make the client retry when that happens? Tests run with `python -m pytest`.
