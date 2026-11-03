The client now retries transient failures, and the full suite passes (25 tests, 9 of them new). I haven't run it against the real carrier API. The change is in `shipsync/client.py`, inside `ShippingClient._request`, so every call goes through it.

**What gets retried**
- **Failures:** timeouts, connection resets and HTTP 502/503/504 responses. I added 504 because it usually comes from the same gateway trouble as 502 and 503.
- **Attempts:** up to 4 in total, waiting 1s, 2s, then 4s between them (about 7s of waiting). If the last attempt still fails, the original error is raised as before, so a real outage still fails the job.
- **Not retried:** other 4xx and 5xx responses fail immediately, as they did before.

**What is deliberately not retried**
- **Keyed creates:** `create_shipment` with an idempotency key is retried. The sync always passes one, so a retry can't create a duplicate.
- **Unkeyed writes:** `create_shipment` without a key and `request_pickup` get one attempt. A timeout there doesn't tell us whether the carrier already acted, so a retry could book a second pickup.

**Remaining gap**
- **Pickup booking:** `request_pickup` is the last step of the sync. If the carrier blips at that moment, the job will still die. Fixing that needs either an idempotency key on the pickup call, if the carrier supports one, or a check for an existing pickup before retrying. I left it alone because it changes how the carrier API is called. Say if you want it.
- **Tuning:** the attempt count and delays are the constants `MAX_ATTEMPTS` and `RETRY_BASE_DELAY_S` at the top of `client.py` if you want to change them.