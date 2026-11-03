package pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class MoneyTest {

    @Test
    void roundsHalfUpToTwoDecimals() {
        assertEquals("1.01", Money.round(new BigDecimal("1.005")).toPlainString());
        assertEquals("1.00", Money.round(new BigDecimal("1.004")).toPlainString());
    }

    @Test
    void zeroHasTwoDecimals() {
        assertEquals("0.00", Money.ZERO.toPlainString());
    }
}
