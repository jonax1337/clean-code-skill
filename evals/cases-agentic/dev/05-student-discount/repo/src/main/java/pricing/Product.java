package pricing;

import java.math.BigDecimal;
import java.util.Objects;

public record Product(String sku, String name, BigDecimal unitPrice) {

    public Product {
        Objects.requireNonNull(sku, "sku");
        Objects.requireNonNull(name, "name");
        Objects.requireNonNull(unitPrice, "unitPrice");
        if (unitPrice.signum() < 0) {
            throw new IllegalArgumentException("unitPrice must not be negative: " + unitPrice);
        }
    }
}
