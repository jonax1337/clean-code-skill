Here is the customer version, mirroring the order repository, with `GetByEmailAsync` added:

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

    public Task<Customer?> GetByEmailAsync(string email, CancellationToken ct)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(email);

        return _db.Set<Customer>()
            .FirstOrDefaultAsync(customer => customer.Email == email, ct);
    }

    public async Task AddAsync(Customer customer, CancellationToken ct)
    {
        _db.Add(customer);
        await _db.SaveChangesAsync(ct);
    }
}
```

`FirstOrDefaultAsync` needs `using Microsoft.EntityFrameworkCore;`.

Notes:

- **Assumption about `Customer.Email`:** I assumed it is a plain `string` property. If it's a value object (e.g. `EmailAddress`), the lookup should take that type instead, and the comparison may need to change depending on how it's mapped.
- **Case sensitivity:** `==` is translated to SQL, so whether `Jo@x.com` matches `jo@x.com` depends on your column collation. SQL Server's default is case-insensitive, but PostgreSQL's is case-sensitive. If you need case-insensitive matching everywhere, the cleanest fix is to store emails normalized (e.g. lowercased) and normalize the argument the same way before querying.
- **Uniqueness:** `FirstOrDefaultAsync` will quietly return one row if duplicates exist. A unique index on `Email` would make the "find by email" contract reliable.
- **Null handling:** I guard against a null or blank email, since that's almost certainly a caller bug and would otherwise produce a pointless query. Drop that line if you'd rather it just return `null`.
- **Registration:** remember to register `ICustomerRepository` → `SqlCustomerRepository` in DI alongside the order repository.

I haven't compiled this or written tests. If you'd like, I can add tests for `GetByEmailAsync` (found, not found, blank input) using the EF Core in-memory or SQLite provider.