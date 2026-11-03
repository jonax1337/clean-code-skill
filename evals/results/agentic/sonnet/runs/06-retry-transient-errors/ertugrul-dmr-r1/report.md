The client now retries transient failures, and all 30 tests pass, including the new retry tests. I haven't run it against the real carrier.

**What gets retried** (in `shipsync/client.py`, inside `_request`):
- **Failures that trigger a retry:** timeouts, connection resets, and 502, 503 or 504 responses. I added 504 myself.
- **Backoff and limit:** the client waits 2, 4, 8, 16, then 32 seconds between attempts, up to 6 attempts. That covers about a minute of 502/503s. If every attempt fails, you get the last error as before.
- **Other errors:** 4xx and 500 are not retried. Those won't fix themselves.

**What deliberately isn't retried**
- **Pickups:** `POST /pickups` is never retried. A timeout or 502 doesn't tell us whether the carrier booked it, and the carrier ignores `Idempotency-Key` there, so a retry could book a second courier. If the pickup call fails, the job still dies, but it dies before any duplicate is booked. Retrying it safely would need a check first, such as listing existing pickups. The carrier API as described in the README has no such call.
- **Shipments without a key:** `POST /shipments` is retried only when it carries an `Idempotency-Key`. `sync_shipments` always sends one, so the nightly job is covered. Calls without a key fail on the first error.

Because the pickup call isn't retried, a blip right at the end of the night can still kill the job. The shipments are already created by then, so the morning re-run skips them and only books the pickup.

I added the tests to `tests/test_client.py`. They cover each failure type, the backoff delays, giving up, the no-retry cases and the idempotency rules.