I added `RefundOrder(orderId, amount)` and its handler, following the same pattern as the other commands. `java tools/RunTests.java` runs 28 tests with 0 failures, including 8 new ones in `RefundOrderHandlerTest`. I haven't committed anything.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`.
- **Limit:** the cap is what the customer actually paid (`amountPaid`), not the order total. For example, a voucher order paid at 80.00 of a 100.00 total can be refunded at most 80.00 in total.
- **Cumulative check:** a refund fails with `INVALID_INPUT` if it plus earlier refunds would exceed `amountPaid`. A refund that uses up exactly what's left succeeds.
- **Recording:** the refund is added to `amountRefunded` through a new `Order.recordRefund`, and the status is left alone.
- **Input checks:** the amount goes through the same money validation as `PayOrder`. It must be above zero with at most two decimals. A missing order fails with `NOT_FOUND`.
- **Wiring and docs:** the handler is registered in `OrderServices.createBus`. I added a `RefundOrder` row and a sentence on the refund cap to the README.

The tests cover partial and multiple refunds, a delivered order, the cap against `amountPaid`, rejected statuses, invalid amounts and an unknown order.

I read "stays as it is" to mean a fully refunded order keeps its status. If Support wants a "refunded" status later, that would be a separate change.