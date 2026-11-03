package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;

/** Test fixture: a bus over a fresh repository, and orders brought into any status through the real commands. */
final class RefundScenario {
    final OrderRepository repository = new InMemoryOrderRepository();
    final CommandBus bus = OrderServices.createBus(repository);

    void order(String id, String total, String paid, OrderStatus status) {
        bus.dispatch(new PlaceOrder(id, "customer-1", new BigDecimal(total)));
        if (status == OrderStatus.PLACED) {
            return;
        }
        bus.dispatch(new PayOrder(id, new BigDecimal(paid)));
        if (status == OrderStatus.CANCELLED) {
            bus.dispatch(new CancelOrder(id));
            return;
        }
        if (status == OrderStatus.PAID) {
            return;
        }
        bus.dispatch(new ShipOrder(id));
        if (status == OrderStatus.DELIVERED) {
            bus.dispatch(new DeliverOrder(id));
        }
    }

    Result<Order> refund(String id, String amount) {
        return bus.dispatch(new RefundOrder(id, new BigDecimal(amount)));
    }

    Order stored(String id) {
        return repository.find(id).orElseThrow();
    }

    void assertRefunded(String id, String expected) {
        assertAmount(expected, stored(id).amountRefunded());
    }

    static void assertAmount(String expected, BigDecimal actual) {
        assertEquals(0, new BigDecimal(expected).compareTo(actual), "expected " + expected + " but was " + actual);
    }
}
