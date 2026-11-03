package shop;

import java.util.Optional;

public interface OrderRepository {

    Optional<Order> find(String id);

    void save(Order order);
}
