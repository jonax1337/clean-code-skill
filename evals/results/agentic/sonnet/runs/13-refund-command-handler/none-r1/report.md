I added the `RefundOrder(orderId, amount)` command, and all 27 tests pass, including the new ones. I haven't committed anything.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`. The order's status never changes.
- **Cap on refunds:** the limit is `amountPaid`, not `total`. A customer who paid 80 on a 100 order (say, with a voucher) can get at most 80 back across all refunds. A refund that would go over fails with `INVALID_INPUT`, and the message includes how much has already been refunded.
- **Partial refunds:** these work, and each one is added to `amountRefunded` on the order.
- **Input checks:** the amount is validated like a payment. It must be greater than zero and have at most two decimal places. An unknown order gives `NOT_FOUND`.

The changes are a new `RefundOrder` record and `RefundOrderHandler`, a new `Order.refund(amount)` method, and the handler registered in `OrderServices.createBus`. I also added the command to the README table and noted the cap there. The new tests are in `RefundOrderHandlerTest` and cover:
- partial refunds
- refunds on delivered orders
- the cap measured against `amountPaid`
- the cap across several refunds
- wrong status
- bad amounts
- an unknown order

Nothing stops two refunds from being processed at the same moment. That matches how the other handlers work, since the repository has no locking or versioning.