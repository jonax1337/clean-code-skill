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
        _db.Set<Customer>().FirstOrDefaultAsync(c => c.Email == email, ct);

    public async Task AddAsync(Customer customer, CancellationToken ct)
    {
        _db.Add(customer);
        await _db.SaveChangesAsync(ct);
    }
}
```

Notes:

- `GetByEmailAsync` uses `FirstOrDefaultAsync`, which needs `using Microsoft.EntityFrameworkCore;`. If `Email` has a unique index, `SingleOrDefaultAsync` would also work, but `FirstOrDefaultAsync` avoids the extra row fetch.
- Email matching follows the database collation. SQL Server is case-insensitive by default; PostgreSQL is case-sensitive. If you need consistent behavior, normalize emails on write (e.g. lowercase) and compare against `email.ToLowerInvariant()`, or configure a case-insensitive collation on the column.
- I assumed `Customer` has an `Email` string property and a `Guid` key. Adjust if yours differ.
- For read-only lookups you could add `.AsNoTracking()` to the email query, but I kept it consistent with `GetByIdAsync`, which returns a tracked entity.