package shop;

import java.util.HashMap;
import java.util.Map;

public final class CommandBus {
    private final Map<Class<?>, CommandHandler<?>> handlers = new HashMap<>();

    public <C> void register(Class<C> commandType, CommandHandler<C> handler) {
        if (handlers.putIfAbsent(commandType, handler) != null) {
            throw new IllegalStateException("Handler already registered for " + commandType.getSimpleName());
        }
    }

    @SuppressWarnings("unchecked")
    public <C> Result<Order> dispatch(C command) {
        CommandHandler<C> handler = (CommandHandler<C>) handlers.get(command.getClass());
        if (handler == null) {
            return Result.failure(
                    ErrorCode.INVALID_INPUT, "No handler registered for " + command.getClass().getSimpleName());
        }
        return handler.handle(command);
    }
}
