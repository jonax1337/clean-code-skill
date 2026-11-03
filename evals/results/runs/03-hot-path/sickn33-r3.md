```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int MAX_VARINT_BITS = 32;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    int shift = 0;
    byte current;
    do {
        if (shift >= MAX_VARINT_BITS) {
            throw new RuntimeException("VarInt too big");
        }
        current = buf.get();
        value |= (current & PAYLOAD_MASK) << shift;
        shift += PAYLOAD_BITS_PER_BYTE;
    } while (hasContinuationBit(current));
    return value;
}

private static boolean hasContinuationBit(byte b) {
    return (b & CONTINUATION_BIT) != 0;
}
```

**What changed**
- **Names:** `pos` is now `shift`, since it's a bit shift and not a buffer position. `b` is now `current`. The magic numbers `0x7F`, `0x80`, `7` and `32` are named constants.
- **Loop:** `while (true)` with a `break` is now a `do/while` whose condition says what it means: keep reading while the continuation bit is set. `hasContinuationBit` names the bit test.
- **Overflow guard:** the check moved to the top of the loop, so the happy path reads straight through.

**Behavior is preserved**
- The result is the same for every input.
- It still throws `RuntimeException("VarInt too big")` when a fifth byte still has its continuation bit set.
- It consumes exactly 5 bytes before throwing, as the original did, because the guard fires before a sixth `get()`.
- I kept `RuntimeException` so existing `catch` blocks keep working. A dedicated subclass (e.g. `VarIntTooBigException extends RuntimeException`) would be a cheap, compatible improvement if you want it.

**Performance**
- The constants are `static final` primitives, so `javac` inlines them as literals.
- `hasContinuationBit` is a tiny static method that the JIT will inline, and the loop does the same work per byte as before (one `get()`, one mask, one shift, one test).
- I can't run a benchmark here, so I haven't measured it. Please confirm with a JMH run or your profiler before merging.
- If 12 % is still too high, the usual next step is to avoid per-field calls. For example, add a fast path for single-byte values, or read from a backing `byte[]` with an index instead of `ByteBuffer.get()`. I haven't added either, since both are unmeasured changes.

**Tests:** I'd cover these cases:
- 0, 1, 127, 128, 255, 25565, `Integer.MAX_VALUE`, and -1 (the 5-byte encoding).
- A 5-byte input whose last byte has the continuation bit set, which must throw.
- A truncated buffer, which still throws `BufferUnderflowException`.