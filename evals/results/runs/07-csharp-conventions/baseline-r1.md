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

- `GetByEmailAsync` uses `FirstOrDefaultAsync`, which needs `using Microsoft.EntityFrameworkCore;`. It assumes `Customer` has an `Email` property of type `string`.
- Email matching is as case-sensitive as your database collation. SQL Server's default is case-insensitive, but PostgreSQL's is case-sensitive. If you need consistent behavior, normalize emails on write (e.g. store lowercase) and compare against `email.ToLowerInvariant()`, or use a case-insensitive collation on the column.
- Consider a unique index on `Customer.Email` so lookups are fast and duplicates can't occur:

  ```csharp
  modelBuilder.Entity<Customer>().HasIndex(c => c.Email).IsUnique();
  ```

- If the result is only read, not modified, you can add `.AsNoTracking()` before `FirstOrDefaultAsync` to skip change tracking.