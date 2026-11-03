Here is the customer version, mirroring the order repository:

```csharp
using Microsoft.EntityFrameworkCore;

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

Notes:

- **Assumptions:** `Customer` is an entity with a `Guid` key and a string `Email` property. I couldn't see it, so adjust if the names differ.
- **Consistency:** `FindByEmailAsync` returns `Customer?` when nothing matches, the same as `GetByIdAsync` does for orders. I used "Find" because that's your wording. If you'd rather match the existing `Get…Async` naming, rename it to `GetByEmailAsync`.
- **Email casing:** `==` is translated to SQL, so whether `Jane@x.com` matches `jane@x.com` depends on your column collation. SQL Server's default is case-insensitive, but PostgreSQL's is case-sensitive. If you need guaranteed case-insensitive lookup, store a normalized email (e.g. lowercased) and compare against that, rather than calling `ToLower()` in the query, which defeats index use.
- **Uniqueness:** `FirstOrDefaultAsync` quietly returns one row if duplicates exist. Put a unique index on `Email` in your model configuration so the lookup is unambiguous.
- **Tests:** I didn't add tests, since I can't run anything here. Useful cases are found, not found, and a different-casing email, ideally against the real provider rather than the in-memory one, because of the collation behavior above.