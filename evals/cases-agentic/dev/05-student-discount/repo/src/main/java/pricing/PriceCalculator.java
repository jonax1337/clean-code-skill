package pricing;

import java.math.BigDecimal;

public class PriceCalculator {
    private static final BigDecimal TAX_RATE = new BigDecimal("0.19");

    private final DiscountPolicy discountPolicy;

    public PriceCalculator(DiscountPolicy discountPolicy) {
        this.discountPolicy = discountPolicy;
    }

    public Quote quote(Order order) {
        BigDecimal subtotal = order.subtotal();
        BigDecimal discount = discountOn(subtotal, order.customer());
        BigDecimal taxable = subtotal.subtract(discount);
        BigDecimal tax = Money.round(taxable.multiply(TAX_RATE));
        return new Quote(subtotal, discount, tax, taxable.add(tax));
    }

    /** The price of one unit as listed in the catalog for this customer, before tax. */
    public BigDecimal discountedUnitPrice(Customer customer, Product product) {
        BigDecimal unitPrice = Money.round(product.unitPrice());
        return unitPrice.subtract(discountOn(unitPrice, customer));
    }

    private BigDecimal discountOn(BigDecimal amount, Customer customer) {
        return Money.round(amount.multiply(discountPolicy.rateFor(customer)));
    }
}
