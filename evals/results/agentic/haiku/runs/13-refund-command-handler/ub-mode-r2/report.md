I added `RefundOrder(orderId, amount)` with a handler wired into the bus. The full suite passes: 28 tests, 8 of them new.

**Rules as implemented** (in `RefundOrderHandler`):
- **Status:** only `SHIPPED` or `DELIVERED` orders can be refunded. Anything else fails with `INVALID_STATE`, the same code the other handlers use.
- **Cap:** the amount must be positive with at most two decimals (the existing `Validator` enforces this). Refunds across one order can't exceed `amountPaid`. The cap is checked against the remaining refundable amount, `amountPaid - amountRefunded`. A refund that would go over fails with `INVALID_INPUT`, the same code `PayOrder` uses for an amount above the total.
- **Recording:** each accepted refund is added to `amountRefunded`. The status is not changed.

**Files:**
- `src/main/java/shop/RefundOrder.java`: new command record.
- `src/main/java/shop/RefundOrderHandler.java`: new handler with the rules above.
- `src/main/java/shop/Order.java`: added `refundableAmount()` and `refund(amount)`.
- `src/main/java/shop/OrderServices.java`: registered the handler.
- `src/test/java/shop/RefundOrderHandlerTest.java`: new tests, written first. I confirmed they failed to compile because `RefundOrder` did not exist yet.
- `README.md`: added a `RefundOrder` row to the command table and a short note on the rules.

**Not done:**
- **Commit and push:** I did not commit or push. The changes are in the working tree for you to review. Tell me if you want them committed, and whether to push to `main`.
- **Quality tools:** the ub-mode steps for crapper, dryer and mutator need tools that aren't in this repo, so I didn't run them.

**Choices you may want to check:**
- A refund is allowed on a shipped order before delivery. That follows Support's rule, which only names the two statuses.
- The cap uses `amountPaid`, which is the amount the payment actually recorded. For an order paid in full that is the total; for a voucher-covered order it is the lower amount.