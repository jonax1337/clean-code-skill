I added `RefundOrder(orderId, amount)` and committed it to `main` as `ca7b5ad`. All 29 tests pass and the compiler gives no warnings. Nothing was pushed because the repo has no remote.

**How it behaves**
- Only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status is rejected with `INVALID_STATE`.
- A refund can be partial, and each one is added to `amountRefunded`. The order's status doesn't change.
- **The limit is `amountPaid`, not `total`.** The README notes that a voucher can cover part of the total, so on a 100.00 order where the customer paid 80.00, refunds stop at 80.00. A refund that would push the running total over that is rejected with `INVALID_INPUT` (the same code used for paying more than the total), and nothing is recorded.
- The amount is checked like other money in the service: it must be greater than zero and have at most two decimal places. An unknown order returns `NOT_FOUND`.

**Files:** new `RefundOrder.java` and `RefundOrderHandler.java`; `Order.refund(amount)`; the handler is registered in `OrderServices.createBus`; one row and a short note added to the README.

**Log**
1. Read the whole repo and found the pattern every handler follows, plus the voucher note that makes `amountPaid` the right limit.
2. Wrote `RefundOrderHandlerTest` first (9 tests covering shipped and delivered refunds, several partial refunds adding up, the paid-vs-total limit, the limit with earlier refunds, wrong statuses, bad amounts and an unknown order). Seven failed for the expected reason: no handler was registered yet. The other two passed only because an unregistered command already returns `INVALID_INPUT`.
3. Wrote the handler, `Order.refund` and the wiring: 29/29 pass.
4. Tried two deliberate bugs by hand: limiting refunds by `total` instead of `amountPaid`, and using `>=` instead of `>`. The tests caught each one (2 failures each), then I restored the file.
5. Committed with the reason, what changed and the test results in the message.

**Not done**
- The skill's crapper, dryer and mutator tools aren't in the skill folder, so the hand-made bug check in step 4 replaced the mutator.
- Every handler, including the new one, repeats the same "validate, find, not-found" code. I left it alone because tidying it up would be a separate refactor.