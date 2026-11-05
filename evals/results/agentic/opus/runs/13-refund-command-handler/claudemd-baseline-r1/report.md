I've added the `RefundOrder(orderId, amount)` command. All 29 tests pass when I run `java tools/RunTests.java`, including 9 new ones for refunds.

**How it works:**
- **Status:** refunds are only allowed on `SHIPPED` or `DELIVERED` orders. Any other status is rejected with `INVALID_STATE`, and the order's status never changes.
- **Limit:** the cap is the amount the customer actually paid (`amountPaid`), not the order total. Since a voucher can make `amountPaid` lower than the total, a refund that fits within the total can still be too much. A refund is rejected with `INVALID_INPUT` if adding it would make all refunds together more than `amountPaid`. Partial refunds add up in `amountRefunded`.
- **Amount checks:** it uses the same checks as payments: the amount is required, must be more than zero, and can have at most two decimal places. An unknown order gives `NOT_FOUND`.

**Changes:**
- New `src/main/java/shop/RefundOrder.java` and `RefundOrderHandler.java`, written the same way as the existing handlers.
- `Order.recordRefund(amount)` adds the refund to `amountRefunded`.
- The handler is registered in `OrderServices.createBus`.
- The README now lists the command and its rules.
- New `src/test/java/shop/RefundOrderHandlerTest.java` covers:
  - partial refunds on shipped and delivered orders, with the status staying the same
  - several refunds adding up
  - a refund over `amountPaid` but under the total being rejected
  - a second refund that would go over the limit being rejected
  - paid-but-not-shipped and cancelled orders being rejected
  - invalid amounts
  - an unknown order

**Your call:** a refund that's too large is reported as `INVALID_INPUT`, the same code `PayOrder` uses for overpaying. If support would rather have a separate error code for this, it's a small change.