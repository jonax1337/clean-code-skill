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

- `FirstOrDefaultAsync` needs `using Microsoft.EntityFrameworkCore;` (you likely already have it for `DbContext`).
- I assumed `Customer` has a `string Email` property. Adjust if it's a value object (e.g. `c.Email.Value == email`).
- Email matching is as case-sensitive as your database collation. SQL Server's default is case-insensitive, but PostgreSQL's is case-sensitive. If that matters, normalize emails on write and lookup (e.g. `email.Trim().ToLowerInvariant()`), or use a case-insensitive column/collation.
- Add a unique index on `Email` in your model configuration (`builder.HasIndex(c => c.Email).IsUnique();`) so lookups are fast and duplicates are prevented.
- Register it alongside the order repository: `services.AddScoped<ICustomerRepository, SqlCustomerRepository>();`