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

    @Test
    void studentsGetTenPercent() {
        assertRate("0.10", new Customer("Sam", CustomerType.STUDENT, 0));
        assertRate("0.10", new Customer("Sam", CustomerType.STUDENT, 499));
    }

    @Test
    void studentGetsTheLargerOfStudentAndLoyaltyDiscount() {
        assertRate("0.10", new Customer("Sam", CustomerType.STUDENT, 500));
        assertRate("0.10", new Customer("Sam", CustomerType.STUDENT, 1999));
        assertRate("0.15", new Customer("Sam", CustomerType.STUDENT, 2000));
    }

    private void assertRate(String expected, Customer customer) {
        assertEquals(0, new BigDecimal(expected).compareTo(policy.rateFor(customer)));
    }
}
