# shipsync

Nightly job that books carrier shipments for the day's orders and schedules one pickup for them.

    SHIPSYNC_API_KEY=... python -m shipsync.cli orders.json

`orders.json` is a list of `{"reference": "A-1001", "address": {"name": ..., "street": ..., "city": ...,
"postal_code": ..., "country": ...}}`.

## Layout

- `shipsync/transport.py`: the thin HTTP layer (`Transport.send(Request) -> Response`). `UrllibTransport` is the
  real one; tests use a fake.
- `shipsync/client.py`: `ShippingClient`, one method per carrier endpoint.
- `shipsync/sync.py`: the job itself.
- `shipsync/cli.py`: command line entry point.

## Carrier API

All calls need `Authorization: Bearer <api key>`. Responses of 400 and above become `ApiError`.

| Call | Notes |
| --- | --- |
| `GET /shipments/{id}` | One shipment. |
| `GET /shipments?status=open` | All shipments with that status. |
| `POST /shipments` | Creates a shipment for an order. Every call creates a new shipment, unless the request carries an `Idempotency-Key` header: a repeated key returns the shipment created by the first request instead of creating another one. |
| `POST /pickups` | Books a courier pickup for a list of shipments. Every call books a new pickup, and the carrier ignores `Idempotency-Key` here. |
| `GET /shipments/{id}/label` | `202` while the label is still being rendered, `200` with the label URL when it is ready. |

## Tests

    python -m pytest

The tests use `tests/fakes.py`, a scripted fake transport, and pass a recording `sleep` to the client, so nothing
touches the network or waits.
