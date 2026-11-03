The client now retries timeouts, connection failures and 502/503/504 responses. `python -m pytest` gives 30 passed, with the new retry tests included. I haven't run it against the real carrier.

- **Backoff:** a request gets up to 5 attempts, waiting 5, 10, 20 and 40 s between them. That's about 75 s of waiting, so a one-minute carrier outage should now be survived. If every attempt fails, the last error is raised as before (`ApiError` or the transport error).
- **Other statuses:** 4xx and 500 are not retried.
- **Which requests retry:**
  - GETs always retry.
  - `POST /shipments` retries because the sync already sends an `Idempotency-Key`. A repeat can't create a duplicate.
  - `POST /pickups` is sent only once. The carrier ignores idempotency keys there, so a retry after a timeout could book a second pickup.

The pickup is the last step of the job. If the carrier hiccups at that moment, the job still fails and someone has to re-run it. A re-run is safe: shipments that already exist are skipped, and a new pickup is booked only for shipments the re-run creates itself. If you want pickups retried too, retry only on 502/503/504 and accept the small double-booking risk.

The change is in `shipsync/client.py`. The new tests are in `tests/test_client.py`, and I added a short Retries section to the README. I haven't committed anything.