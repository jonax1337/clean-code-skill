```kotlin
class UserService(private val repo: UserRepository) {
    fun displayName(id: Long): String? = repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: "$firstName $lastName"
}
```

**What changed**
- The `if (user == null) return null` guard became a safe call (`?.`). The nullable return for "not found" stays, since it is idiomatic in Kotlin and keeps the public signature unchanged.
- The nickname rule now lives in a private `User.displayName()` extension. `displayName(id)` reads as "look up the user, then ask for their display name", and the lookup is separate from the naming rule.
- `nickname?.takeIf { it.isNotBlank() } ?: ...` replaces the null check plus blank check plus early return.
- String concatenation became a string template.

**Behavior preserved**
- A blank or null nickname falls back to `"$firstName $lastName"`.
- A non-blank nickname is returned untrimmed, as before.
- An unknown id returns `null`.

**Not verified**
I couldn't compile or run anything here, and I can't see `User`, `UserRepository` or any existing tests. I haven't checked that this compiles against your types.

**Suggestions, not applied**
- If `User` is in your codebase, `displayName()` may belong there as a member, since it only uses the user's own fields. I kept it private here to avoid changing a class I can't see.
- If there are no tests yet, `displayName` needs four cases: unknown id, a nickname set, a null nickname, and a blank nickname (such as `"  "`). A fake `UserRepository` is enough for these.