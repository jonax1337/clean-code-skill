```kotlin
class UserService(private val repo: UserRepository) {
    fun displayName(id: Long): String? =
        repo.findById(id)?.nicknameOrFullName()

    private fun User.nicknameOrFullName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: "$firstName $lastName"
}
```

**What changed**
- The early `return null` and the null/blank check on `nickname` became safe calls (`?.`, `takeIf`, `?:`). That is the usual Kotlin way to write them.
- The "which name do we show" rule is now a named private extension, `nicknameOrFullName`. `displayName` just reads "find the user, then pick their name".
- String concatenation became a template: `"$firstName $lastName"`.
- The nullable return stays. In Kotlin, `String?` for "user not found" is idiomatic, and changing it would alter the public signature.

**Behavior preserved**
- A missing user still gives `null`.
- A non-blank nickname is returned unchanged, not trimmed.
- A null or blank nickname still falls back to `"first last"`.

**What I did not do**
- I did not run a compiler or tests. I can only see this one class, so none of this is verified.
- I did not add tests. I can't see `User` or `UserRepository`, so I'd have to guess their constructors and your test framework. Before merging, I'd pin these cases with a fake repository: user missing, nickname `null`, nickname `""`, nickname `"   "`, and a real nickname.
- If other code needs the same rule, the better home for `nicknameOrFullName` is `User` itself. I left it private here because I can't see that file and no other caller is in scope.