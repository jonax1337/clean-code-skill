## Tests first (pin current behavior)

These pass against the old code and must still pass after the refactor. I assumed `User(id, firstName, lastName, nickname)` and `UserRepository.findById(Long): User?`, so adjust them to your real types.

```kotlin
class UserServiceTest {
    private fun serviceWith(user: User?) = UserService(object : UserRepository {
        override fun findById(id: Long): User? = user
    })

    private fun user(nickname: String?) = User(1, "Ada", "Lovelace", nickname)

    @Test fun `unknown user has no display name`() =
        assertNull(serviceWith(null).displayName(1))

    @Test fun `nickname wins when present`() =
        assertEquals("Countess", serviceWith(user("Countess")).displayName(1))

    @Test fun `null nickname falls back to full name`() =
        assertEquals("Ada Lovelace", serviceWith(user(null)).displayName(1))

    @Test fun `blank nickname falls back to full name`() =
        assertEquals("Ada Lovelace", serviceWith(user("   ")).displayName(1))
}
```

## Refactor

```kotlin
class UserService(private val repo: UserRepository) {
    fun displayName(id: Long): String? = repo.findById(id)?.displayName()
}

private fun User.displayName(): String =
    nickname?.takeIf { it.isNotBlank() } ?: "$firstName $lastName"
```

## What changed and why

- **The early-return null check became `?.`.** Absence is handled by the type, so the lookup is one expression.
- **The naming rule is now a pure function on `User`.** It has no repository dependency, so it's easy to test and reuse. `UserService` only does the lookup.
- **`nickname?.takeIf { it.isNotBlank() }` replaces `!= null && isNotBlank()`.** The null and blank checks are one decision in one place. It also no longer relies on a smart cast of `user.nickname`, which breaks if `nickname` is a `var` or comes from another module.
- **The string template replaces `+` concatenation.** Behavior is the same.
- **Public API is unchanged:** `displayName(id: Long): String?`.

## Action log

1. Wrote four behavior tests covering missing user, nickname, null nickname and blank nickname, so the refactor is pinned.
2. Replaced the null check with a safe call and extracted `User.displayName()`.
3. Replaced the null-and-blank check with `takeIf`, and the concatenation with a template.

## Not done

I can't run anything here, so I haven't run the tests, or crapper, dryer or mutator. At this size the function is well under CRAP 10 with nothing to deduplicate, so I expect no findings, but that is unconfirmed. This isn't a git repository, so there is no commit or push. Please run the tests before and after applying the change.