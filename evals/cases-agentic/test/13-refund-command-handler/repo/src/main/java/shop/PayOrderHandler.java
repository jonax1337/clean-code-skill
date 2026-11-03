package shop;

import java.util.Optional;

public final class PayOrderHandler implements CommandHandler<PayOrder> {
    private final OrderRepository orders;

    public PayOrderHandler(OrderRepository orders) {
        this.orders = orders;
    }

    @Override
    public Result<Order> handle(PayOrder command) {
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
        if (order.status() != OrderStatus.PLACED) {
            return Result.failure(
                    ErrorCode.INVALID_STATE,
                    "Only placed orders can be paid, but order " + order.id() + " is " + order.status());
        }
        if (command.amount().compareTo(order.total()) > 0) {
            return Result.failure(
                    ErrorCode.INVALID_INPUT,
                    "Payment " + command.amount() + " is more than the order total " + order.total());
        }
        order.markPaid(command.amount());
        orders.save(order);
        return Result.ok(order);
    }
}
