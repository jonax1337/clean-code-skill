I haven't compiled or run any of this, and I assumed `Customer` has `Guid Id` and `string Email`. Per ub-mode, the tests come first.

## 1. Failing tests

```csharp
public sealed class SqlCustomerRepositoryTests
{
    private static DbContext NewDb()
    {
        var options = new DbContextOptionsBuilder<TestDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        return new TestDbContext(options); // your context with DbSet<Customer>
    }

    [Fact]
    public async Task AddAsync_then_GetByIdAsync_returns_the_customer()
    {
        var customer = new Customer { Id = Guid.NewGuid(), Email = "a@example.com" };
        var repo = new SqlCustomerRepository(NewDb());

        await repo.AddAsync(customer, CancellationToken.None);

        var found = await repo.GetByIdAsync(customer.Id, CancellationToken.None);
        Assert.Equal(customer.Id, found?.Id);
    }

    [Fact]
    public async Task FindByEmailAsync_returns_the_matching_customer()
    {
        var repo = new SqlCustomerRepository(NewDb());
        var a = new Customer { Id = Guid.NewGuid(), Email = "a@example.com" };
        var b = new Customer { Id = Guid.NewGuid(), Email = "b@example.com" };
        await repo.AddAsync(a, CancellationToken.None);
        await repo.AddAsync(b, CancellationToken.None);

        var found = await repo.FindByEmailAsync("b@example.com", CancellationToken.None);

        Assert.Equal(b.Id, found?.Id);
    }

    [Fact]
    public async Task FindByEmailAsync_returns_null_when_no_match()
    {
        var repo = new SqlCustomerRepository(NewDb());

        Assert.Null(await repo.FindByEmailAsync("nobody@example.com", CancellationToken.None));
    }
}
```

These fail at first because `SqlCustomerRepository` doesn't exist, which is the expected reason.

## 2. Smallest change that passes

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
        _db.Set<Customer>().FirstOrDefaultAsync(c => c.Email == email, ct);

    public async Task AddAsync(Customer customer, CancellationToken ct)
    {
        _db.Add(customer);
        await _db.SaveChangesAsync(ct);
    }
}
```

It mirrors the order repository, and `FindByEmailAsync` is the only addition.

## Things to decide

- **Email case:** `==` is translated to SQL, so case sensitivity follows the column collation. SQL Server's default is case-insensitive, but the InMemory provider is case-sensitive. If emails must match regardless of case, normalize them in one place, either when the `Customer` is created or in a value converter, rather than adding `ToLower()` to this query.
- **Uniqueness:** `FirstOrDefaultAsync` hides duplicates. A unique index on `Email` makes "one customer per email" a database guarantee. I'd add it as a separate migration, and the repository then needs no guard.
- **Test provider:** InMemory doesn't enforce constraints or collation. If you have SQLite or Testcontainers set up, swap that in for the email tests.

## Log

- Wrote the tests first so the new behavior is pinned, including the no-match case.
- Added the interface and class by mirroring `SqlOrderRepository`, adding only `FindByEmailAsync`.
- Left out a base generic repository. Two implementations don't justify it yet.
- Not done: running the tests, the Crapper, Dryer and Mutator tools, and commit/push. I have no tool access or git repo here. The new methods are trivial, so CRAP should be well under 10.