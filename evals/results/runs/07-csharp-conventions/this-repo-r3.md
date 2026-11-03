```csharp
using Microsoft.EntityFrameworkCore;

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
        _db.Set<Customer>().FirstOrDefaultAsync(c => c.Email == email, ct);

    public async Task AddAsync(Customer customer, CancellationToken ct)
    {
        _db.Add(customer);
        await _db.SaveChangesAsync(ct);
    }
}
```

**What I did:** `ICustomerRepository` and `SqlCustomerRepository` mirror the order versions (same constructor, same `GetByIdAsync` and `AddAsync`). `GetByEmailAsync` is the only addition. It returns `null` when there is no match, like `GetByIdAsync`. It tracks the entity, so a caller can modify the result and save it.

**Assumptions to check:**
- `Customer` has a string `Email` property. I couldn't see the entity, so I assumed this.
- Case sensitivity of the email match is decided by the database collation. SQL Server's default is case-insensitive, but PostgreSQL's is case-sensitive. If emails can differ in case, normalize them on write and on lookup, or use a case-insensitive column.
- I used `FirstOrDefaultAsync`. If you have a unique index on `Email` (you probably should), it behaves the same as `SingleOrDefaultAsync`.

**Not done:** I couldn't compile or run anything here, and I didn't add tests or DI registration, since I haven't seen your test project or composition root. If you have repository tests for orders, the same shape applies here. I'd add one for `GetByEmailAsync` covering found, not found, and different casing.