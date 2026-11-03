package pricing;

import java.math.BigDecimal;
import java.util.Objects;

public record OrderLine(Product product, int quantity) {

    public OrderLine {
        Objects.requireNonNull(product, "product");
        if (quantity <= 0) {
            throw new IllegalArgumentException("quantity must be positive: " + quantity);
        }
    }

    public BigDecimal subtotal() {
        return Money.round(product.unitPrice().multiply(BigDecimal.valueOf(quantity)));
    }
}
