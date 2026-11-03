```kotlin
class UserService(private val userRepository: UserRepository) {

    fun displayName(id: Long): String? =
        userRepository.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname.takeUnless { it.isNullOrBlank() } ?: fullName()

    private fun User.fullName(): String = "$firstName $lastName"
}
```

**What changed**

- **Null handling:** The early `if (user == null) return null` is now a safe call (`?.`), so the lookup and the "not found" case read as one step.
- **Nickname check:** `nickname != null && nickname.isNotBlank()` became `isNullOrBlank()`, which says the same thing in one call. Using `takeUnless` with `?:` makes the rule read as "nickname, unless blank, otherwise full name".
- **Abstraction levels:** `displayName(id)` only does lookup and delegation. The naming rule lives in `User.displayName()`, and string assembly lives in `fullName()`.
- **Names:** `repo` became `userRepository`, so the name no longer relies on a abbreviation.
- **String building:** `firstName + " " + lastName` became a string template.

**Behavior is preserved**

- An unknown id still returns `null`.
- A non-blank nickname is returned as-is, untrimmed.
- Otherwise the result is `"first last"`.

**Things to consider**

- Returning `String?` forces every caller to handle null. If "user not found" is truly exceptional in your codebase, a thrown `UserNotFoundException` would be cleaner. I left it alone because that changes the public contract, so it's a decision for you and your callers.
- If `displayName()` is useful elsewhere, it could move onto `User` itself, which would make `UserService` a thin lookup wrapper.
- I haven't run anything. Three small tests would pin the behavior down: unknown id, blank or null nickname, and a valid nickname.