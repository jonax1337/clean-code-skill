package pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;

class StudentDiscountTest {
    private final PriceCalculator calculator = new PriceCalculator(new DiscountPolicy());

    @Test
    void studentGetsTenPercentOffTheSubtotalBeforeTax() {
        assertQuote(student(0), "10.00", 1, "10.00", "1.00", "1.71", "10.71");
    }

    @Test
    void discountIsRoundedHalfUp() {
        assertQuote(student(0), "10.05", 1, "10.05", "1.01", "1.72", "10.76");
        assertQuote(student(0), "0.05", 1, "0.05", "0.01", "0.01", "0.05");
    }

    @Test
    void discountIsTakenFromTheWholeOrderNotPerLine() {
        Product sticker = new Product("ST-1", "Sticker", new BigDecimal("0.05"));
        Product pencil = new Product("PC-1", "Pencil", new BigDecimal("3.35"));
        Order order = new Order(student(0), List.of(new OrderLine(pencil, 3), new OrderLine(sticker, 1)));

        Quote quote = calculator.quote(order);

        assertEquals("10.10", quote.subtotal().toPlainString());
        assertEquals("1.01", quote.discount().toPlainString());
        assertEquals("1.73", quote.tax().toPlainString());
        assertEquals("10.82", quote.total().toPlainString());
    }

    @Test
    void studentWithFewLoyaltyPointsStillGetsTenPercent() {
        assertQuote(student(499), "10.00", 1, "10.00", "1.00", "1.71", "10.71");
    }

    @Test
    void catalogPriceIncludesStudentDiscount() {
        Product jacket = new Product("JK-1", "Jacket", new BigDecimal("24.95"));

        assertEquals("22.45", calculator.discountedUnitPrice(student(0), jacket).toPlainString());
    }

    @Test
    void receiptShowsStudentDiscount() {
        Product pen = new Product("PN-1", "Pen", new BigDecimal("10.00"));
        Order order = new Order(student(0), List.of(new OrderLine(pen, 1)));

        String receipt = new ReceiptFormatter().format(order, calculator.quote(order));

        assertTrue(receipt.contains("Ada"));
        assertTrue(receipt.contains("-1.00"));
    }

    @Test
    void discountPolicyGivesStudentsTenPercent() {
        assertEquals(0, new BigDecimal("0.10").compareTo(new DiscountPolicy().rateFor(student(0))));
    }

    private static Customer student(int loyaltyPoints) {
        return new Customer("Ada", CustomerType.valueOf("STUDENT"), loyaltyPoints);
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
