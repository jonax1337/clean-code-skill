package shop;

import java.math.BigDecimal;

public record PayOrder(String orderId, BigDecimal amount) {}
