package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class CancelOrderHandlerTest {
    private final OrderRepository orders = new InMemoryOrderRepository();
    private final CommandBus bus = OrderServices.createBus(orders);

    @Test
    void cancelsAPlacedOrder() {
        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));

        Result<Order> result = bus.dispatch(new CancelOrder("o-1"));

        assertTrue(result.isOk());
        assertEquals(OrderStatus.CANCELLED, orders.find("o-1").orElseThrow().status());
    }

    @Test
    void rejectsAnOrderThatWasShipped() {
        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
        bus.dispatch(new PayOrder("o-1", new BigDecimal("100.00")));
        bus.dispatch(new ShipOrder("o-1"));

        Result<Order> result = bus.dispatch(new CancelOrder("o-1"));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_STATE, result.error().code());
        assertEquals(OrderStatus.SHIPPED, orders.find("o-1").orElseThrow().status());
    }
}
