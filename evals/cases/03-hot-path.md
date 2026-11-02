# Clean up hot-path code (Java)

Tests: "when not to apply" — readability improvements without performance regressions.

## Prompt

Clean this up according to clean code. It's called for every field of every incoming packet in our proxy and shows up at ~12 % CPU in the profiler, so don't make it slower.

```java
public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    int pos = 0;
    byte b;
    while (true) {
        b = buf.get();
        value |= (b & 0x7F) << pos;
        if ((b & 0x80) == 0) break;
        pos += 7;
        if (pos >= 32) throw new RuntimeException("VarInt too big");
    }
    return value;
}
```

## Assertions

1. No allocation is added on the normal (non-error) path: no `Optional`, boxing, streams, lambdas, iterators or new objects per call.
2. The bit masks and shift constants (`0x7F`, `0x80`, `7`, `32`) are given names.
3. The method stays a single tight loop: no interfaces, polymorphism, strategy objects or splitting into several small helper methods on the hot path.
4. The error case is improved: a more specific exception type or a message with useful context.
5. The response explicitly acknowledges the performance constraint and explains which clean-code changes it did or did not make because of it.
