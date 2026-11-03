`RefundOrder` is in place and all 31 tests pass, including 11 new ones for the refund handler. I haven't committed anything.

**What changed**
- `RefundOrder.java`: the command record, `(orderId, amount)`.
- `RefundOrderHandler.java`: the handler, which applies Support's rules in this order:
  1. Validates input (non-blank id, positive amount with at most two decimals).
  2. Returns `NOT_FOUND` for an unknown order.
  3. Returns `INVALID_STATE` unless the order is `SHIPPED` or `DELIVERED`.
  4. Returns `INVALID_INPUT` if the amount is more than `amountPaid - amountRefunded`.
  5. Otherwise adds the amount to `amountRefunded` and saves. The status is not touched.
- `Order.java`: a new `recordRefund(amount)` method that only increases `amountRefunded`.
- `OrderServices.java`: registers the new handler on the bus.
- `README.md`: adds the command to the table and states the rules.
- `RefundOrderHandlerTest.java`: covers partial and full refunds, delivered orders, cumulative refunds, the cap, the boundary at the exact remaining amount, wrong statuses, zero amounts and unknown orders.

**Choices I made**
- The cap is based on `amountPaid`, not `total`. Support said "what the customer actually paid", and the README says paid can be lower than total.
- An over-refund returns `INVALID_INPUT`, matching how `PayOrder` rejects an amount over the total. A wrong status returns `INVALID_STATE`.

**Not covered**
- Nothing here talks to a payment provider. This only records the refund on the order, as you asked.
- Two refunds submitted at the same time could both pass the cap check. The in-memory repository has no concurrency control, so this matters only once a persistent repository exists.