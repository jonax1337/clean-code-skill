package shop;

import java.util.Optional;

public final class ShipOrderHandler implements CommandHandler<ShipOrder> {
    private final OrderRepository orders;

    public ShipOrderHandler(OrderRepository orders) {
        this.orders = orders;
    }

    @Override
    public Result<Order> handle(ShipOrder command) {
        Validator validator = new Validator().requireText("orderId", command.orderId());
        if (!validator.isValid()) {
            return validator.failure();
        }
        Optional<Order> found = orders.find(command.orderId());
        if (found.isEmpty()) {
            return Result.failure(ErrorCode.NOT_FOUND, "Order " + command.orderId() + " does not exist");
        }
        Order order = found.get();
        if (order.status() != OrderStatus.PAID) {
            return Result.failure(
                    ErrorCode.INVALID_STATE,
                    "Only paid orders can be shipped, but order " + order.id() + " is " + order.status());
        }
        order.markShipped();
        orders.save(order);
        return Result.ok(order);
    }
}
