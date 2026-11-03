package pricing;

import java.math.BigDecimal;

public class ReceiptFormatter {

    public String format(Order order, Quote quote) {
        StringBuilder receipt = new StringBuilder();
        receipt.append("Receipt for ").append(order.customer().name())
                .append(" (").append(label(order.customer().type())).append(")\n");
        for (OrderLine line : order.lines()) {
            receipt.append(line.quantity()).append(" x ").append(line.product().name())
                    .append("  ").append(line.subtotal().toPlainString()).append('\n');
        }
        appendAmount(receipt, "Subtotal", quote.subtotal());
        appendAmount(receipt, "Discount", quote.discount().negate());
        appendAmount(receipt, "Tax", quote.tax());
        appendAmount(receipt, "Total", quote.total());
        return receipt.toString();
    }

    private static String label(CustomerType type) {
        return switch (type) {
            case REGULAR -> "regular customer";
            case EMPLOYEE -> "employee";
            case STUDENT -> "student";
        };
    }

    private static void appendAmount(StringBuilder receipt, String label, BigDecimal amount) {
        receipt.append(String.format("%-10s%10s%n", label, amount.toPlainString()));
    }
}
