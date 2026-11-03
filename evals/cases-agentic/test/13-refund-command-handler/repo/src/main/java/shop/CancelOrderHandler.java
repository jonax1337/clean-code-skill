package shop;

import java.util.Optional;

public final class CancelOrderHandler implements CommandHandler<CancelOrder> {
    private final OrderRepository orders;

    public CancelOrderHandler(OrderRepository orders) {
        this.orders = orders;
    }

    @Override
    public Result<Order> handle(CancelOrder command) {
        Validator validator = new Validator().requireText("orderId", command.orderId());
        if (!validator.isValid()) {
            return validator.failure();
        }
        Optional<Order> found = orders.find(command.orderId());
        if (found.isEmpty()) {
            return Result.failure(ErrorCode.NOT_FOUND, "Order " + command.orderId() + " does not exist");
        }
        Order order = found.get();
        if (order.status() != OrderStatus.PLACED && order.status() != OrderStatus.PAID) {
            return Result.failure(
                    ErrorCode.INVALID_STATE,
                    "Only placed or paid orders can be cancelled, but order " + order.id() + " is " + order.status());
        }
        order.cancel();
        orders.save(order);
        return Result.ok(order);
    }
}
