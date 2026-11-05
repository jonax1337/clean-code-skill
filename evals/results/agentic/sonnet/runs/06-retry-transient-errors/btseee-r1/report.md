The client now retries timeouts, connection resets and 502/503/504 responses. It does this only where a repeat can't cause damage. All 27 tests pass, including the new retry tests, but I haven't run it against the real carrier API.

**What retries:**
- **Attempts and waits:** each call gets up to 4 attempts, waiting 1s, 5s, then 20s between them. If the last attempt still fails, the original error is raised as before.
- **Not retried:** other statuses such as 400, 404 and 500 fail immediately.
- **Where the code is:** the retry logic is in `ShippingClient._request` in `shipsync/client.py`, and the README has a short note on it.

**Which calls retry:**
- **Reads:** `GET`s retry. This includes label polling.
- **Creating a shipment:** `create_shipment` retries only when it carries an `Idempotency-Key`. The sync job always sends one, so it is covered. Without a key, a lost response followed by a retry could create a duplicate shipment.
- **Pickups:** `request_pickup` never retries. The carrier ignores idempotency keys on `/pickups`, so a timeout after the carrier had already booked the pickup would book a second courier. If the pickup call fails, the job still dies, but it can't double-book.

**Things to know:**
- I added 504 to the 502/503 you mentioned, since it's the same kind of gateway blip. It's one entry in `RETRYABLE_STATUSES` if you'd rather drop it.
- The backoff is about 26s in total. That covers short blips but not a carrier outage lasting several minutes. If the "502/503 for a minute" cases are longer than that, lengthen `RETRY_BACKOFF_S`.
- If the pickup call fails, nothing retries it. A re-run after a failed pickup would skip the shipments already created and book no pickup for them. I left that alone, but it may be worth a follow-up.