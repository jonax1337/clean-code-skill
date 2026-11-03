package shop;

import java.util.Objects;

/** The outcome of a command: the updated value, or a failure that says why the command was rejected. */
public final class Result<T> {

    public record Failure(ErrorCode code, String message) {}

    private final T value;
    private final Failure failure;

    private Result(T value, Failure failure) {
        this.value = value;
        this.failure = failure;
    }

    public static <T> Result<T> ok(T value) {
        return new Result<>(Objects.requireNonNull(value), null);
    }

    public static <T> Result<T> failure(ErrorCode code, String message) {
        return new Result<>(null, new Failure(code, message));
    }

    public boolean isOk() {
        return failure == null;
    }

    public T value() {
        if (failure != null) {
            throw new IllegalStateException("Result failed: " + failure.message());
        }
        return value;
    }

    public Failure error() {
        if (failure == null) {
            throw new IllegalStateException("Result is ok");
        }
        return failure;
    }
}
