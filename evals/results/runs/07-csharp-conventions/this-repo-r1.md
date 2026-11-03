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

- **Naming:** I used `GetByEmailAsync` rather than "Find" so it matches `GetByIdAsync`. Rename it if you prefer.
- **Assumptions:** `Customer` has a `string Email` property. If your model uses an email value object, the predicate and parameter type need to change.
- **Case sensitivity:** `c.Email == email` is translated to SQL, so whether `Bob@x.com` matches `bob@x.com` depends on the column collation. SQL Server's default is case-insensitive, while PostgreSQL's is case-sensitive. If you need case-insensitive matching everywhere, the safest fix is to store emails normalized (for example lowercased on write) and normalize the argument the same way. I didn't add that because it changes how `Customer` is written, which goes beyond this request.
- **Duplicates:** I used `FirstOrDefaultAsync` so duplicate emails don't throw. If email is unique, add a unique index on it. That also keeps the lookup fast.
- **Registration and tests:** I haven't seen your DI setup or test project, so I didn't register `ICustomerRepository` or add tests. I also haven't compiled or run anything. The tests I'd add are: found by email, not found returns null, and `AddAsync` followed by a lookup by id and by email.