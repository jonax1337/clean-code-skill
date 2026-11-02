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

- `GetByEmailAsync` uses `FirstOrDefaultAsync`, which needs `using Microsoft.EntityFrameworkCore;`. I assumed `Customer` has an `Email` string property.
- The comparison is translated to SQL, so case sensitivity follows the column collation. SQL Server's default is case-insensitive; PostgreSQL's is case-sensitive. If you need to guarantee case-insensitive matching, normalize emails on write and on lookup (e.g. `email.Trim().ToLowerInvariant()`), or store a normalized email column.
- Add a unique index on `Email` in your model configuration so lookups are fast and duplicates are prevented:

```csharp
modelBuilder.Entity<Customer>().HasIndex(c => c.Email).IsUnique();
```

- If you want read-only lookups, add `.AsNoTracking()` before `FirstOrDefaultAsync`. I left it tracked to match `GetByIdAsync`, which uses `FindAsync` and tracks the entity.
- Remember to register it in DI, e.g. `services.AddScoped<ICustomerRepository, SqlCustomerRepository>();`.