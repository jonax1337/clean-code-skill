I added the `RefundOrder(orderId, amount)` command. All 27 tests pass (`java tools/RunTests.java`), including 7 new ones for refunds.

**What changed**
- `RefundOrder.java`: the new command record.
- `RefundOrderHandler.java`: the handler, written like the other handlers. It checks the input, looks up the order, then applies the rules:
  - The order must be `SHIPPED` or `DELIVERED`. If not, it returns `INVALID_STATE`.
  - The refund can't be more than `amountPaid − amountRefunded`. That means all refunds together can never go over what the customer actually paid. The limit is the amount paid, not the order total, because a voucher can cover part of the total. If the refund is too big, it returns `INVALID_INPUT`, the same code `PayOrder` uses for paying too much.
  - On success, the amount is added to `amountRefunded` and the order's status doesn't change.
- `Order.recordRefund(amount)`: adds the refund to `amountRefunded`.
- `OrderServices.createBus`: registers the new handler.
- `README.md`: a new row in the command table and a sentence on the refund limit.
- `RefundOrderHandlerTest.java` covers:
  - a partial refund of a shipped order
  - several refunds adding up to the full amount paid on a delivered order
  - a refund rejected for being above the amount paid but below the total
  - a refund rejected because it plus earlier refunds would go over the amount paid
  - a refund rejected because the order wasn't shipped yet
  - an invalid amount
  - an unknown order

**Not covered:** two refunds for the same order arriving at the same moment could both pass the check and together go over the limit. The other commands have the same gap, since the repository has no locking or version check. If refunds can come in concurrently in production, it should be handled in the repository.