`RefundOrder(orderId, amount)` is added and committed on `main`. The full suite passes (28 tests, including 8 new ones for refunds).

**Rules, as built**
- **Status:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`, and the order's status never changes.
- **Cap:** all refunds of an order together can't exceed `amountPaid`. I used what the customer paid, not the order total, because the README says vouchers can cover part of an order. A refund over the remaining amount fails with `INVALID_INPUT`, and nothing is saved.
- **Recording:** each refund is added to `amountRefunded`, so partial refunds accumulate. Refunding exactly the remaining amount is allowed.
- **Amount checks:** it uses the same checks as `PayOrder`: positive, at most two decimal places, and the order must exist.

**What changed**
- New files: `RefundOrder` and `RefundOrderHandler`.
- Edited files: `Order.java` (new `recordRefund`), `OrderServices.java` (registers the handler) and the README command table.
- Tests: `RefundOrderHandlerTest` covers partial and cumulative refunds, delivered orders, the cap, each wrong status, bad amounts and an unknown order.

**Not done**
- **Failing test first:** I wrote the tests and the code in one pass, so I never ran the tests against the code before it existed.
- **Tools:** the skill's crapper, dryer and mutator tools aren't in this repo, so I didn't run them.
- **Push:** I didn't push, because `git remote -v` printed nothing, so this repo has no remote.
- **Line endings:** git warned that CRLF line endings in three files will become LF.