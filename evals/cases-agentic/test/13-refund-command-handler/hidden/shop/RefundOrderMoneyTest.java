package shop;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class RefundOrderMoneyTest {
    private final RefundScenario scenario = new RefundScenario();

    @Test
    void threeRefundsOfTenCentsFitIntoThirtyCents() {
        scenario.order("o-1", "0.30", "0.30", OrderStatus.SHIPPED);

        assertTrue(scenario.refund("o-1", "0.10").isOk());
        assertTrue(scenario.refund("o-1", "0.10").isOk());
        assertTrue(scenario.refund("o-1", "0.10").isOk());

        scenario.assertRefunded("o-1", "0.30");
        assertFalse(scenario.refund("o-1", "0.01").isOk());
    }

    @Test
    void manySmallRefundsAddUpExactly() {
        scenario.order("o-1", "19.99", "19.99", OrderStatus.DELIVERED);

        for (int i = 0; i < 3; i++) {
            assertTrue(scenario.refund("o-1", "6.66").isOk(), "refund " + i);
        }
        scenario.assertRefunded("o-1", "19.98");

        assertFalse(scenario.refund("o-1", "0.02").isOk());
        assertTrue(scenario.refund("o-1", "0.01").isOk());
        scenario.assertRefunded("o-1", "19.99");
        assertFalse(scenario.refund("o-1", "0.01").isOk());
    }

    @Test
    void aLargeAmountKeepsItsCents() {
        scenario.order("o-1", "9999999999.99", "9999999999.99", OrderStatus.SHIPPED);

        assertTrue(scenario.refund("o-1", "9999999999.98").isOk());
        assertFalse(scenario.refund("o-1", "0.02").isOk());
        assertTrue(scenario.refund("o-1", "0.01").isOk());
        scenario.assertRefunded("o-1", "9999999999.99");
    }
}
