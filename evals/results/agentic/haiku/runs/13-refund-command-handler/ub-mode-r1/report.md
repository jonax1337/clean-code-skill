`RefundOrder(orderId, amount)` is in place and all 30 tests pass (20 existing, 10 new). I did not commit; the changes are in the working tree.

**What it does**
- Only `SHIPPED` or `DELIVERED` orders can be refunded. Other statuses fail with `INVALID_STATE`.
- The refund amount must be positive with at most two decimal places, the same rule `PayOrder` uses.
- Refunds are capped at `amountPaid − amountRefunded`, so several partial refunds can add up to the amount paid but never exceed it. Going over fails with `INVALID_INPUT`, the same code `PayOrder` uses for an amount above the total.
- Each successful refund adds to `amountRefunded` and saves the order. The status does not change.

**Files**
- `src/main/java/shop/RefundOrder.java`: the command record.
- `src/main/java/shop/RefundOrderHandler.java`: validation, status check, cap check, then records and saves.
- `src/main/java/shop/Order.java`: new `recordRefund(amount)` method.
- `src/main/java/shop/OrderServices.java`: registers the handler on the bus.
- `src/test/java/shop/RefundOrderHandlerTest.java`: 10 tests through `CommandBus`, covering the rules above.
- `README.md`: adds a `RefundOrder` row to the command table.

**Choices I made that you may want to change**
- Refunding a `CANCELLED` order is rejected, since Support's rules only allow shipped or delivered orders.
- Over-refunds return `INVALID_INPUT`, not `INVALID_STATE`, to match how `PayOrder` reports an amount that is too large.
- The cap uses `amountPaid`, not `total`, so an order with a voucher can't be refunded beyond what was actually paid.

**Process log**
1. Ran the existing suite as a baseline: 20 of 20 passed.
2. Wrote the refund tests first and confirmed they failed to compile because `RefundOrder` was missing.
3. Added the command, handler, `Order` method, registration, and README row.
4. Re-ran the suite: 30 of 30 pass, with no compiler warnings under `-Xlint:all`.

The ub-mode skill also asks for the crapper, dryer, and mutator tools. I did not run them because they are not available in this environment. The new code has no coverage measurement, and the tests were not checked for surviving mutants.