I've added the `RefundOrder(orderId, amount)` command with Support's rules. All 29 tests pass, including 9 new ones for refunds.

**How it behaves:**
- **Status check:** only shipped or delivered orders can be refunded. Any other status is rejected with `INVALID_STATE`.
- **The limit:** all refunds of an order together can't be more than what the customer actually paid (`amountPaid`), not the order total. The README says these can differ when a voucher covered part of the order. So if the total is 100.00 and the customer paid 80.00, refunds stop at 80.00.
- **Partial refunds** add up in `amountRefunded`. A refund that would push the sum over the amount paid is rejected with `INVALID_INPUT`, the same code `PayOrder` uses for overpaying. The error message says how much can still be refunded.
- **Amount checks** are the same as for payments: it's required, must be greater than zero, and can have at most two decimal places.
- The order's status doesn't change.

**Changes:**
- New files: `src/main/java/shop/RefundOrder.java` and `RefundOrderHandler.java`, built the same way as the existing handlers.
- `Order.recordRefund(amount)` adds the refund to `amountRefunded`.
- The handler is registered in `OrderServices.createBus`.
- New tests in `src/test/java/shop/RefundOrderHandlerTest.java`. They cover partial, repeated and full refunds, going over the limit, the paid-less-than-total case, wrong statuses, bad amounts and unknown orders.
- `README.md` now lists the command and the refund limit.

Two things to raise with Support:
- **Two refunds at once:** like the other handlers, this one reads the order, checks it and then saves it, with nothing stopping two requests from running at the same time. Two refunds sent together could both pass the check and add up to more than was paid. That doesn't matter for the in-memory repository, but a real database would need something like optimistic locking.
- **Error code:** if Support would rather treat "refund too large" as a business-rule failure than as bad input, it's a one-line change to `INVALID_STATE`.

I haven't committed anything.