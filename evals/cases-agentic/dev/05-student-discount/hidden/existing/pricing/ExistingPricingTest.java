package pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;

class ExistingPricingTest {
    private final DiscountPolicy policy = new DiscountPolicy();
    private final PriceCalculator calculator = new PriceCalculator(policy);

    @Test
    void regularRatesFollowTheLoyaltyThresholds() {
        assertRate("0", regular(0));
        assertRate("0", regular(499));
        assertRate("0.05", regular(500));
        assertRate("0.05", regular(1999));
        assertRate("0.15", regular(2000));
    }

    @Test
    void employeesGetTwentyPercentWhateverTheirPoints() {
        assertRate("0.20", new Customer("Eve", CustomerType.EMPLOYEE, 0));
        assertRate("0.20", new Customer("Eve", CustomerType.EMPLOYEE, 5000));
    }

    @Test
    void quotesRoundHalfUp() {
        assertQuote(regular(0), "0.05", 1, "0.05", "0.00", "0.01", "0.06");
        assertQuote(regular(500), "100.00", 1, "100.00", "5.00", "18.05", "113.05");
        assertQuote(new Customer("Eve", CustomerType.EMPLOYEE, 0), "10.05", 1, "10.05", "2.01", "1.53", "9.57");
    }

    @Test
    void quotesMultiplyByQuantity() {
        assertQuote(regular(2000), "19.99", 1000, "19990.00", "2998.50", "3228.39", "20219.89");
    }

    @Test
    void emptyOrderCostsNothing() {
        Quote quote = calculator.quote(new Order(regular(0), List.of()));

        assertEquals("0.00", quote.total().toPlainString());
    }

    @Test
    void catalogPricesFollowTheDiscount() {
        Product jacket = new Product("JK-1", "Jacket", new BigDecimal("24.95"));

        assertEquals("24.95", calculator.discountedUnitPrice(regular(0), jacket).toPlainString());
        assertEquals("23.70", calculator.discountedUnitPrice(regular(500), jacket).toPlainString());
        assertEquals("19.96", calculator.discountedUnitPrice(new Customer("Eve", CustomerType.EMPLOYEE, 0), jacket).toPlainString());
    }

    @Test
    void receiptNamesTheCustomerKind() {
        Product pen = new Product("PN-1", "Pen", new BigDecimal("2.50"));
        Order order = new Order(regular(0), List.of(new OrderLine(pen, 2)));

        String receipt = new ReceiptFormatter().format(order, calculator.quote(order));

        assertTrue(receipt.startsWith("Receipt for Ada (regular customer)"));
        assertTrue(receipt.contains("2 x Pen  5.00"));
    }

    private static Customer regular(int loyaltyPoints) {
        return new Customer("Ada", CustomerType.REGULAR, loyaltyPoints);
    }

    private void assertRate(String expected, Customer customer) {
        assertEquals(0, new BigDecimal(expected).compareTo(policy.rateFor(customer)));
    }

    private void assertQuote(
            Customer customer, String unitPrice, int quantity, String subtotal, String discount, String tax, String total) {
        Product product = new Product("P-1", "Item", new BigDecimal(unitPrice));
        Quote quote = calculator.quote(new Order(customer, List.of(new OrderLine(product, quantity))));

        assertEquals(subtotal, quote.subtotal().toPlainString());
        assertEquals(discount, quote.discount().toPlainString());
        assertEquals(tax, quote.tax().toPlainString());
        assertEquals(total, quote.total().toPlainString());
    }
}
