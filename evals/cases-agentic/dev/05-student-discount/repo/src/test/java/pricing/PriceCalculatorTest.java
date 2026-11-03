package pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;

class PriceCalculatorTest {
    private final PriceCalculator calculator = new PriceCalculator(new DiscountPolicy());
    private final Product notebook = new Product("NB-1", "Notebook", new BigDecimal("10.05"));

    @Test
    void quoteWithoutDiscountAddsTax() {
        Quote quote = calculator.quote(order(CustomerType.REGULAR, 0, 1));

        assertQuote(quote, "10.05", "0.00", "1.91", "11.96");
    }

    @Test
    void quoteAppliesDiscountBeforeTax() {
        Quote quote = calculator.quote(order(CustomerType.EMPLOYEE, 0, 1));

        assertQuote(quote, "10.05", "2.01", "1.53", "9.57");
    }

    @Test
    void quoteMultipliesByQuantity() {
        Quote quote = calculator.quote(order(CustomerType.REGULAR, 2000, 3));

        assertQuote(quote, "30.15", "4.52", "4.87", "30.50");
    }

    @Test
    void emptyOrderCostsNothing() {
        Quote quote = calculator.quote(new Order(new Customer("Ada", CustomerType.REGULAR, 0), List.of()));

        assertQuote(quote, "0.00", "0.00", "0.00", "0.00");
    }

    @Test
    void catalogPriceIncludesCustomerDiscount() {
        Customer employee = new Customer("Eve", CustomerType.EMPLOYEE, 0);

        assertEquals("8.04", calculator.discountedUnitPrice(employee, notebook).toPlainString());
    }

    private Order order(CustomerType type, int loyaltyPoints, int quantity) {
        return new Order(new Customer("Ada", type, loyaltyPoints), List.of(new OrderLine(notebook, quantity)));
    }

    private static void assertQuote(Quote quote, String subtotal, String discount, String tax, String total) {
        assertEquals(subtotal, quote.subtotal().toPlainString());
        assertEquals(discount, quote.discount().toPlainString());
        assertEquals(tax, quote.tax().toPlainString());
        assertEquals(total, quote.total().toPlainString());
    }
}
