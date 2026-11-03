package shop;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/** Collects the problems of a command's input so that a handler can reject it with one failed result. */
public final class Validator {
    private static final int MONEY_SCALE = 2;

    private final List<String> problems = new ArrayList<>();

    public Validator requireText(String field, String value) {
        if (value == null || value.isBlank()) {
            problems.add(field + " must not be blank");
        }
        return this;
    }

    public Validator requireMoney(String field, BigDecimal value) {
        if (value == null) {
            problems.add(field + " is required");
        } else if (value.signum() <= 0) {
            problems.add(field + " must be greater than zero");
        } else if (value.stripTrailingZeros().scale() > MONEY_SCALE) {
            problems.add(field + " must have at most two decimal places");
        }
        return this;
    }

    public boolean isValid() {
        return problems.isEmpty();
    }

    public <T> Result<T> failure() {
        return Result.failure(ErrorCode.INVALID_INPUT, String.join("; ", problems));
    }
}
