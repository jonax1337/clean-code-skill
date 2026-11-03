I added the `RefundOrder(orderId, amount)` command with Support's rules. The full test suite passes (28 tests, including 8 new ones for refunds).

**How it behaves**
- **Status:** only `SHIPPED` or `DELIVERED` orders can be refunded, and a refund doesn't change the status. Any other status is rejected as `INVALID_STATE`.
- **Limit:** each refund is added to `amountRefunded`. A refund is rejected (`INVALID_INPUT`) if it would push the total refunded above **`amountPaid`**. I used the amount paid rather than the order total because the two can differ when a voucher covered part of the order. For example, on a 100.00 order where the customer paid 80.00, you can refund at most 80.00 in total.
- **Bad input:** a missing, zero, negative or more-than-two-decimals amount, or a blank order ID, is rejected with the same checks `PayOrder` uses. An unknown order returns `NOT_FOUND`.

**What changed**
- `RefundOrder.java` and `RefundOrderHandler.java` are new and follow the same pattern as the other handlers.
- `Order.java` has two new methods: `refundableAmount()` (amount paid minus amount refunded) and `recordRefund(amount)`.
- `OrderServices.createBus` now registers the new handler.
- `README.md` lists the new command in its table.
- `RefundOrderHandlerTest.java` tests partial refunds, several refunds adding up, the limit being the amount paid rather than the total, the status rules, and invalid input.

**Worth knowing:** like the existing handlers, this reads the order, checks it, then saves it, with no locking. If two refunds for the same order arrive at the same moment, both could pass the limit check. That's fine with the current in-memory repository, but a real database would need version checks or locking to stop it.

I haven't committed anything.