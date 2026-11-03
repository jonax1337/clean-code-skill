I added the `RefundOrder(orderId, amount)` command with Support's three rules, and all tests pass.

**How it works** (`src/main/java/shop/RefundOrderHandler.java`):
- **Input:** the order ID can't be blank, and the amount must be positive with at most two decimal places.
- **Unknown order:** fails with `NOT_FOUND`.
- **Status:** only shipped or delivered orders can be refunded. Any other status fails with `INVALID_STATE`.
- **Limit:** the amount can't be more than what was paid minus what has already been refunded. Going over fails with `INVALID_INPUT`, the same code used when a payment is too high.
- **Recording:** the amount is added to the order's `amountRefunded` and the status doesn't change.

**One decision to check:** the cap is the amount the customer paid, not the order total. The README says a voucher can make the paid amount lower than the total, so a 100.00 order paid with 80.00 can be refunded at most 80.00 in total.

**Other changes:**
- `Order.java` has a new `recordRefund(amount)` method that adds to `amountRefunded`.
- The handler is registered in `OrderServices.createBus`.
- The README now lists the command and the refund rule.

**Tests:** I added 8 tests in `RefundOrderHandlerTest`. They cover partial refunds, refunds that add up to exactly the amount paid, going one cent over on a single refund and on a later one (including an amount above what was paid but below the total), a status that isn't allowed, a negative amount, and an unknown order. `java tools/RunTests.java` ran 28 tests and all 28 passed.

I haven't committed anything.