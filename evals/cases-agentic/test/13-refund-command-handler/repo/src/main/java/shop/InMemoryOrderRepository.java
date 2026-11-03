package shop;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public final class InMemoryOrderRepository implements OrderRepository {
    private final Map<String, Order> orders = new HashMap<>();

    @Override
    public Optional<Order> find(String id) {
        return Optional.ofNullable(orders.get(id)).map(Order::copy);
    }

    @Override
    public void save(Order order) {
        orders.put(order.id(), order.copy());
    }
}
