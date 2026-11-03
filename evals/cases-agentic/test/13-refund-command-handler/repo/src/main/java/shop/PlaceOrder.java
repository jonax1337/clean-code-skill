package shop;

import java.math.BigDecimal;

public record PlaceOrder(String orderId, String customerId, BigDecimal total) {}
