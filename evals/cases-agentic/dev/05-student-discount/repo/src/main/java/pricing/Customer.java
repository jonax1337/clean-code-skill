package pricing;

import java.util.Objects;

public record Customer(String name, CustomerType type, int loyaltyPoints) {

    public Customer {
        Objects.requireNonNull(name, "name");
        Objects.requireNonNull(type, "type");
        if (loyaltyPoints < 0) {
            throw new IllegalArgumentException("loyaltyPoints must not be negative: " + loyaltyPoints);
        }
    }
}
