The client now retries timeouts, connection resets and 502/503 responses. I added tests for it in `tests/test_client.py`, and the full suite passes (26 tests). I committed it as `a0c26a1`, but didn't push because the repo has no remote configured.

**How it behaves** (`shipsync/client.py`)
- **Attempts and waits:** each request gets up to 6 attempts. The waits between them are 2, 4, 8, 16 and 32 seconds, about 62 seconds in total, so a one-minute carrier outage is covered. The numbers are constants at the top of the file if you want to change them.
- **Final failure:** if the last attempt also fails, you get the original error: `ApiError` with the 502/503 status, or the timeout or connection error. The sync's existing handling of 5xx errors still applies.
- **4xx responses:** these are never retried.
- **Label polling:** each label check is retried the same way. A 202 "not ready yet" reply still follows the existing polling logic.

**One thing you might not expect:** the pickup booking (`request_pickup`) is deliberately not retried. It's a POST with no idempotency key. If the first attempt reached the carrier but the response was lost, a retry could book the pickup twice. The same goes for `create_shipment` when no key is passed. The sync always passes a key for `create_shipment`, so those calls are retried safely.

That does leave one gap: if the pickup call fails, the job still dies at the end and needs a manual re-run. Closing it means giving pickups an idempotency key, which depends on whether the carrier API supports one on `/pickups`. I haven't checked that.