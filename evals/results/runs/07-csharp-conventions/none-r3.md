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
- `FirstOrDefaultAsync` needs `using Microsoft.Extensions.../Microsoft.EntityFrameworkCore;`, specifically `using Microsoft.EntityFrameworkCore;`.
- I assumed `Customer` has a `string Email` property. Adjust if it's a value object (e.g. `c.Email.Value == email`).
- Email matching uses the database collation. On SQL Server the default is case-insensitive; on others (e.g. PostgreSQL) it's case-sensitive. If you need consistent behavior, normalize emails on write and lookup (e.g. `ToUpperInvariant()` / a normalized column) rather than calling `ToLower()` inside the query, which defeats index use.
- Register it alongside the order repository: `services.AddScoped<ICustomerRepository, SqlCustomerRepository>();`