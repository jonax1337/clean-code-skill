```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: fullName()

    private fun User.fullName(): String =
        "$firstName $lastName"
}
```

**What changed**

- **Removed the early-return null check.** `?.` expresses "no user means no name" in one line, so the public method reads as a single step.
- **Extracted `User.displayName()`.** The nickname-or-full-name rule now has a name, so it is no longer mixed in with the repository lookup. The lookup and the naming rule are now at separate levels of abstraction.
- **Replaced the null-and-blank check with `takeIf` and `?:`.** The `nickname != null && nickname.isNotBlank()` condition becomes "use the nickname if it's not blank, otherwise the full name".
- **Added `fullName()` and a string template.** This replaces the `+` concatenation, and the name documents what the expression is.

**Behavior preserved**

- A missing user still returns `null`.
- A non-blank nickname is returned untrimmed, exactly as before.
- Otherwise the result is `"$firstName $lastName"`.

**Notes**

- The skill advises against returning null, but I kept `String?` because changing it would alter the public contract and every caller. If your codebase prefers it, you could throw a `UserNotFoundException` or return a result type instead. That should be a separate, deliberate change.
- If `User` is your own domain class, `displayName()` and `fullName()` might fit better there as members. That would remove the extension functions from the service and let other code reuse the rule.
- I couldn't run anything here. Tests worth having: unknown id returns `null`, a nickname is returned, a null nickname falls back to the full name, and a blank nickname (`"  "`) falls back to the full name.