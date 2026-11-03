I added `RefundOrder(orderId, amount)` to the order service. It's committed on `main` as `9aba6bb`, and all 29 tests pass (20 existing, 9 new).

**How it behaves**
- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status is rejected with `INVALID_STATE`.
- **Partial refunds:** each refund is added to the order's `amountRefunded`. Several refunds are allowed as long as their sum stays within what the customer paid.
- **The cap is what the customer paid, not the order total.** The README says vouchers can make the amount paid lower than the total. So on a 100.00 order where the customer paid 80.00, a refund of 80.01 is rejected. That check lives in one place, `Order.refundableAmount()`, which is the amount paid minus what was already refunded.
- **Too-large refunds** are rejected with `INVALID_INPUT`, the same way `PayOrder` handles an overpayment.
- **Bad amounts:** zero, negative, or more than two decimal places are rejected. Unknown orders return `NOT_FOUND`.
- **Status stays as it is**, and the tests check that.

**What I did**
1. Read the code and README, and ran the tests before changing anything (20 passed).
2. Wrote `RefundOrderHandlerTest` first and saw it fail because no handler was registered.
3. Added `RefundOrder`, `RefundOrderHandler` and two methods on `Order` (`refundableAmount`, `recordRefund`), and registered the handler in `OrderServices`. I followed the same pattern as the existing handlers.
4. Added the command to the README.
5. The skill's crapper, dryer and mutator tools aren't in the skill folder, so I couldn't run them. Instead I changed the code by hand three ways: capping at the amount paid without subtracting earlier refunds, capping at the total, and making the limit check off by one. The tests failed each time, and I restored the code afterwards.
6. Committed. **I didn't push** because the repo has no remote.

**Decision for you:** the repository loads an order and saves it back with no version check. If two refunds for the same order run at exactly the same time, both could pass the check and together refund more than was paid. The other commands have the same gap; it matters more here because it involves money. If refunds can run in parallel in production, the fix belongs in the repository, as a version check on save. I haven't made that change; tell me if you want it.