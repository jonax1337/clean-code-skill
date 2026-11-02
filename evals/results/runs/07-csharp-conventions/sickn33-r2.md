```csharp
public interface ICustomerRepository
{
    Task<Customer?> GetByIdAsync(Guid id, CancellationToken ct);
    Task<Customer?> GetByEmailAsync(string email, CancellationToken ct);
    Task AddAsync(Customer customer, CancellationToken ct);
}

public sealed class SqlCustomerRepository : ICustomerRepository
{
    private readonly DbContext _db;

    public SqlCustomerRepository(DbContext db) => _db = db;

    public Task<Customer?> GetByIdAsync(Guid id, CancellationToken ct) =>
        _db.Set<Customer>().FindAsync(new object[] { id }, ct).AsTask();

    public Task<Customer?> GetByEmailAsync(string email, CancellationToken ct) =>
        _db.Set<Customer>().SingleOrDefaultAsync(c => c.Email == email, ct);

    public async Task AddAsync(Customer customer, CancellationToken ct)
    {
        _db.Add(customer);
        await _db.SaveChangesAsync(ct);
    }
}
```

You'll need `using Microsoft.EntityFrameworkCore;` for `SingleOrDefaultAsync`.

Notes:

- **Mirrors the order repository**: same constructor injection, same `Task<T?>` return for "not found" (no exceptions for a missing row), same `AddAsync` that saves immediately.
- **`SingleOrDefaultAsync`** is used rather than `FirstOrDefaultAsync` because email should be unique. If duplicates ever exist, it throws instead of silently picking one. I'd also back this with a unique index on `Email` in your model configuration.
- **Assumption**: `Customer.Email` is a plain `string`. If it's a value object or has a converter, the predicate needs adjusting.
- **Case sensitivity**: the comparison follows the database collation (SQL Server is case-insensitive by default, others aren't). If you need consistent behavior, normalize emails (for example, trim and lowercase) when storing and querying. I left that out since it changes behavior beyond what you asked for.
- **Registration**: add `services.AddScoped<ICustomerRepository, SqlCustomerRepository>();` alongside the order repository registration.

I haven't compiled this or written tests, since I can't run anything here. A focused test for `GetByEmailAsync` (found, not found, and duplicate emails) would be worth adding, for example against the EF Core in-memory or SQLite provider.