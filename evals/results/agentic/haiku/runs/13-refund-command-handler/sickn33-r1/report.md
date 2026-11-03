`RefundOrder` is in place and all 27 tests pass, including 7 new ones for refunds.

**What changed**
- `RefundOrder.java`: new command record `(orderId, amount)`.
- `RefundOrderHandler.java`: the handler, following the same pattern as the other handlers. It checks, in order:
  1. `orderId` is present and `amount` is positive with at most two decimals (`INVALID_INPUT`).
  2. The order exists (`NOT_FOUND`).
  3. The status is `SHIPPED` or `DELIVERED` (`INVALID_STATE`).
  4. The amount is no more than `amountPaid - amountRefunded` (`INVALID_INPUT`).
- `Order.java`: new `recordRefund(amount)` method that adds to `amountRefunded`. The status is not touched.
- `OrderServices.java`: registers the handler on the bus.
- `README.md`: adds the command to the table and describes the rules.
- `RefundOrderHandlerTest.java`: covers both allowed statuses, rejection before shipping, overpaying, the cumulative cap across two refunds, an unknown order, and a zero amount.

**Choices I made that you may want to check**
- The cap is based on the amount **paid**, not the order total. The README says an order can be paid for less than its total, so refunding up to the total would refund money the customer never paid.
- Refund-over-limit and wrong-status use `INVALID_INPUT` and `INVALID_STATE`, the same codes the existing handlers use for their equivalent cases.
- A refund does not check whether the order was cancelled. That can't happen, because only `SHIPPED` and `DELIVERED` orders qualify.

I haven't committed anything. Tell me if you want a commit.