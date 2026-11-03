The client now retries timeouts, connection resets and 502/503/504 responses, and all 25 tests pass, including the new retry tests. I haven't run it against the real carrier API.

The change is in `ShippingClient._request` in `shipsync/client.py`. It makes up to 5 attempts and waits 2, 4, 8 and 16 seconds between them, about 30 seconds in total. That should cover a minute-long blip only partly, so raise `MAX_ATTEMPTS` or `RETRY_BACKOFF_S` if your outages usually last the full minute. If every attempt fails, you get the last error as before. 4xx responses are never retried.

**What gets retried:**
- **GET requests:** always retried, since repeating them is harmless.
- **`create_shipment`:** retried only when it carries an idempotency key. The sync always sends one (`order-<ref>`), so the nightly job is covered. Without a key, a timeout could mean the carrier created the shipment anyway, and a retry would create a duplicate.
- **`request_pickup`:** not retried, because it has no idempotency key and a retry could book the pickup twice. A blip there will still fail the job, but only after all shipments are created. Re-running is safe, because the sync skips orders that already have a shipment. It would also re-book a pickup for the orders that were created before the failure. If the carrier supports an idempotency key on `/pickups`, adding one would let us retry it as well. I didn't change that without knowing the API.

I added 504 to your list of 502 and 503 because it's the same kind of gateway failure.