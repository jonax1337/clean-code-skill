I added `RefundOrder(orderId, amount)` to the order service. The full suite passes, including 8 new tests for refunds.

- **Status rule:** only shipped or delivered orders can be refunded. Any other status returns `INVALID_STATE`. That includes paid orders that haven't shipped yet, and cancelled ones.
- **Cap:** all refunds of an order together can't exceed `amountPaid - amountRefunded`. I used what the customer paid, not the order total, because a customer can pay less than the total. A refund over the cap returns `INVALID_INPUT`. Partial refunds add up in `amountRefunded`.
- **Status after a refund:** the order keeps its current status.
- **Input checks:** it reuses the existing ones, so the amount must be positive with at most two decimals. An unknown order returns `NOT_FOUND`.

The new files are `RefundOrder.java`, `RefundOrderHandler.java` and `RefundOrderHandlerTest.java`. I also added three small methods to `Order` (`isRefundable`, `refundableAmount`, `recordRefund`) and registered the handler in `OrderServices.createBus`.

I didn't commit anything.