package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class PlaceOrderHandlerTest {
    private final OrderRepository orders = new InMemoryOrderRepository();
    private final CommandBus bus = OrderServices.createBus(orders);

    @Test
    void placesANewOrder() {
        Result<Order> result = bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("59.90")));

        assertTrue(result.isOk());
        assertEquals(OrderStatus.PLACED, orders.find("o-1").orElseThrow().status());
    }

    @Test
    void rejectsADuplicateOrderId() {
        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("59.90")));

        Result<Order> result = bus.dispatch(new PlaceOrder("o-1", "c-2", new BigDecimal("10.00")));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.ALREADY_EXISTS, result.error().code());
    }

    @Test
    void rejectsInvalidInput() {
        Result<Order> result = bus.dispatch(new PlaceOrder(" ", "c-1", new BigDecimal("-1")));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
    }
}
