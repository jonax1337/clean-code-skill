`RefundOrder` is in place and the full suite passes: 29 tests, including 9 new refund tests.

**What changed**
- `RefundOrder.java`: new command record `(orderId, amount)`.
- `RefundOrderHandler.java`: the handler. It checks, in order:
  - orderId is present and amount is positive, at most two decimals (`INVALID_INPUT`)
  - the order exists (`NOT_FOUND`)
  - the status is `SHIPPED` or `DELIVERED` (`INVALID_STATE`)
  - previous refunds plus this one do not exceed `amountPaid` (`INVALID_INPUT`)
  
  On success it records the refund and saves. Status is not touched.
- `Order.java`: added `refund(amount)`, which adds to `amountRefunded`.
- `OrderServices.java`: registered the handler on the bus.
- `RefundOrderHandlerTest.java`: covers shipped and delivered refunds, status unchanged, partial refunds accumulating, the cap at amount paid, rejection for placed, paid-but-unshipped, and cancelled orders, rejection of a non-positive amount, and unknown orders.
- `README.md`: added a `RefundOrder` row and a short note on the rules.

**Choices I made that you may want to change**
- The cap is `amountPaid`, not `total`. An order paid for less than its total (a voucher, per the README) can only be refunded up to what was paid.
- Over-refunds use `INVALID_INPUT`, the same code `PayOrderHandler` uses for "more than the total". Wrong-status refunds use `INVALID_STATE`.
- Refunding exactly the remaining amount is allowed.

**Not covered**
- This only records the refund on the order. It does not call a payment provider or move money. If support expects the customer to be paid back, that integration is still needed.
- I did not commit anything.