package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class CommandBusTest {
    private record Unknown(String orderId) {}

    @Test
    void failsForACommandWithoutHandler() {
        CommandBus bus = OrderServices.createBus(new InMemoryOrderRepository());

        Result<Order> result = bus.dispatch(new Unknown("o-1"));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
    }

    @Test
    void refusesToRegisterTwoHandlersForOneCommand() {
        OrderRepository orders = new InMemoryOrderRepository();
        CommandBus bus = new CommandBus();
        bus.register(ShipOrder.class, new ShipOrderHandler(orders));

        assertThrows(
                IllegalStateException.class, () -> bus.register(ShipOrder.class, new ShipOrderHandler(orders)));
    }
}
