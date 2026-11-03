package shop;

import java.math.BigDecimal;

public final class Order {
    private final String id;
    private final String customerId;
    private final BigDecimal total;
    private OrderStatus status;
    private BigDecimal amountPaid;
    private BigDecimal amountRefunded;

    public Order(String id, String customerId, BigDecimal total) {
        this.id = id;
        this.customerId = customerId;
        this.total = total;
        this.status = OrderStatus.PLACED;
        this.amountPaid = BigDecimal.ZERO;
        this.amountRefunded = BigDecimal.ZERO;
    }

    private Order(Order other) {
        this.id = other.id;
        this.customerId = other.customerId;
        this.total = other.total;
        this.status = other.status;
        this.amountPaid = other.amountPaid;
        this.amountRefunded = other.amountRefunded;
    }

    /** A snapshot, so that a repository can hand out orders without sharing state with its stored copy. */
    public Order copy() {
        return new Order(this);
    }

    public String id() {
        return id;
    }

    public String customerId() {
        return customerId;
    }

    public BigDecimal total() {
        return total;
    }

    public OrderStatus status() {
        return status;
    }

    public BigDecimal amountPaid() {
        return amountPaid;
    }

    public BigDecimal amountRefunded() {
        return amountRefunded;
    }

    public void markPaid(BigDecimal amount) {
        this.status = OrderStatus.PAID;
        this.amountPaid = amount;
    }

    public void markShipped() {
        this.status = OrderStatus.SHIPPED;
    }

    public void markDelivered() {
        this.status = OrderStatus.DELIVERED;
    }

    public void cancel() {
        this.status = OrderStatus.CANCELLED;
    }

    public void recordRefund(BigDecimal amount) {
        this.amountRefunded = amountRefunded.add(amount);
    }
}
