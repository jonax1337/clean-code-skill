```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int INT_BITS = 32;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < INT_BITS; shift += PAYLOAD_BITS_PER_BYTE) {
        byte current = buf.get();
        value |= (current & PAYLOAD_MASK) << shift;
        if (!hasContinuationBit(current)) {
            return value;
        }
    }
    throw new RuntimeException("VarInt too big");
}

private static boolean hasContinuationBit(byte b) {
    return (b & CONTINUATION_BIT) != 0;
}
```

**What changed**
- **Magic numbers became named constants**: `0x7F`, `0x80`, `7` and `32` now say what they mean. They are `static final` primitives, so javac inlines them and there is no runtime cost.
- **`while (true)` with `break` became a bounded `for` loop**: the limit of five bytes is visible in the loop header instead of being a mid-loop check. `pos` is now `shift`, which describes how it is used.
- **Early `return`**: this replaces the `break` and the trailing `return`, and `value` and `b` are no longer declared outside the loop.
- **`hasContinuationBit` helper**: it is tiny and static, so HotSpot will inline it. If you'd rather not depend on that in a hot path, inline the expression `(current & CONTINUATION_BIT) == 0`; it is still readable.

**Behavior is preserved**
- Shifts are 0, 7, 14, 21, 28, so at most 5 bytes are read. If the 5th byte still has the continuation bit set, it throws the same `RuntimeException("VarInt too big")`, exactly as the original did.
- `buf.get()` still throws `BufferUnderflowException` on truncated input.
- The high bits of the 5th byte still overflow silently, as before. I kept this to avoid changing behavior, but if you want strict validation, that would be a separate change.

**Performance**
I couldn't run anything here, so I haven't measured it. The loop does the same work per byte: one `get()`, one mask, one shift, one branch. I'd expect identical JIT output, but please confirm with your existing profiler run or a quick JMH benchmark against the old version.

**Suggested next steps**
- Add tests for 1-byte, 2-byte and 5-byte values, `-1` (which encodes to 5 bytes), a 6-byte input that should throw, and a truncated buffer.
- Consider a dedicated `VarIntTooBigException extends RuntimeException`. That would be clearer than a bare `RuntimeException`, and existing `catch (RuntimeException)` sites would still work. I left it out to keep this change behavior-neutral.