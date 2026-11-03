package shop;

import java.util.Optional;

public final class DeliverOrderHandler implements CommandHandler<DeliverOrder> {
    private final OrderRepository orders;

    public DeliverOrderHandler(OrderRepository orders) {
        this.orders = orders;
    }

    @Override
    public Result<Order> handle(DeliverOrder command) {
        Validator validator = new Validator().requireText("orderId", command.orderId());
        if (!validator.isValid()) {
            return validator.failure();
        }
        Optional<Order> found = orders.find(command.orderId());
        if (found.isEmpty()) {
            return Result.failure(ErrorCode.NOT_FOUND, "Order " + command.orderId() + " does not exist");
        }
        Order order = found.get();
        if (order.status() != OrderStatus.SHIPPED) {
            return Result.failure(
                    ErrorCode.INVALID_STATE,
                    "Only shipped orders can be delivered, but order " + order.id() + " is " + order.status());
        }
        order.markDelivered();
        orders.save(order);
        return Result.ok(order);
    }
}
