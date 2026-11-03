package pricing;

import java.math.BigDecimal;

/** Decides which discount rate a customer gets. */
public class DiscountPolicy {
    private static final BigDecimal EMPLOYEE_RATE = new BigDecimal("0.20");
    private static final BigDecimal STUDENT_RATE = new BigDecimal("0.10");
    private static final BigDecimal GOLD_RATE = new BigDecimal("0.15");
    private static final BigDecimal SILVER_RATE = new BigDecimal("0.05");
    private static final int GOLD_POINTS = 2000;
    private static final int SILVER_POINTS = 500;

    public BigDecimal rateFor(Customer customer) {
        return switch (customer.type()) {
            case EMPLOYEE -> EMPLOYEE_RATE;
            case STUDENT -> STUDENT_RATE.max(loyaltyRateFor(customer.loyaltyPoints()));
            case REGULAR -> loyaltyRateFor(customer.loyaltyPoints());
        };
    }

    private BigDecimal loyaltyRateFor(int loyaltyPoints) {
        if (loyaltyPoints >= GOLD_POINTS) {
            return GOLD_RATE;
        }
        if (loyaltyPoints >= SILVER_POINTS) {
            return SILVER_RATE;
        }
        return BigDecimal.ZERO;
    }
}
