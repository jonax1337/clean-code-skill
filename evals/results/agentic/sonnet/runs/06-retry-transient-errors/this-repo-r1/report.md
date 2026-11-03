The client now retries timeouts, connection resets and 502/503 responses, so a one-minute carrier blip no longer kills the sync. `python -m pytest` gives 29 passed (22 existing, 7 new test functions). I didn't run the sync against the real carrier.

The change is in `ShippingClient._request` in `shipsync/client.py`:

- **Backoff:** it makes up to 7 attempts, waiting 2, 4, 8, 16, 30 and 30 seconds between them. That is about 90 s in total, which covers the roughly one-minute outages you described. If every attempt fails, the last error is raised as before.
- **What is retried:** `RequestTimeout`, `ConnectionFailed`, and HTTP 502 or 503. Other errors (400, 404, 429, 500, 504) fail immediately, as they did before.
- **What is not retried:** a repeated POST could create a duplicate if the first one actually went through. So only GETs and POSTs that carry an `Idempotency-Key` are retried.
  - `create_shipment` as `sync_shipments` calls it always has a key, so the sync's main write is covered.
  - `request_pickup` has no key and is not retried. If the pickup call fails right at the end of the job, it will still die. To retry it too, you'd need to confirm the carrier accepts an idempotency key on `/pickups` and have the client send one.
- **Label polling:** `wait_for_label` goes through the same retry path.

Retries have no jitter and don't read a `Retry-After` header. For one nightly job that seemed unnecessary, but it's easy to add. The new tests are in `tests/test_client.py`.