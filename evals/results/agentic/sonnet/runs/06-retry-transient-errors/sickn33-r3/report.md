`ShippingClient` now retries timeouts, connection resets and 502/503/504 responses. A short outage no longer kills the nightly sync. All 22 tests pass, including 7 new ones.

**What it does**
- It makes up to 4 attempts, waiting 1s, 2s, then 4s between them. The settings are `RETRY_MAX_ATTEMPTS`, `RETRY_BASE_DELAY_S` and `RETRYABLE_STATUSES` in `shipsync/client.py`.
- If the last attempt still fails, you get the same exception as before (`ApiError` or the transport error), so the sync fails as it does today.
- Other 4xx and 5xx statuses (404 and so on) are not retried.

**What it retries**
- **GETs:** always.
- **`create_shipment`:** only when an idempotency key is passed. The sync always passes one, so a retry can't create a duplicate shipment.
- **`request_pickup`:** never, because it has no idempotency key. If the first attempt got through but the reply was lost, a retry could book two pickups. If a blip during that last step still fails your nightly runs, the fix is to have the carrier accept an idempotency key on pickups. Tell me if you want that added.

The longest total wait is 7 seconds per call. That's enough for a short blip but not for a carrier that's down for a full minute. If the minute-long 502/503 outages are what's killing you, raise `RETRY_MAX_ATTEMPTS` or the base delay. For example, 6 attempts at a 2s base gives about 62s of waiting.

I haven't committed anything.