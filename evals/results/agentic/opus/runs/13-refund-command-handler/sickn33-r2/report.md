I added `RefundOrder(orderId, amount)` and it follows support's rules. All 29 tests pass, including 9 new ones for refunds.

**How it works**
- **Which orders:** only shipped or delivered orders can be refunded. Anything else, including cancelled orders, is rejected as `INVALID_STATE`.
- **Limit:** all refunds on an order together can't go above what the customer actually paid (`amountPaid`, not `total`). For example, if a voucher covered 20 of a 100.00 order and the customer paid 80.00, the limit is 80.00. A refund over that is rejected as `INVALID_INPUT`, the same code used when a payment is larger than the total.
- **Partial refunds:** each refund is added to `amountRefunded`. The order's status doesn't change.
- **Bad input:** a missing or blank order ID, an amount of zero or less, or more than two decimal places is rejected the same way as for the other commands. An unknown order returns `NOT_FOUND`.

**Changes**
- `RefundOrder.java` and `RefundOrderHandler.java`: the new command and its handler.
- `Order.java`: added `refundableAmount()` (amount paid minus amount already refunded) and `recordRefund(amount)`.
- `OrderServices.java`: registers the new handler.
- `README.md`: added the command to the table, with a note on the refund rules.
- `RefundOrderHandlerTest.java`: tests for partial refunds, several refunds adding up, the paid-vs-total limit, the status rules, invalid amounts and unknown orders.

I haven't committed anything.