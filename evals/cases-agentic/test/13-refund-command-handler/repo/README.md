# Order service

A small order service built around commands. Every command is a record, every command has exactly one handler
class, and handlers talk to orders through an `OrderRepository`. Handlers report expected problems (bad input,
unknown order, wrong status) as a failed `Result`; they do not throw.

## Commands

| Command        | Handler               | Moves the order from              |
|----------------|-----------------------|-----------------------------------|
| `PlaceOrder`   | `PlaceOrderHandler`   | (new) to `PLACED`                 |
| `PayOrder`     | `PayOrderHandler`     | `PLACED` to `PAID`                |
| `ShipOrder`    | `ShipOrderHandler`    | `PAID` to `SHIPPED`               |
| `DeliverOrder` | `DeliverOrderHandler` | `SHIPPED` to `DELIVERED`          |
| `CancelOrder`  | `CancelOrderHandler`  | `PLACED` or `PAID` to `CANCELLED` |

All handlers are registered in `OrderServices.createBus`. Commands are sent through `CommandBus.dispatch`.

An order's amount paid can be lower than its total, for example when a voucher covered part of it. Money is
`BigDecimal` with at most two decimal places.

## Tests

`java tools/RunTests.java` compiles `src/main` and `src/test` into `build/` and runs all JUnit 5 tests with the
console launcher in `lib/`. It needs a JDK (17 or newer).
