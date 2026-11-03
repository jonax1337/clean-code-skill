package pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class DiscountPolicyTest {
    private final DiscountPolicy policy = new DiscountPolicy();

    @Test
    void regularCustomerWithoutPointsGetsNoDiscount() {
        assertRate("0", new Customer("Ada", CustomerType.REGULAR, 0));
    }

    @Test
    void silverLoyaltyStartsAtFiveHundredPoints() {
        assertRate("0", new Customer("Ada", CustomerType.REGULAR, 499));
        assertRate("0.05", new Customer("Ada", CustomerType.REGULAR, 500));
    }

    @Test
    void goldLoyaltyStartsAtTwoThousandPoints() {
        assertRate("0.05", new Customer("Ada", CustomerType.REGULAR, 1999));
        assertRate("0.15", new Customer("Ada", CustomerType.REGULAR, 2000));
    }

    @Test
    void employeesGetTwentyPercent() {
        assertRate("0.20", new Customer("Eve", CustomerType.EMPLOYEE, 0));
    }

    private void assertRate(String expected, Customer customer) {
        assertEquals(0, new BigDecimal(expected).compareTo(policy.rateFor(customer)));
    }
}
