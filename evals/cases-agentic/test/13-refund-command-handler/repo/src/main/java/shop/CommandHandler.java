package shop;

public interface CommandHandler<C> {

    Result<Order> handle(C command);
}
