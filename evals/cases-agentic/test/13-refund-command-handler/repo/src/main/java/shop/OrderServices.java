package shop;

/** Wires every command to its handler. */
public final class OrderServices {

    private OrderServices() {}

    public static CommandBus createBus(OrderRepository orders) {
        CommandBus bus = new CommandBus();
        bus.register(PlaceOrder.class, new PlaceOrderHandler(orders));
        bus.register(PayOrder.class, new PayOrderHandler(orders));
        bus.register(ShipOrder.class, new ShipOrderHandler(orders));
        bus.register(DeliverOrder.class, new DeliverOrderHandler(orders));
        bus.register(CancelOrder.class, new CancelOrderHandler(orders));
        return bus;
    }
}
