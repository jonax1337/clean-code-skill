`ShippingClient` now retries timeouts, connection resets and 502/503 responses, so a one-minute carrier blip no longer kills the sync. `python -m pytest` gives 30 passed, including 9 new test functions in `tests/test_client_retry.py`. I haven't run it against the real carrier.

**What gets retried**
- Up to 8 attempts, waiting 1, 2, 4, 8, 16, 30 and 30 seconds between them (about 91 s in total). That's longer than the roughly 60 s outages you described.
- Other errors (400, 404, 500 and so on) are not retried and fail straight away, as before. After the last attempt, the final error is raised.
- Reads (`GET`) are always retried, including the label polling.
- `POST /shipments` is retried because the sync already sends an `Idempotency-Key`. If the first attempt actually went through, the carrier returns that shipment instead of creating a second one. A call without a key is not retried.
- **`POST /pickups` is never retried.** The carrier ignores `Idempotency-Key` there, and a timeout or reset can happen after the pickup was booked. Retrying could book a second courier. A blip during the pickup step will still fail the job. But by then the shipments exist, so a re-run skips them and only creates the pickup, if nothing was created in the first run. If you want that step covered too, it needs a check of whether the pickup already exists, or the carrier needs to support idempotency there. I left that out.

The change is in `shipsync/client.py`, in `_request`.

I didn't add jitter to the delays, since there's only one nightly job calling the carrier. I also left 504 out because you only mentioned 502/503. Adding it is one entry in `RETRYABLE_STATUSES`.