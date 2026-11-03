The client now retries timeouts, connection resets and 502/503/504 responses, but not every call. The full suite passes (25 tests), including the new retry tests. I haven't run it against the real carrier API.

**What changed:**
- The retry is in `ShippingClient._request` (`shipsync/client.py`), so every call goes through it.
- It makes up to 4 attempts. The waits between attempts are 1s, 2s and 4s, using the injected `sleep`, so tests don't actually wait.
- If every attempt fails, you get the same error as before: `ApiError` with the last status, or the transport error. `sync_shipments` therefore behaves as it did.
- 4xx responses are never retried.
- I added 504 to your 502/503 because it's the same kind of gateway blip. Edit `RETRYABLE_STATUSES` if you'd rather not.

**Not every call is retried.** A timeout or reset doesn't tell us whether the carrier already processed the request, so a retry could create a duplicate.
- GETs and `create_shipment` with an `Idempotency-Key` are retried. The sync always sends that key.
- `request_pickup` and `create_shipment` without a key are sent only once.

**Still exposed:** `request_pickup` is the last step of the nightly job, so a blip there will still kill the run. A re-run won't create duplicate shipments, because the sync skips orders that already have one. But it would book a second pickup for any shipments created in that run. If the carrier accepts an `Idempotency-Key` on `/pickups`, we could send one and retry that call too. I didn't add it because I don't know if the API supports it.

I haven't committed anything.