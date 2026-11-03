```java
private static final int VARINT_PAYLOAD_MASK = 0x7F;
private static final int VARINT_CONTINUATION_BIT = 0x80;
private static final int VARINT_BITS_PER_BYTE = 7;
private static final int VARINT_MAX_SHIFT = 32;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < VARINT_MAX_SHIFT; shift += VARINT_BITS_PER_BYTE) {
        byte current = buf.get();
        value |= (current & VARINT_PAYLOAD_MASK) << shift;
        if ((current & VARINT_CONTINUATION_BIT) == 0) {
            return value;
        }
    }
    throw new RuntimeException("VarInt too big");
}
```

**What changed**
- **Magic numbers:** `0x7F`, `0x80`, `7` and `32` are now named constants. They are `static final` primitives, so the compiler inlines them and there is no runtime cost.
- **Loop structure:** the `while (true)` with a `break` and a manual `pos` update became a bounded `for` loop. The shift is the loop variable, and the happy path returns directly. This removes the mutable `b` declared outside the loop and the `break`.
- **Naming:** `b` is now `current`, and `pos` is now `shift`, which is what it actually is.

**Behavior and performance**
- The logic is identical. It reads at most 5 bytes (shifts 0, 7, 14, 21, 28) and throws if the fifth byte still has the continuation bit set. The original reached the same limit via `pos >= 32`.
- The hot path is the same work as before: one `get()`, one mask, one shift, one OR, and one branch per byte. The bounded loop is trivially JIT-friendly, so I don't expect any slowdown. I haven't benchmarked it here, so it's worth a quick check in your profiler.
- I left the exception as `RuntimeException` so no existing `catch` blocks change behavior. If you can change callers, a dedicated exception type, such as a `VarIntTooBigException`, would be cleaner.