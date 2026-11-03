package pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;

class StudentAndLoyaltyTest {
    private final DiscountPolicy policy = new DiscountPolicy();
    private final PriceCalculator calculator = new PriceCalculator(policy);

    @Test
    void studentWithSilverLoyaltyGetsTheStudentDiscount() {
        assertRate("0.10", student(500));
        assertRate("0.10", student(1999));
        assertQuote(student(500), "100.00", "10.00", "17.10", "107.10");
    }

    @Test
    void studentWithGoldLoyaltyGetsTheLoyaltyDiscount() {
        assertRate("0.15", student(2000));
        assertRate("0.15", student(100_000));
        assertQuote(student(2000), "100.00", "15.00", "16.15", "101.15");
    }

    @Test
    void discountsDoNotStack() {
        assertQuote(student(2000), "100.00", "15.00", "16.15", "101.15");
        assertQuote(student(500), "100.00", "10.00", "17.10", "107.10");
    }

    @Test
    void loyaltyDiscountIsRoundedHalfUpForStudents() {
        assertQuote(student(2000), "10.05", "1.51", "1.62", "10.16");
    }

    @Test
    void catalogPriceUsesTheLargerDiscount() {
        Product jacket = new Product("JK-1", "Jacket", new BigDecimal("24.95"));

        assertEquals("22.45", calculator.discountedUnitPrice(student(500), jacket).toPlainString());
        assertEquals("21.21", calculator.discountedUnitPrice(student(2000), jacket).toPlainString());
    }

    @Test
    void employeeDiscountIsNotAffectedByLoyaltyPoints() {
        Customer employee = new Customer("Eve", CustomerType.EMPLOYEE, 2000);

        assertRate("0.20", employee);
        assertQuote(employee, "100.00", "20.00", "15.20", "95.20");
    }

    private static Customer student(int loyaltyPoints) {
        return new Customer("Ada", CustomerType.valueOf("STUDENT"), loyaltyPoints);
    }

    private void assertRate(String expected, Customer customer) {
        assertEquals(0, new BigDecimal(expected).compareTo(policy.rateFor(customer)));
    }

    private void assertQuote(Customer customer, String unitPrice, String discount, String tax, String total) {
        Product product = new Product("P-1", "Item", new BigDecimal(unitPrice));
        Quote quote = calculator.quote(new Order(customer, List.of(new OrderLine(product, 1))));

        assertEquals(unitPrice, quote.subtotal().toPlainString());
        assertEquals(discount, quote.discount().toPlainString());
        assertEquals(tax, quote.tax().toPlainString());
        assertEquals(total, quote.total().toPlainString());
    }
}
