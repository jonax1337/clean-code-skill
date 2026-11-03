I added the `RefundOrder(orderId, amount)` command with the rules Support asked for. The full test suite passes (28 tests, including 8 new refund tests).

**One decision to check:** I capped refunds at the amount the customer actually paid (`amountPaid`), not the order total. The README says the two can differ when a voucher covered part of the order. For example, if an order totals 100.00 and the customer paid 80.00, at most 80.00 can be refunded across all refunds, and a refund of 80.01 is rejected.

**What changed:**
- **New command:** `RefundOrder.java` and `RefundOrderHandler.java`, written the same way as the existing handlers.
- **Rules:**
  - The amount must be a valid money value: present, greater than zero, and at most two decimal places.
  - The order must exist.
  - The order must be `SHIPPED` or `DELIVERED`. Otherwise the refund is rejected as `INVALID_STATE`.
  - A refund that would push the total refunded over the amount paid is rejected as `INVALID_INPUT`, the same code `PayOrder` uses when a payment is too high. A rejected refund leaves the order unchanged.
- **Recording:** a new `Order.recordRefund(amount)` adds each refund to `amountRefunded`. The order's status stays as it is.
- **Wiring:** the handler is registered in `OrderServices.createBus`, and I added a row for it to the command table in the README.
- **Tests:** `RefundOrderHandlerTest` covers partial refunds, several refunds adding up, both statuses staying the same, the cap based on the amount paid, the wrong-status case, invalid amounts and an unknown order.

Nothing is committed yet.