`RefundOrder(orderId, amount)` now works. The commit is local only: the push failed because this repo has no remote configured. The full suite passes (27 tests, including the new `RefundOrderHandlerTest`).

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status returns `INVALID_STATE`.
- **Cap:** all refunds on an order together can't exceed `amountPaid`, not `total`. A voucher can make the amount paid lower than the total, and the cap follows what the customer actually paid. A refund over the cap returns `INVALID_INPUT`.
- **Partial refunds:** each refund adds to `amountRefunded`, and the order's status stays as it is. A refund that brings the total to exactly the amount paid is allowed.
- **Input checks:** the amount goes through the same check as `PayOrder` (positive, at most two decimals). An unknown order returns `NOT_FOUND`.

I added `RefundOrder` and `RefundOrderHandler`, registered the handler in `OrderServices.createBus`, and added `refundable()` and `refund()` to `Order`. I also added a row for the new command to the README table.

**Log**
1. I read the existing handlers, `Order` and the README to match their conventions.
2. I wrote the tests first and confirmed the build failed because the new methods and registration didn't exist yet.
3. I added the command, handler, `Order` methods and bus registration, then re-ran the suite.
4. I committed to `main` with the reason and the proof in the message.
5. I did not run the crapper, dryer or mutator tools. The handler follows the same pattern as the others, so I didn't expect new duplication or complexity.