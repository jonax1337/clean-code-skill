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
        return _db.Set<Customer>().FirstOrDefaultAsync(c => c.Email == email, ct);
    }

    public async Task AddAsync(Customer customer, CancellationToken ct)
    {
        _db.Add(customer);
        await _db.SaveChangesAsync(ct);
    }
}
```

Notes:

- I mirrored the order repository's structure, naming, and nullable-return convention (`Customer?` when not found), so it stays consistent with the existing code.
- `GetByEmailAsync` needs `using Microsoft.EntityFrameworkCore;` for `FirstOrDefaultAsync`, if it's not already in scope.
- I assumed `Customer` has an `Email` property of type `string`. If it's a value object (e.g. `EmailAddress`), adjust the comparison and parameter type accordingly.
- Email matching is only as case-insensitive as your database collation. SQL Server's default is case-insensitive, but PostgreSQL's isn't. If you need guaranteed case-insensitivity, normalize emails on write and on lookup (e.g. store a lowercased value) rather than calling `ToLower()` in the query, which can defeat an index.
- You'll likely want a unique index on `Customer.Email` in your model configuration, both for lookup performance and to enforce one customer per email.
- I added a guard clause on `email` since passing null or blank is a caller bug; it throws instead of silently querying. Since the guard is synchronous, a bad argument throws at call time rather than on await, which is fine here.
- I didn't write tests since I can't run anything in this session, but a good set would cover: found by id, not found by id, found by email, not found by email, and the invalid-email guard.