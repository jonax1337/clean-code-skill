# Refund command for the order service (Java)

Tests adding a feature to a codebase with strong, visible conventions: every command is a record with exactly one handler class, all handlers are wired in `OrderServices.createBus`, input goes through the existing `Validator`, expected failures are returned as a `Result` (never thrown), and money is `BigDecimal`. The business rules carry the traps: the refund limit is the amount actually paid (which can be lower than the order total), earlier refunds count against it, the exact remaining amount must be accepted whatever its scale, and the repository stores snapshots so the order has to be saved. Graders look for a new handler that follows the pattern and reuses `Validator` and `Result`, exact decimal arithmetic, a registration next to the others, no edits to the other handlers, and tests for the new command.

## Prompt

We need to be able to refund orders. Please add a `RefundOrder(orderId, amount)` command to the order service. Support wants these rules: only shipped or delivered orders can be refunded, a refund can be partial but all refunds of an order together can never be more than what the customer actually paid, and the refund is recorded on the order (it already has `amountRefunded`). The order's status stays as it is.
