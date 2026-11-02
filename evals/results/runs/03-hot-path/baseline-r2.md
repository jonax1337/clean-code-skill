```java
private static final int SEGMENT_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int SHIFT_PER_BYTE = 7;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < Integer.SIZE; shift += SHIFT_PER_BYTE) {
        byte current = buf.get();
        value |= (current & SEGMENT_MASK) << shift;
        if ((current & CONTINUATION_BIT) == 0) {
            return value;
        }
    }
    throw new IllegalArgumentException("VarInt too big");
}
```

**What changed**

- **Named constants** replace the magic numbers `0x7F`, `0x80` and `7`. They're `static final` primitives, so the compiler inlines them and there's no runtime cost.
- **A `for` loop replaces `while (true)` with `break`.** The loop bound (`shift < 32`) now states the 5-byte limit directly, and the valid case returns as soon as the last byte is seen.
- **Variable scope is tighter.** `b` is declared inside the loop as `current`, and the separate `pos` increment and check are folded into the loop header.
- **The exception is now `IllegalArgumentException`.** It's still a `RuntimeException`, so existing `catch (RuntimeException e)` handlers keep working. If anything catches the exact type, keep `RuntimeException`.

**Behavior and performance**

- Semantics are the same. It reads at most 5 bytes, throws if the 5th still has the continuation bit set, and leaves the buffer position in the same place.
- The hot path is the same work as before: one `get()`, a mask, a shift, an OR, and a test per byte. There are no allocations or extra calls, and the method is small enough for the JIT to inline.
- I haven't benchmarked this. It should be equivalent, but if the 12% matters, confirm with JMH or your profiler.
- If the profile stays high, the bigger win is usually upstream, such as avoiding per-field `ByteBuffer.get()` bounds checks by reading from a backing `byte[]` with a manual index, or batching the field parsing. That's a larger change than a cleanup.