```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int MAX_VARINT_BYTES = 5;
private static final int MAX_VARINT_SHIFT = MAX_VARINT_BYTES * PAYLOAD_BITS_PER_BYTE;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < MAX_VARINT_SHIFT; shift += PAYLOAD_BITS_PER_BYTE) {
        byte current = buf.get();
        value |= (current & PAYLOAD_MASK) << shift;
        if ((current & CONTINUATION_BIT) == 0) {
            return value;
        }
    }
    throw new RuntimeException("VarInt too big");
}
```

**What changed**
- **Named constants** replace the magic numbers `0x7F`, `0x80`, `7` and `32`. All are `static final` primitives, so the compiler folds them in and nothing changes at runtime.
- **A bounded `for` loop** replaces `while (true)` with `break`. The loop bound now states the rule (at most 5 bytes), and the success path is a plain early `return`.
- **The `pos >= 32` check is gone.** The loop bound does the same job: shifts run 0, 7, 14, 21, 28, and a fifth byte that still has the continuation bit falls through to the exception.
- **Variable names** are now `shift` instead of `pos` (it's a bit offset, not a position) and `current` instead of `b`. `b` is declared inside the loop so its scope is as small as possible.

**Performance and behavior**
- The work per byte is the same: one `get()`, one mask-and-shift, one branch. The only change is that the overflow check is now the loop condition instead of a separate branch, so it is no faster or slower in practice. The method stays small enough for the JIT to inline.
- Behavior is identical, including the exception for over-long VarInts and `BufferUnderflowException` from `buf.get()` on truncated input.

If you want to go further, throw a specific exception such as `IllegalArgumentException` or a custom `MalformedPacketException` instead of `RuntimeException`. That would let callers handle bad packets explicitly. It's off the hot path, so it costs nothing, but it changes what callers can catch, so I left it alone.

I can't profile here. If the 12% is a concern, the real gains probably come from reading fields in bulk, or from a fast path for single-byte VarInts when `buf.hasArray()`. I'd benchmark with JMH before trying either.