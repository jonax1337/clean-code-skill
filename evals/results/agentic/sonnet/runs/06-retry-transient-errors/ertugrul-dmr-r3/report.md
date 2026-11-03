The client now retries transient failures. All 25 tests pass, including the new retry tests.

**What changed (`shipsync/client.py`)**
- A request is attempted up to 4 times (`MAX_ATTEMPTS`). Between attempts it waits 1s, 2s, then 4s (`RETRY_BASE_DELAY_S`).
- It retries on timeouts, connection resets, and HTTP 502, 503 and 504. I added 504 because it is the same kind of gateway blip.
- Other errors, such as a 404 or 400, fail immediately. If the last attempt still fails, you get the original error, so the sync's existing `ApiError` handling is unchanged.

**What is not retried**
- **`request_pickup`:** it sends no idempotency key. A timeout or 503 doesn't tell us whether the carrier already booked the pickup, so a retry could book it twice. It still fails on the first error.
- **`create_shipment` without a key:** it is not retried, for the same reason. `sync_shipments` always passes a key, so the nightly job gets retries on creates.
- **Who retries:** GETs and any POST that has an `Idempotency-Key` are retried.

The pickup is the one place a blip can still kill the job. Retrying it safely needs an idempotency key on `request_pickup`. That is a small change if the carrier supports it, but I didn't want to guess at that.

**Backoff and the job's runtime**
Backoff uses the existing injected `sleep`, so tests don't wait. In the worst case a single call now adds 7 seconds of waiting on top of the request timeouts.

I haven't committed anything.