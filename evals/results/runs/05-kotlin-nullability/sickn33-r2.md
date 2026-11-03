```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.let(::displayNameOf)

    private fun displayNameOf(user: User): String =
        user.nickname.takeUnless { it.isNullOrBlank() } ?: fullNameOf(user)

    private fun fullNameOf(user: User): String =
        "${user.firstName} ${user.lastName}"
}
```

**What changed and why**

- **Removed the null-check ladder.** `findById(id)?.let(...)` replaces the early `return null`, so the public function reads as one step: find the user, then derive the display name.
- **One level of abstraction per function.** `displayName` handles lookup, `displayNameOf` picks the nickname or full name, and `fullNameOf` builds the string. This follows the stepdown rule, with each function calling the one below it.
- **`isNullOrBlank()` replaces `!= null && isNotBlank()`.** It's more concise, and it doesn't rely on smart-casting `user.nickname`, which only works if the property is a stable `val` in the same module.
- **String template instead of `+`.** It's easier to read, and it gives the same result.

**Behavior is preserved.** It still returns `null` for an unknown id, returns the nickname untrimmed when it's non-blank, and otherwise returns `"first last"`.

I kept the `String?` return type on purpose. Clean Code generally prefers not returning null, but switching to an exception or a result type would change the contract for every caller, and I can't see them from here. If you want that, it's a separate change.

I can't run anything in this session, so I haven't verified this. Before merging, I'd cover these cases with tests:
- Unknown id returns `null`.
- A non-blank nickname is returned as-is.
- A `null` nickname falls back to the full name.
- A blank nickname (`"  "`) falls back to the full name.