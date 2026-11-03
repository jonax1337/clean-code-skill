`RefundOrder(orderId, amount)` is in place and registered on the bus. The full suite passes: 31 tests, 20 existing plus 11 new. I haven't committed anything.

**What changed**
- `RefundOrder.java`: new command record.
- `RefundOrderHandler.java`: the handler. It applies the rules in this order:
  1. The order must exist (`NOT_FOUND`).
  2. The order must be `SHIPPED` or `DELIVERED` (`INVALID_STATE`).
  3. The amount must be positive with at most two decimal places (`INVALID_INPUT`, via the existing `Validator`).
  4. The amount must not exceed `amountPaid - amountRefunded` (`INVALID_INPUT`).
- `Order.java`: new `refund(amount)` method that adds to `amountRefunded`. Status is not touched.
- `OrderServices.java`: registers the handler.
- `README.md`: adds a `RefundOrder` row to the command table and a line on the cap.
- `RefundOrderHandlerTest.java`: covers partial refunds, status staying the same, the non-shipped/placed/cancelled rejections, the exact-amount boundary, the cumulative cap, the voucher case, zero/negative/over-precision amounts, and unknown orders.

**Choices I made that you may want to change**
- **The cap uses `amountPaid`, not `total`.** That is what the customer actually paid. For an order with a voucher, a refund above the amount paid is rejected even though it is below the total.
- **Over-cap refunds return `INVALID_INPUT`.** `PayOrder` uses the same code when a payment exceeds the total. If you would rather treat it as a state problem, change that one code.
- **Refunds are not idempotent.** Each call adds to the total, so a retry after a timeout will refund twice. Support didn't mention this. If you want a request ID, that's a separate change.
- **I did not add a payment-provider call.** The command only records the refund on the order, as you asked. Money has to move somewhere else.