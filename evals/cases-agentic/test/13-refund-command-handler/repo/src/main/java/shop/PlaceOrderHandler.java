package shop;

public final class PlaceOrderHandler implements CommandHandler<PlaceOrder> {
    private final OrderRepository orders;

    public PlaceOrderHandler(OrderRepository orders) {
        this.orders = orders;
    }

    @Override
    public Result<Order> handle(PlaceOrder command) {
        Validator validator = new Validator()
                .requireText("orderId", command.orderId())
                .requireText("customerId", command.customerId())
                .requireMoney("total", command.total());
        if (!validator.isValid()) {
            return validator.failure();
        }
        if (orders.find(command.orderId()).isPresent()) {
            return Result.failure(ErrorCode.ALREADY_EXISTS, "Order " + command.orderId() + " already exists");
        }
        Order order = new Order(command.orderId(), command.customerId(), command.total());
        orders.save(order);
        return Result.ok(order);
    }
}
