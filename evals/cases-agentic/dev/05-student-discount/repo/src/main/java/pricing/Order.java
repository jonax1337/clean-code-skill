package pricing;

import java.math.BigDecimal;
import java.util.List;
import java.util.Objects;

public record Order(Customer customer, List<OrderLine> lines) {

    public Order {
        Objects.requireNonNull(customer, "customer");
        lines = List.copyOf(lines);
    }

    public BigDecimal subtotal() {
        return lines.stream().map(OrderLine::subtotal).reduce(Money.ZERO, BigDecimal::add);
    }
}
