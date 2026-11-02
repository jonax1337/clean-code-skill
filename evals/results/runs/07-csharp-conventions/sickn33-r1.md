```csharp
public interface ICustomerRepository
{
    Task<Customer?> GetByIdAsync(Guid id, CancellationToken ct);
    Task<Customer?> FindByEmailAsync(string email, CancellationToken ct);
    Task AddAsync(Customer customer, CancellationToken ct);
}

public sealed class SqlCustomerRepository : ICustomerRepository
{
    private readonly DbContext _db;

    public SqlCustomerRepository(DbContext db) => _db = db;

    public Task<Customer?> GetByIdAsync(Guid id, CancellationToken ct) =>
        _db.Set<Customer>().FindAsync(new object[] { id }, ct).AsTask();

    public Task<Customer?> FindByEmailAsync(string email, CancellationToken ct) =>
        _db.Set<Customer>().FirstOrDefaultAsync(customer => customer.Email == email, ct);

    public async Task AddAsync(Customer customer, CancellationToken ct)
    {
        _db.Add(customer);
        await _db.SaveChangesAsync(ct);
    }
}
```

This needs `using Microsoft.EntityFrameworkCore;` for `FirstOrDefaultAsync`.

- **Same shape as the order repository.** `GetByIdAsync` and `AddAsync` mirror the originals, so the two repositories read the same way.
- **`FindByEmailAsync` naming.** It returns `null` when nothing matches, as `GetByIdAsync` does, and "Find" signals that a miss is normal.
- **Assumption about `Customer.Email`.** I assumed it's a `string` property. If it's a value object, change the comparison to match, for example `customer.Email == new EmailAddress(email)`.
- **Case sensitivity.** The comparison follows your database collation. SQL Server's default is case-insensitive, but other providers may not be. If you need case-insensitive matching regardless of collation, normalize emails when storing and querying. I left that out so as not to change behavior beyond what you asked.
- **Uniqueness.** `FirstOrDefaultAsync` assumes at most one customer per email. A unique index on `Email` would enforce that in the database.
- **DI registration.** Remember to register it, e.g. `services.AddScoped<ICustomerRepository, SqlCustomerRepository>();`.

I haven't compiled this or run any tests, since I can only see the code you pasted.