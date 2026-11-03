package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class DeliverOrderHandlerTest {
    private final OrderRepository orders = new InMemoryOrderRepository();
    private final CommandBus bus = OrderServices.createBus(orders);

    @Test
    void deliversAShippedOrder() {
        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
        bus.dispatch(new PayOrder("o-1", new BigDecimal("100.00")));
        bus.dispatch(new ShipOrder("o-1"));

        Result<Order> result = bus.dispatch(new DeliverOrder("o-1"));

        assertTrue(result.isOk());
        assertEquals(OrderStatus.DELIVERED, orders.find("o-1").orElseThrow().status());
    }

    @Test
    void rejectsAnOrderThatWasNotShipped() {
        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
        bus.dispatch(new PayOrder("o-1", new BigDecimal("100.00")));

        Result<Order> result = bus.dispatch(new DeliverOrder("o-1"));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_STATE, result.error().code());
    }
}
