package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class ValidatorTest {

    @Test
    void acceptsTextAndMoney() {
        Validator validator = new Validator().requireText("name", "x").requireMoney("amount", new BigDecimal("0.10"));

        assertTrue(validator.isValid());
    }

    @Test
    void rejectsBlankText() {
        assertFalse(new Validator().requireText("name", "  ").isValid());
        assertFalse(new Validator().requireText("name", null).isValid());
    }

    @Test
    void rejectsMoneyThatIsMissingNotPositiveOrTooPrecise() {
        assertFalse(new Validator().requireMoney("amount", null).isValid());
        assertFalse(new Validator().requireMoney("amount", BigDecimal.ZERO).isValid());
        assertFalse(new Validator().requireMoney("amount", new BigDecimal("-5.00")).isValid());
        assertFalse(new Validator().requireMoney("amount", new BigDecimal("1.005")).isValid());
        assertTrue(new Validator().requireMoney("amount", new BigDecimal("1.500")).isValid());
    }

    @Test
    void failureNamesEveryProblem() {
        Result<Order> result = new Validator().requireText("name", "").requireMoney("amount", null).failure();

        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
        assertTrue(result.error().message().contains("name"));
        assertTrue(result.error().message().contains("amount"));
    }
}
