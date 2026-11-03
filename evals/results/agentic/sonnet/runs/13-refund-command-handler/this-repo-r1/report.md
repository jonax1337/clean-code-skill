`RefundOrder(orderId, amount)` is now a command on the order service. I ran `java tools/RunTests.java` after the last edit: 29 tests found, 29 successful, 0 failed. The 8 new refund tests are part of that.

**What it does**
- Only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`, and an unknown order fails with `NOT_FOUND`.
- The refund amount uses the same check as payments. It must be greater than zero and have at most two decimal places, otherwise it fails with `INVALID_INPUT`.
- All refunds of an order together can't exceed `amountPaid`, not `total`. Orders can be underpaid, for example when a voucher covered part of the total, so the customer only gets back what they actually paid. A refund over the remaining refundable amount fails with `INVALID_INPUT`, and the order is left unchanged.
- A successful refund is added to `amountRefunded`, so partial refunds accumulate. The status doesn't change.

**Files**
- New: `RefundOrder.java`, `RefundOrderHandler.java` and `RefundOrderHandlerTest.java`.
- Changed: `Order.java` (new `recordRefund`), `OrderServices.java` (registers the handler) and `README.md` (new row in the command table plus one line on the refund rule).

The tests cover partial refunds that keep the status, refunds on delivered orders, several refunds adding up to exactly the amount paid, one refund too many, an underpaid order, wrong statuses (paid but not shipped, cancelled), an unknown order, and bad amounts.

**One thing for Support to confirm:** refunding the full amount paid is allowed and leaves nothing further refundable. I didn't add anything to block repeat refunds beyond that cap.