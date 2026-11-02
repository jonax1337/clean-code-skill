```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname.takeUnless { it.isNullOrBlank() } ?: fullName()

    private fun User.fullName(): String = "$firstName $lastName"
}
```

**What changed and why**

- **Null handling:** The guard clause `if (user == null) return null` becomes a safe call (`?.`). The "missing user" case is now handled by the language instead of a manual check.
- **Nickname check:** `nickname != null && nickname.isNotBlank()` becomes `isNullOrBlank()`. This also avoids relying on a smart cast, which fails if `nickname` is a `var` or comes from another module.
- **One level of abstraction:** `displayName(id)` now only says "find the user and ask for their display name". The rule for choosing between nickname and full name lives in a private `User.displayName()` extension, and the name concatenation lives in `fullName()`.
- **String building:** `firstName + " " + lastName` becomes a string template.
- **Behavior preserved:** I kept the nullable return type. It is the existing contract, and switching to an exception or a result type would change what callers see. The nickname is still returned untrimmed, as before.

If you can edit `User`, these two extensions would fit better as member functions there. The `User` class wasn't shown, so I kept them private to this service.

I haven't run anything. Before merging, I'd cover four cases with tests:

- unknown id returns `null`
- a nickname is returned when present
- a `null` or blank nickname falls back to the full name
- the full name is formatted as `"First Last"`