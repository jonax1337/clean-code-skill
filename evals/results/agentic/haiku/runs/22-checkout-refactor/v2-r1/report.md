I split `process_order` in `shop/checkout.py` into small helpers. The public signature is unchanged, and behavior is the same as far as I could check.

`process_order` now reads as the checkout steps in order:

1. `_validate_items`
2. Pricing: `_subtotal_cents`, `_tax_cents`, `_discount_cents`, `_shipping_cents`
3. `_reserve_stock`
4. `_charge_customer`
5. `_settle` (commit stock, redeem coupon, mark paid)
6. `_send_receipt`

Only `shop/checkout.py` changed. I did not commit.

**Verification**
- The existing 9 tests pass, before and after the change.
- I ran a differential check of the original and refactored functions on 20,000 random orders, covering VIP, country and coupon variants, stock shortages, declined payments, gateway crashes and notifier failures. It compared return values, exception types and messages, order status and totals, charges, receipts, and the inventory and coupon state. There were 0 mismatches. The random inputs produced mostly rejected orders, so the paid path was covered less than the rejection paths.
- No linter or type checker is installed in this environment, so I did not run one.

**Choices I made**
- The tax comment moved onto `_tax_cents`, where the rounding happens.
- Only `PaymentDeclined` triggers the stock release, as before.

**Something to look at (not changed)**
If the gateway raises anything other than `PaymentDeclined`, such as a network error, the reserved stock is never released and the order status stays `new`. That is existing production behavior, and fixing it would change behavior, so I left it. If you want it fixed, it is a small follow-up, and I'd add a test for it first.