package shop;

import java.math.BigDecimal;

public record RefundOrder(String orderId, BigDecimal amount) {}
