Here is the cleaned-up version. It is the same algorithm: one `buf.get()` per byte, no allocation, and the same inlined constants and bit operations.

```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_FLAG = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int VARINT_BIT_LIMIT = 32;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < VARINT_BIT_LIMIT; shift += PAYLOAD_BITS_PER_BYTE) {
        byte current = buf.get();
        value |= (current & PAYLOAD_MASK) << shift;
        if (isLastByte(current)) {
            return value;
        }
    }
    throw new RuntimeException("VarInt too big");
}

private static boolean isLastByte(byte b) {
    return (b & CONTINUATION_FLAG) == 0;
}
```

**What changed**
- **Names:** `pos` is really a bit shift, so it is now `shift`. The magic numbers `0x7F`, `0x80`, `7` and `32` are named constants.
- **Control flow:** `while (true)` with `break` and a mid-loop check became a bounded `for` loop that returns as soon as it sees the last byte. The limit is now visible in the loop header instead of in a check inside the body.
- **Abstraction level:** `isLastByte` replaces the raw bit test, so the loop reads as "read byte, accumulate, stop on the last byte".
- **Scope:** `b` is declared inside the loop, next to where it is used.

**Behavior is preserved**
- The shifts are 0, 7, 14, 21 and 28, so at most 5 bytes are read. If the 5th byte still has the continuation bit set, it throws, as before.
- Bits shifted past bit 31 on the 5th byte are silently dropped, as before.
- The exception type and message are unchanged. If your callers don't depend on the exact type, you could switch to a more specific `RuntimeException` subclass, but I left it alone to keep this a pure refactor.

**Performance**
- The constants are `static final` primitives, so javac inlines them. `isLastByte` is tiny and static, so HotSpot will inline it.
- I couldn't run a profiler or benchmark here. Before merging, I'd run a quick JMH comparison of old versus new, and add a few tests for the 1-byte, 5-byte and 6-byte (too big) cases.
- If the 12% is still a concern, the next step is likely at the call site rather than in this method, for example reading from the backing array directly or batching reads. That would be a separate change.