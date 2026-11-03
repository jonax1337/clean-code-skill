package pricing;

import java.math.BigDecimal;

public record Quote(BigDecimal subtotal, BigDecimal discount, BigDecimal tax, BigDecimal total) {
}
