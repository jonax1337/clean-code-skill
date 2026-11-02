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

- `GetByEmailAsync` uses `FirstOrDefaultAsync`, which needs `using Microsoft.EntityFrameworkCore;`. If you expect email to be unique, consider a unique index on `Customer.Email` in your model configuration.
- The comparison `c.Email == email` is case-sensitive or not depending on your database collation (SQL Server is case-insensitive by default; PostgreSQL is case-sensitive). If you need consistent behavior, normalize emails (e.g. trim and lowercase) on write and on lookup, and use `AsNoTracking()` if you only need read access.
- I assumed `Customer` has a `string Email` property and a `Guid` key, mirroring `Order`. Adjust if your entity differs.
- Register it in DI alongside the order repository, e.g. `services.AddScoped<ICustomerRepository, SqlCustomerRepository>();`.