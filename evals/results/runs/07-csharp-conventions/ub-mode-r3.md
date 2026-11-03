I haven't run anything here, so none of this is compiled or tested. I assumed `Customer` has a `Guid Id` and a `string Email` that EF maps. Adjust the test setup if your `Customer` constructor or `DbContext` differs.

## 1. Failing test first

It fails to compile now because `SqlCustomerRepository` doesn't exist. It uses two contexts on one SQLite connection, so reads hit the database and not the change tracker.

```csharp
public sealed class SqlCustomerRepositoryTests : IDisposable
{
    private readonly SqliteConnection _conn = new("DataSource=:memory:");

    public SqlCustomerRepositoryTests()
    {
        _conn.Open();
        using var db = NewDb();
        db.Database.EnsureCreated();
    }

    private TestDbContext NewDb() =>
        new(new DbContextOptionsBuilder<TestDbContext>().UseSqlite(_conn).Options);

    [Fact]
    public async Task Added_customer_can_be_found_by_id_and_by_email()
    {
        var customer = new Customer { Id = Guid.NewGuid(), Email = "ada@example.com" };

        using (var write = NewDb())
            await new SqlCustomerRepository(write).AddAsync(customer, default);

        using var read = NewDb();
        var repo = new SqlCustomerRepository(read);

        Assert.Equal(customer.Id, (await repo.GetByIdAsync(customer.Id, default))?.Id);
        Assert.Equal(customer.Id, (await repo.GetByEmailAsync("ada@example.com", default))?.Id);
    }

    [Fact]
    public async Task Unknown_email_returns_null()
    {
        using var db = NewDb();
        Assert.Null(await new SqlCustomerRepository(db).GetByEmailAsync("nobody@example.com", default));
    }

    public void Dispose() => _conn.Dispose();
}

public sealed class TestDbContext : DbContext
{
    public TestDbContext(DbContextOptions<TestDbContext> o) : base(o) { }
    public DbSet<Customer> Customers => Set<Customer>();
}
```

## 2. Smallest change that makes it pass

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

## Notes

- **Email matching:** `==` is translated to SQL, so case sensitivity follows the column collation. SQL Server's default is case-insensitive and SQLite's is case-sensitive. If you need a specific rule, normalize emails once where they enter, for example in a parsed `Email` type, instead of lowercasing in queries.
- **Unique index:** Add a unique index on `Email`. The lookup then returns at most one row and stays fast. Right now `FirstOrDefaultAsync` would quietly pick one if duplicates existed.
- **Left for later:** I didn't extract a shared generic base for orders and customers. With two near-identical classes, a base class would be premature. Run the dryer tool once it exists and extract only if it ranks the duplication 0.8 or higher.

## Log

1. Wrote the failing test, which covers add, find by id, find by email, and unknown email, to pin the behavior before the code exists.
2. Added `ICustomerRepository` and `SqlCustomerRepository`, mirroring the order repository to keep the change small.
3. Implemented email lookup as a single query with no extra layers.
4. Not done in this session: running the tests, crapper, dryer and mutator, and committing and pushing. Suggested commit message: "Add customer repository with email lookup. Mirrors the order repository; covered by SQLite-backed repository tests."