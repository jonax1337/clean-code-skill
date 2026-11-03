The client now retries timeouts, connection errors and 502/503/504 responses, and all 26 tests pass, including the new ones. I haven't run the nightly job against the real carrier.

- **Retry behaviour:** a call is tried up to 4 times, waiting 1s, then 2s, then 4s between attempts. After the last attempt the original error is raised as before. 4xx responses fail straight away. The change is in `shipsync/client.py`. I added 504 to the 502/503 you mentioned, since it's the same kind of gateway blip.
- **`POST /shipments`:** it is only retried when it carries an `Idempotency-Key`. The nightly sync always sends one, so it gets the retries. A call without a key would create a duplicate shipment if the first attempt actually went through, so it isn't retried.
- **`POST /pickups`:** it is never retried. The README says the carrier ignores idempotency keys there, so a retry could book a second pickup. If the pickup call is what dies, the job will still fail at that step. Making that safe needs a check on the carrier side first, such as listing existing pickups before booking again.
- **Tests and README:** the new tests are in `tests/test_client.py`. They cover the retries, the attempt limit, and the cases that must not be retried. I added a short "Retries" section to the README.

I haven't committed anything.