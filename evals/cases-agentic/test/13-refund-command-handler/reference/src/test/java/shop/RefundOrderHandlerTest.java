package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class RefundOrderHandlerTest {
    private final OrderRepository orders = new InMemoryOrderRepository();
    private final CommandBus bus = OrderServices.createBus(orders);

    private void shippedOrder(String total, String paid) {
        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal(total)));
        bus.dispatch(new PayOrder("o-1", new BigDecimal(paid)));
        bus.dispatch(new ShipOrder("o-1"));
    }

    private Result<Order> refund(String amount) {
        return bus.dispatch(new RefundOrder("o-1", new BigDecimal(amount)));
    }

    private void assertRefunded(String expected) {
        assertEquals(0, new BigDecimal(expected).compareTo(orders.find("o-1").orElseThrow().amountRefunded()));
    }

    @Test
    void recordsAPartialRefundOnAShippedOrder() {
        shippedOrder("100.00", "100.00");

        Result<Order> result = refund("40.00");

        assertTrue(result.isOk());
        assertRefunded("40.00");
        assertEquals(OrderStatus.SHIPPED, orders.find("o-1").orElseThrow().status());
    }

    @Test
    void refundsADeliveredOrder() {
        shippedOrder("100.00", "100.00");
        bus.dispatch(new DeliverOrder("o-1"));

        assertTrue(refund("100.00").isOk());
        assertRefunded("100.00");
    }

    @Test
    void refusesAnOrderThatWasNotShipped() {
        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
        bus.dispatch(new PayOrder("o-1", new BigDecimal("100.00")));

        Result<Order> result = refund("10.00");

        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_STATE, result.error().code());
        assertRefunded("0");
    }

    @Test
    void limitsRefundsToWhatWasPaidMinusEarlierRefunds() {
        shippedOrder("100.00", "80.00");
        refund("50.00");

        assertFalse(refund("30.01").isOk());
        assertRefunded("50.00");
        assertTrue(refund("30.00").isOk());
        assertRefunded("80.00");
    }

    @Test
    void rejectsInvalidInputAndUnknownOrders() {
        shippedOrder("100.00", "100.00");

        assertEquals(ErrorCode.INVALID_INPUT, refund("0").error().code());
        assertEquals(ErrorCode.INVALID_INPUT, refund("1.234").error().code());
        assertEquals(
                ErrorCode.NOT_FOUND,
                bus.dispatch(new RefundOrder("missing", new BigDecimal("1.00"))).error().code());
    }
}
