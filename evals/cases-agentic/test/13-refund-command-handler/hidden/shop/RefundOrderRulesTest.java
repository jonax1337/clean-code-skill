package shop;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class RefundOrderRulesTest {
    private final RefundScenario scenario = new RefundScenario();

    @Test
    void refundsPartOfAShippedOrder() {
        scenario.order("o-1", "100.00", "100.00", OrderStatus.SHIPPED);

        Result<Order> result = assertDoesNotThrow(() -> scenario.refund("o-1", "25.50"));

        assertTrue(result.isOk());
        RefundScenario.assertAmount("25.50", result.value().amountRefunded());
        scenario.assertRefunded("o-1", "25.50");
        assertEquals(OrderStatus.SHIPPED, scenario.stored("o-1").status());
    }

    @Test
    void refundsTheWholeAmountOfADeliveredOrder() {
        scenario.order("o-1", "100.00", "100.00", OrderStatus.DELIVERED);

        Result<Order> result = scenario.refund("o-1", "100.00");

        assertTrue(result.isOk());
        scenario.assertRefunded("o-1", "100.00");
        assertEquals(OrderStatus.DELIVERED, scenario.stored("o-1").status());
    }

    @Test
    void refusesOrdersThatAreNeitherShippedNorDelivered() {
        scenario.order("placed", "100.00", "100.00", OrderStatus.PLACED);
        scenario.order("paid", "100.00", "100.00", OrderStatus.PAID);
        scenario.order("cancelled", "100.00", "100.00", OrderStatus.CANCELLED);

        for (String id : new String[] {"placed", "paid", "cancelled"}) {
            Result<Order> result = assertDoesNotThrow(() -> scenario.refund(id, "10.00"));

            assertFalse(result.isOk(), id);
            assertEquals(ErrorCode.INVALID_STATE, result.error().code(), id);
            scenario.assertRefunded(id, "0");
        }
    }

    @Test
    void reportsAnUnknownOrder() {
        Result<Order> result = assertDoesNotThrow(() -> scenario.refund("missing", "10.00"));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.NOT_FOUND, result.error().code());
    }

    @Test
    void theLimitIsWhatWasPaidNotTheOrderTotal() {
        scenario.order("o-1", "100.00", "80.00", OrderStatus.SHIPPED);

        Result<Order> tooMuch = assertDoesNotThrow(() -> scenario.refund("o-1", "80.01"));
        assertFalse(tooMuch.isOk());
        scenario.assertRefunded("o-1", "0");

        assertTrue(scenario.refund("o-1", "80.00").isOk());
        scenario.assertRefunded("o-1", "80.00");
    }

    @Test
    void partialRefundsAddUpAndNeverExceedWhatWasPaid() {
        scenario.order("o-1", "100.00", "80.00", OrderStatus.DELIVERED);

        assertTrue(scenario.refund("o-1", "30.00").isOk());
        assertTrue(scenario.refund("o-1", "20.00").isOk());
        scenario.assertRefunded("o-1", "50.00");

        Result<Order> tooMuch = assertDoesNotThrow(() -> scenario.refund("o-1", "30.01"));
        assertFalse(tooMuch.isOk());
        scenario.assertRefunded("o-1", "50.00");

        assertTrue(scenario.refund("o-1", "30.00").isOk());
        scenario.assertRefunded("o-1", "80.00");

        Result<Order> nothingLeft = assertDoesNotThrow(() -> scenario.refund("o-1", "0.01"));
        assertFalse(nothingLeft.isOk());
        scenario.assertRefunded("o-1", "80.00");
    }

    @Test
    void theExactRemainingAmountIsAllowedWhateverItsScale() {
        scenario.order("a", "100.00", "100.00", OrderStatus.SHIPPED);
        scenario.refund("a", "60.00");
        assertTrue(scenario.refund("a", "40.0").isOk());
        scenario.assertRefunded("a", "100");

        scenario.order("b", "100.00", "100.00", OrderStatus.SHIPPED);
        scenario.refund("b", "60.5");
        assertTrue(scenario.refund("b", "39.50").isOk());
        scenario.assertRefunded("b", "100.00");
    }

    @Test
    void aRefundedOrderStaysRefundableUntilNothingIsLeft() {
        scenario.order("o-1", "50.00", "50.00", OrderStatus.SHIPPED);
        scenario.refund("o-1", "50.00");

        assertEquals(OrderStatus.SHIPPED, scenario.stored("o-1").status());
        assertFalse(scenario.refund("o-1", "1.00").isOk());
    }

    @Test
    void refundsOfOneOrderDoNotAffectAnother() {
        scenario.order("o-1", "100.00", "100.00", OrderStatus.SHIPPED);
        scenario.order("o-2", "100.00", "100.00", OrderStatus.SHIPPED);

        scenario.refund("o-1", "70.00");

        scenario.assertRefunded("o-2", "0");
        assertTrue(scenario.refund("o-2", "100.00").isOk());
    }
}
