package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class PayOrderHandlerTest {
    private final OrderRepository orders = new InMemoryOrderRepository();
    private final CommandBus bus = OrderServices.createBus(orders);

    @BeforeEach
    void placeOrder() {
        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
    }

    @Test
    void recordsTheAmountActuallyPaid() {
        Result<Order> result = bus.dispatch(new PayOrder("o-1", new BigDecimal("80.00")));

        assertTrue(result.isOk());
        Order stored = orders.find("o-1").orElseThrow();
        assertEquals(OrderStatus.PAID, stored.status());
        assertEquals(0, new BigDecimal("80.00").compareTo(stored.amountPaid()));
    }

    @Test
    void rejectsMoreThanTheTotal() {
        Result<Order> result = bus.dispatch(new PayOrder("o-1", new BigDecimal("100.01")));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
    }

    @Test
    void rejectsAnOrderThatIsAlreadyPaid() {
        bus.dispatch(new PayOrder("o-1", new BigDecimal("100.00")));

        Result<Order> result = bus.dispatch(new PayOrder("o-1", new BigDecimal("100.00")));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_STATE, result.error().code());
    }

    @Test
    void reportsAnUnknownOrder() {
        Result<Order> result = bus.dispatch(new PayOrder("missing", new BigDecimal("10.00")));

        assertEquals(ErrorCode.NOT_FOUND, result.error().code());
    }
}
