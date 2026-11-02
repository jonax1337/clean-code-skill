# Nullability in Kotlin

Tests: "don't return null" must not override idiomatic Kotlin; no over-extraction.

## Prompt

Apply clean code principles to this class.

```kotlin
class UserService(private val repo: UserRepository) {
    fun displayName(id: Long): String? {
        val user = repo.findById(id)   // returns User?
        if (user == null) return null
        if (user.nickname != null && user.nickname.isNotBlank()) return user.nickname
        return user.firstName + " " + user.lastName
    }
}
```

## Assertions

1. The nullable return type for "user not found" is kept (or the response explicitly justifies a change); it is not replaced by throwing an exception for the normal not-found case.
2. No Java `Optional` is introduced.
3. Uses Kotlin idioms such as `?.`, `?:`, `takeIf`/`ifBlank`/`isNullOrBlank` or string templates instead of Java-style null checks and concatenation.
4. Behavior is preserved: unknown id → `null`; non-blank nickname → nickname; null or blank nickname → "firstName lastName".
5. No over-extraction: the result is not split into more than two additional functions or classes.
