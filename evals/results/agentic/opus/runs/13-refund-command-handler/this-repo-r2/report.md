I added the `RefundOrder(orderId, amount)` command and it's registered in `OrderServices.createBus`. I ran `java tools/RunTests.java` and all 29 tests passed, 9 of them new.

**What it does** (`RefundOrderHandler.java`, built the same way as the other handlers):
- **Input check:** the order ID must not be blank and the amount must be positive with at most two decimal places, the same check payments use. A bad amount fails with `INVALID_INPUT`.
- **Unknown order:** fails with `NOT_FOUND`.
- **Status:** only shipped or delivered orders can be refunded. Any other status fails with `INVALID_STATE`.
- **Limit:** a refund is rejected with `INVALID_INPUT` if it is more than the amount paid minus what has already been refunded. The README says the amount paid can be lower than the order total (for example when a voucher covered part of it), so the limit is the amount paid, not the total. On a €100 order where the customer paid €80, refunds stop at €80.00 in total.
- **Recording:** a new `Order.recordRefund(amount)` adds the amount to `amountRefunded`. The status doesn't change.

**Tests** (`RefundOrderHandlerTest.java`) use an order with a €100 total and €80 paid. They cover:
- a partial refund on a shipped order, and a refund on a delivered order, both keeping their status
- two refunds that add up to exactly €80.00 (accepted)
- €50.00 followed by €30.01 (rejected, and the stored refund stays at €50)
- a single €80.01 refund, which proves the limit is the amount paid and not the total
- a refund on a paid-but-not-shipped order and on a cancelled order (both rejected)
- a zero amount and an unknown order

I also added a row and a sentence about the refund rules to the README's command table. Nothing is committed.

**Something to check with support:** the order only keeps a running total of refunds, not a list of individual refunds. It also doesn't stop two refunds that arrive at the same moment from both getting through. Neither does the existing load-then-save repository for the other commands. That's fine with the in-memory store, but with a real database two simultaneous refunds could together go over the amount paid. I left this alone because fixing it means changing how the repository saves orders, which is beyond this task.