`RefundOrder` is in place and the suite passes: 30 tests, the 20 existing ones plus 10 new refund tests.

**What it does**

- **Status check:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status, including cancelled, fails with `INVALID_STATE`.
- **Cap:** the refundable amount is `amountPaid - amountRefunded`. A refund above that fails with `INVALID_INPUT`. The cap uses what was paid, not the order total, so an order paid 80.00 on a 100.00 total can only be refunded up to 80.00.
- **Recording:** a successful refund adds to `amountRefunded` and saves the order. The status does not change.
- **Input:** `orderId` must be non-blank and `amount` must be positive with at most two decimal places, using the same `Validator` as `PayOrder`.

**Files**

- `RefundOrder.java`: new command record `(orderId, amount)`.
- `RefundOrderHandler.java`: new handler, same shape as the other handlers.
- `Order.java`: new `recordRefund(BigDecimal)` method next to the `markX` methods.
- `OrderServices.java`: registers the new handler on the bus.
- `RefundOrderHandlerTest.java`: tests for partial and full refunds, accumulation, the cap (including the paid-versus-total case), wrong status, cancelled orders, non-positive amounts and unknown orders.
- `README.md`: added a `RefundOrder` row to the command table.

**Choices you may want to change**

- Over-refunds return `INVALID_INPUT`, matching how `PayOrder` rejects an amount above the total. Wrong status returns `INVALID_STATE`.
- The command only records the refund. The repo has no payment provider, so nothing sends money back to the customer. If that call belongs in this command, it needs a gateway seam that doesn't exist yet.

I did not commit anything.