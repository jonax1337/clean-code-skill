package pricing;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;

class ReceiptFormatterTest {
    private final PriceCalculator calculator = new PriceCalculator(new DiscountPolicy());
    private final ReceiptFormatter formatter = new ReceiptFormatter();

    @Test
    void receiptListsLinesAndTotals() {
        Product pen = new Product("PN-1", "Pen", new BigDecimal("2.50"));
        Order order = new Order(new Customer("Eve", CustomerType.EMPLOYEE, 0), List.of(new OrderLine(pen, 4)));

        String receipt = formatter.format(order, calculator.quote(order));

        assertTrue(receipt.startsWith("Receipt for Eve (employee)"));
        assertTrue(receipt.contains("4 x Pen  10.00"));
        assertTrue(receipt.contains("-2.00"));
    }
}
