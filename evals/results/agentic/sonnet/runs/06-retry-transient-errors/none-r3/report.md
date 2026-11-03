The client now retries timeouts, connection resets and 502/503/504 responses, and all 22 tests pass, including 7 new ones. I haven't committed anything.

- **What gets retried:** `ShippingClient._request` in `shipsync/client.py` makes up to 5 attempts. It waits 1, 2, 4 and 8 seconds between attempts, using the client's existing injectable `sleep`. After the last attempt, the original error is raised as before.
- **404 and other 4xx:** these are not retried.
- **What gets retried safely:** GET requests, and POSTs that carry an `Idempotency-Key`. Without a key, retrying a POST after a timeout could create a duplicate on the carrier's side. `sync_shipments` already sends a key on every `create_shipment`, so shipment creation is covered.
- **Pickup booking:** `request_pickup` has no idempotency key, so it is not retried. A blip there will still fail the nightly job, and it's the last step. Retrying it could double-book a pickup, since a timeout doesn't tell us whether the carrier received it. If the carrier supports idempotency keys on `/pickups`, adding one would let it retry too. I can do that if you tell me it does.
- **504:** I added it alongside the 502 and 503 you mentioned, since it's the same kind of gateway failure.

The backoff totals about 15 seconds, which may be too short for a carrier outage that lasts a minute. If so, raise `MAX_ATTEMPTS` or `RETRY_BASE_DELAY_S` at the top of `client.py`.