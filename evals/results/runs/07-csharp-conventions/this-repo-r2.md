Here is the customer repository, mirroring the order one:

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

Notes:

- **Naming:** I used `GetByEmailAsync` rather than `FindByEmailAsync` to match the existing `GetByIdAsync`.
- **Assumption:** `Customer` has a string `Email` property and a `Guid` key. I haven't seen the entity, so adjust if it differs.
- **Case sensitivity:** `c.Email == email` is translated to SQL, so whether it is case-insensitive depends on the column collation. SQL Server's default collation is case-insensitive, while PostgreSQL and SQLite are case-sensitive. If emails are normalized on write (for example lowercased), normalize the argument the same way. I didn't add that, since I don't know your convention.
- **Uniqueness:** I used `FirstOrDefaultAsync`. If emails are unique, a unique index on `Email` is worth having for both integrity and lookup speed. You could then switch to `SingleOrDefaultAsync` so duplicates fail loudly.
- **Tracking:** like `FindAsync`, the result is tracked, so you can modify it and save.
- **Not run:** I couldn't build or run anything here, so this is uncompiled and untested. I'd add tests against SQLite or the EF in-memory provider covering: found by id, not found, found by email, unknown email, and `AddAsync` persisting the customer. If you have existing tests for `SqlOrderRepository`, they're a good template.