The client now retries timeouts, connection resets and 502/503/504 responses. The full suite passes (25 tests), including the new retry tests. I haven't run it against the real carrier API.

**How it behaves** (in `shipsync/client.py`, inside `_request`, so every call gets it):
- **Attempts:** up to 6 per request, with waits of 2, 4, 8, 16 and 32 seconds between them. That's about 62 seconds in total, enough to outlast a minute-long outage.
- **Final failure:** if the last attempt still fails, the original `ApiError` or transport error is raised as before, so the job fails the same way it does today.
- **Not retried:** 4xx responses such as 404 fail immediately.
- **504:** I added it alongside 502 and 503, since it is the same kind of gateway blip.

**POST requests:** a retried POST can create a duplicate if the first attempt actually went through before the connection dropped. So POSTs are only retried when they carry an `Idempotency-Key`, and GETs are always retried.
- **`create_shipment`:** the nightly sync always sends the key, so it is protected.
- **`request_pickup`:** it has no key, so it is not retried, and a blip there still kills the job. To cover it, we'd need to know whether the carrier accepts an idempotency key on `/pickups`. If it does, it's a small change. Do you know?

I added the retry tests to `tests/test_client.py`. They cover each failure type, the backoff schedule, giving up after the last attempt, 4xx not being retried, and the POST rules above.