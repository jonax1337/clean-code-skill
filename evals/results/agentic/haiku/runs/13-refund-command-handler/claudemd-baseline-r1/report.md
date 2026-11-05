`RefundOrder(orderId, amount)` is in place and enforces all three of Support's rules. The full suite passes: 31 tests, the 20 existing ones plus 11 new ones. I haven't committed anything.

**What changed**
- **`RefundOrder.java`** (new): the command record.
- **`RefundOrderHandler.java`** (new): validates the input, then:
  - Rejects any status other than `SHIPPED` or `DELIVERED` with `INVALID_STATE`.
  - Rejects an amount above `amountPaid − amountRefunded` with `INVALID_INPUT`. The message gives the amount still refundable.
  - Otherwise adds the amount to `amountRefunded` and saves. The status is not touched.
- **`Order.java`**: a new `refund(amount)` method, the only place `amountRefunded` changes.
- **`OrderServices.java`**: registers the handler on the bus.
- **`README.md`**: adds a row to the command table.
- **`RefundOrderHandlerTest.java`** (new): covers shipped and delivered refunds, status unchanged, partial refunds adding up, refunding exactly the remaining amount, and rejecting an over-refund. It also covers placed, paid-only, and cancelled orders, a non-positive amount, and an unknown order.

**Choices I made**
- The cap is based on `amountPaid`, not `total`. An order that was paid 80 on a 100 total can be refunded at most 80 in total.
- Wrong status is `INVALID_STATE`. Over-refund and bad amount are `INVALID_INPUT`, matching how `PayOrder` reports amount problems.

**Not covered**
- The in-memory repository has no locking, the same as the other handlers. Two refunds dispatched at the same time could both pass the cap check. That's fine for the current in-memory setup, but a database-backed repository would need a transactional check or a lock before this goes to production.