package pricing;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** Money is a {@link BigDecimal} with two decimals, rounded half up. Every amount in the library goes through here. */
public final class Money {
    private static final int SCALE = 2;
    private static final RoundingMode ROUNDING = RoundingMode.HALF_UP;

    public static final BigDecimal ZERO = round(BigDecimal.ZERO);

    private Money() {
    }

    public static BigDecimal round(BigDecimal amount) {
        return amount.setScale(SCALE, ROUNDING);
    }
}
