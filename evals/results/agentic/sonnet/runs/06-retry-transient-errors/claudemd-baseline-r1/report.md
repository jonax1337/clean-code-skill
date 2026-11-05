The client now retries timeouts, connection resets and 502/503/504 responses. The full suite passes (26 tests, run after my last edit).

**What it does** (`shipsync/client.py`)
- Each request gets up to 4 tries. It waits 1s, 2s, then 4s between them, using the injected `sleep`, so the tests don't actually wait.
- If every try fails, you get the original `ApiError` or `TransportError`, so the sync job fails as it did before. It just takes four attempts to get there.
- Other 4xx and 5xx responses (404, 500 and so on) are not retried.

**Which calls retry**
- **GETs:** these retry, including the label polling.
- **`create_shipment`:** it retries only when it has an idempotency key. The nightly sync always passes one, so the job is covered.
- **`request_pickup`:** it does not retry. It has no idempotency key, and a timeout or 502 can mean the carrier already booked the pickup. A blind retry could book it twice. If pickup failures are part of what's killing the job, the fix is for the carrier to accept an idempotency key there. I can add that if it does.

I added tests for each of these cases in `tests/test_client.py`. I only ran them against the fake transport, not the real carrier API.