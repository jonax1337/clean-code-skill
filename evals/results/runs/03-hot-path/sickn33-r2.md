```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int MAX_SHIFT = 32;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < MAX_SHIFT; shift += PAYLOAD_BITS_PER_BYTE) {
        byte current = buf.get();
        value |= (current & PAYLOAD_MASK) << shift;
        if (isLastByte(current)) {
            return value;
        }
    }
    throw new RuntimeException("VarInt too big");
}

private static boolean isLastByte(byte b) {
    return (b & CONTINUATION_BIT) == 0;
}
```

**What changed**
- **Magic numbers** (`0x7F`, `0x80`, `7`, `32`) now have intention-revealing names.
- **Loop structure:** `while (true)` with a `break` and a mid-loop bounds check became a bounded `for` loop. The exit conditions are now visible in the loop header and the early `return`, and the error path is the single line after the loop.
- **Naming:** `b`, `pos` and the mutable `byte` declared outside the loop became `current` and `shift`. `pos` was really a bit shift, not a position. `current` is declared where it's used.
- **Helper:** `isLastByte` names the continuation-bit test at the same level of abstraction as the rest of the method.

**Behavior is preserved**
- A VarInt still consumes at most 5 bytes. The original threw when `pos` reached 35 after a fifth byte that still had its continuation bit set. The new loop exits at the same point and throws.
- Bits of the fifth byte that overflow 32 are still silently dropped, as before.
- `buf.get()` still throws `BufferUnderflowException` on truncated input.
- The exception type and message are unchanged.

**Performance**
- The work per byte is the same: one `get`, a mask, a shift, an OR and a test. No allocations, boxing or extra branches were added.
- The constants are `static final` primitives, so they are compile-time constants.
- `isLastByte` is a tiny static method, which the JIT inlines.

I can't run a profiler here, so I haven't measured this. Since the method is this hot, run a quick JMH comparison against the old version before merging.

If you're free to change behavior later, a dedicated exception type such as `VarIntTooBigException` would be better than a bare `RuntimeException`. Callers could then tell malformed packets from other failures. I left it alone to keep this a pure refactor.