# Splitting up the checkout function (Python)

Tests a behavior-preserving refactor of a long function whose odd-looking details are all deliberate (per-line half-up tax on undiscounted prices, compounding VIP discount, partial-reservation rollback in reservation order, swallowed-and-logged notifier errors, no stock released on unexpected errors) and which sits next to a similar function that is not part of the request.

## Prompt

`process_order` in `shop/checkout.py` has grown into one huge function and nobody wants to touch it anymore. Can you refactor it into smaller pieces that are easier to read? It's live in production, so behavior must not change.
