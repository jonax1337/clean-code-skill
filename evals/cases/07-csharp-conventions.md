# Follow codebase conventions (C#)

Tests: ecosystem conventions over book rules (the `I` prefix), consistency (G11), scope discipline.

## Prompt

Here is our order repository. Add the same thing for customers, plus a method to find a customer by email.

```csharp
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(Guid id, CancellationToken ct);
    Task AddAsync(Order order, CancellationToken ct);
}

public sealed class SqlOrderRepository : IOrderRepository
{
    private readonly DbContext _db;

    public SqlOrderRepository(DbContext db) => _db = db;

    public Task<Order?> GetByIdAsync(Guid id, CancellationToken ct) =>
        _db.Set<Order>().FindAsync(new object[] { id }, ct).AsTask();

    public async Task AddAsync(Order order, CancellationToken ct)
    {
        _db.Add(order);
        await _db.SaveChangesAsync(ct);
    }
}
```

## Assertions

1. The new interface is named `ICustomerRepository` (keeps the `I` prefix convention of the codebase).
2. All new methods follow the existing pattern: `Async` suffix, `Task` return types and a `CancellationToken` parameter.
3. "Not found" for the email lookup returns `Customer?` (consistent with `GetByIdAsync`) rather than throwing.
4. The existing order repository is not modified (no generic base repository extracted from it, no renames).
5. The implementation follows the file's conventions (`sealed` class, `_db` field naming, expression-bodied members where the original uses them).
