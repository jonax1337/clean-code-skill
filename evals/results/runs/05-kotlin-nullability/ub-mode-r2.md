## Refactored code

```kotlin
class UserService(private val repo: UserRepository) {
    fun displayName(id: Long): String? =
        repo.findById(id)?.let(::displayNameOf)
}

private fun displayNameOf(user: User): String =
    user.nickname?.takeIf { it.isNotBlank() } ?: "${user.firstName} ${user.lastName}"
```

## Pinning tests (write these first, they should pass before and after)

I haven't seen `User` or `UserRepository`, so the constructor and fake below are assumptions. Adjust them to your real types.

```kotlin
class UserServiceTest {
    private fun serviceWith(user: User?) =
        UserService(object : UserRepository {
            override fun findById(id: Long): User? = user
        })

    @Test fun `unknown user gives null`() =
        assertNull(serviceWith(null).displayName(1))

    @Test fun `nickname wins when present`() =
        assertEquals("Bobby", serviceWith(User("Bob", "Smith", "Bobby")).displayName(1))

    @Test fun `null nickname falls back to full name`() =
        assertEquals("Bob Smith", serviceWith(User("Bob", "Smith", null)).displayName(1))

    @Test fun `blank nickname falls back to full name`() =
        assertEquals("Bob Smith", serviceWith(User("Bob", "Smith", "   ")).displayName(1))
}
```

## What changed and why

- **Null handling:** the `if (user == null) return null` guard became `?.let`. The null case is now handled by the type system instead of a manual check.
- **Nickname check:** `nickname != null && nickname.isNotBlank()` became `takeIf { it.isNotBlank() }` with `?:`. This states the rule once: use the nickname if it is usable, otherwise use the full name.
- **String building:** `+` concatenation became a string template.
- **Pure function:** the naming rule is now `displayNameOf`, a pure function that takes a `User` and returns a `String`. The service only does the lookup. The rule can be tested without a repository.
- **Behavior:** unchanged. A non-blank nickname is still returned untrimmed, and a blank one still falls back to the full name.

## Action log

1. Read the class and identified three smells: a manual null guard, a repeated null check on `nickname`, and lookup mixed with naming logic.
2. Chose pinning tests before restructuring, since this is a refactor and behavior must not change.
3. Made the smallest structural edit: an expression body plus one extracted pure function.
4. Kept `displayNameOf` private. Nothing else needs it, so no new public surface.

## Not done

- I couldn't run anything here, so the tests and the refactor are unexecuted. Run the tests against the old version first, then the new one.
- The crapper, dryer and mutator tools from the skill weren't available. The function is now trivially under CRAP 10, but mutation testing is still outstanding.
- No commit was made, since this directory isn't a git repository.