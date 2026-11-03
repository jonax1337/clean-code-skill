package shop;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class RefundOrderInputTest {
    private final RefundScenario scenario = new RefundScenario();

    private Result<Order> dispatch(String orderId, BigDecimal amount) {
        return assertDoesNotThrow(() -> scenario.bus.dispatch(new RefundOrder(orderId, amount)));
    }

    private void assertInvalidInput(Result<Order> result) {
        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
        scenario.assertRefunded("o-1", "0");
    }

    @Test
    void rejectsAMissingOrBlankOrderId() {
        scenario.order("o-1", "100.00", "100.00", OrderStatus.SHIPPED);

        for (String orderId : new String[] {null, "", "   "}) {
            Result<Order> result = dispatch(orderId, new BigDecimal("10.00"));

            assertInvalidInput(result);
        }
    }

    @Test
    void rejectsAMissingAmount() {
        scenario.order("o-1", "100.00", "100.00", OrderStatus.SHIPPED);

        assertInvalidInput(dispatch("o-1", null));
    }

    @Test
    void rejectsAnAmountThatIsZeroOrNegative() {
        scenario.order("o-1", "100.00", "100.00", OrderStatus.SHIPPED);

        assertInvalidInput(dispatch("o-1", BigDecimal.ZERO));
        assertInvalidInput(dispatch("o-1", new BigDecimal("0.00")));
        assertInvalidInput(dispatch("o-1", new BigDecimal("-5.00")));
    }

    @Test
    void rejectsAnAmountWithMoreThanTwoDecimals() {
        scenario.order("o-1", "100.00", "100.00", OrderStatus.SHIPPED);

        assertInvalidInput(dispatch("o-1", new BigDecimal("10.005")));
        assertInvalidInput(dispatch("o-1", new BigDecimal("0.001")));
    }

    @Test
    void acceptsAnAmountWithTrailingZerosBeyondTwoDecimals() {
        scenario.order("o-1", "100.00", "100.00", OrderStatus.SHIPPED);

        Result<Order> result = dispatch("o-1", new BigDecimal("10.500"));

        assertTrue(result.isOk());
        scenario.assertRefunded("o-1", "10.5");
    }

    @Test
    void rejectsBadInputBeforeLookingForTheOrder() {
        Result<Order> result = dispatch("missing", new BigDecimal("-1"));

        assertFalse(result.isOk());
        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
    }
}
