I added `RefundOrder` to the order service. All 27 tests pass, including 7 new ones for the refund rules.

**What changed**
- `RefundOrder.java`: new command record with `orderId` and `amount`.
- `RefundOrderHandler.java`: the handler. It applies the rules in this order:
  - The order must exist (`NOT_FOUND`).
  - The order must be `SHIPPED` or `DELIVERED` (`INVALID_STATE`).
  - The amount must be positive with at most two decimals, and the order ID must be present (`INVALID_INPUT`).
  - The amount must not exceed `amountPaid - amountRefunded` (`INVALID_INPUT`). The check uses what the customer paid, not the order total, so an order paid for less than its total can't be refunded up to the total.
- `Order.java`: new `refund(amount)` method that adds to `amountRefunded`. The status is not touched.
- `OrderServices.java`: registers the handler with the bus.
- `README.md`: adds a `RefundOrder` row to the command table.
- `RefundOrderHandlerTest.java`: covers full and partial refunds, shipped and delivered orders, several refunds adding up, over-refund rejection, the paid-versus-total case, wrong status, and unknown orders.

**Choices I made that you may want to change**
- Over-refunding returns `INVALID_INPUT`, the same code `PayOrder` uses for an amount above the total. A different code would be a one-line change.
- The refund check and the save are not atomic. The in-memory repository doesn't need that, but a database-backed repository would need a transaction or a conditional update to stop two concurrent refunds from both passing the check.

I haven't committed anything.