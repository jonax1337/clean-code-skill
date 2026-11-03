package shop;

import java.math.BigDecimal;
import java.util.Optional;

public final class RefundOrderHandler implements CommandHandler<RefundOrder> {
    private final OrderRepository orders;

    public RefundOrderHandler(OrderRepository orders) {
        this.orders = orders;
    }

    @Override
    public Result<Order> handle(RefundOrder command) {
        Validator validator = new Validator()
                .requireText("orderId", command.orderId())
                .requireMoney("amount", command.amount());
        if (!validator.isValid()) {
            return validator.failure();
        }
        Optional<Order> found = orders.find(command.orderId());
        if (found.isEmpty()) {
            return Result.failure(ErrorCode.NOT_FOUND, "Order " + command.orderId() + " does not exist");
        }
        Order order = found.get();
        if (order.status() != OrderStatus.SHIPPED && order.status() != OrderStatus.DELIVERED) {
            return Result.failure(
                    ErrorCode.INVALID_STATE,
                    "Only shipped or delivered orders can be refunded, but order " + order.id() + " is "
                            + order.status());
        }
        BigDecimal refundable = order.amountPaid().subtract(order.amountRefunded());
        if (command.amount().compareTo(refundable) > 0) {
            return Result.failure(
                    ErrorCode.INVALID_INPUT,
                    "Refund " + command.amount() + " is more than the " + refundable + " still refundable");
        }
        order.recordRefund(command.amount());
        orders.save(order);
        return Result.ok(order);
    }
}
