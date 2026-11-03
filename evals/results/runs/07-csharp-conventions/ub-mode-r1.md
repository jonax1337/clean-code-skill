I couldn't run anything here, so none of this has been compiled or run. I assumed `Customer` has a `Guid Id` and a `string Email`, since the entity wasn't shown.

## 1. Failing test first

```csharp
public sealed class SqlCustomerRepositoryTests
{
    private sealed class TestDb : DbContext
    {
        private readonly string _name;
        public TestDb(string name) => _name = name;
        public DbSet<Customer> Customers => Set<Customer>();
        protected override void OnConfiguring(DbContextOptionsBuilder o) =>
            o.UseInMemoryDatabase(_name);
    }

    private static SqlCustomerRepository RepoOn(string dbName) =>
        new(new TestDb(dbName));

    [Fact]
    public async Task Added_customer_can_be_found_by_id_from_a_fresh_context()
    {
        var name = Guid.NewGuid().ToString();
        var customer = new Customer { Id = Guid.NewGuid(), Email = "ada@example.com" };

        await RepoOn(name).AddAsync(customer, default);
        var found = await RepoOn(name).GetByIdAsync(customer.Id, default);

        Assert.Equal("ada@example.com", found?.Email);
    }

    [Fact]
    public async Task Finds_customer_by_email()
    {
        var name = Guid.NewGuid().ToString();
        var customer = new Customer { Id = Guid.NewGuid(), Email = "ada@example.com" };
        await RepoOn(name).AddAsync(customer, default);

        var found = await RepoOn(name).FindByEmailAsync("ada@example.com", default);

        Assert.Equal(customer.Id, found?.Id);
    }

    [Fact]
    public async Task Returns_null_for_unknown_email()
    {
        var found = await RepoOn(Guid.NewGuid().ToString())
            .FindByEmailAsync("nobody@example.com", default);

        Assert.Null(found);
    }
}
```

These fail at compile time because `SqlCustomerRepository` doesn't exist yet. That is the expected reason.

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

Register it next to the order repository, for example `services.AddScoped<ICustomerRepository, SqlCustomerRepository>();`.

## Notes

- **Email matching:** `==` follows the database collation. SQL Server is case-insensitive by default, while the in-memory provider and Postgres are case-sensitive. If you want case-insensitive lookup everywhere, normalize emails to one form (for example lowercase) where they enter the system, and normalize the argument the same way. Also add a unique index on `Email`, since `FirstOrDefault` would otherwise silently pick one of several matches.
- **Duplication:** `GetByIdAsync` and `AddAsync` are now identical in both repositories apart from the type. I kept them as written to keep the edit small. If the dryer tool ranks them 0.8 or higher, a generic `SqlRepository<T>` base would remove the duplication.
- **Tools:** I couldn't run crapper, dryer or mutator here. The new methods have no branching, so I expect their CRAP score to be low.

## Log

1. Wrote three behavior tests that go through the public repository API and read back through a fresh context, so they fail if persistence is a no-op.
2. Mirrored the order repository for customers, because that is the existing design and a smaller edit than a new abstraction.
3. Added `FindByEmailAsync` as a single query, so the email rule lives in one place.
4. Did not extract a generic base, because that is out of scope for the smallest edit; I flagged it instead.
5. Not done: running the tests, the quality tools, and the commit. Suggested commit message: "Add customer repository with email lookup; tests cover add, get by id, find by email, and unknown email."