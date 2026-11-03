```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int MAX_VARINT_BITS = 32;

public static int readVarInt(ByteBuffer buffer) {
    int value = 0;
    int shift = 0;
    do {
        byte current = buffer.get();
        value |= (current & PAYLOAD_MASK) << shift;
        if (!hasContinuationBit(current)) {
            return value;
        }
        shift += PAYLOAD_BITS_PER_BYTE;
    } while (shift < MAX_VARINT_BITS);

    throw new RuntimeException("VarInt too big");
}

private static boolean hasContinuationBit(byte current) {
    return (current & CONTINUATION_BIT) != 0;
}
```

**What changed**
- **Names:** `buf`, `b`, and `pos` became `buffer`, `current`, and `shift`. `pos` was misleading because it's a bit shift, not a buffer position. The magic numbers `0x7F`, `0x80`, `7`, and `32` are now named constants.
- **Control flow:** the `while (true)` with `break` is now a `do/while` with a clear exit. The happy path returns early, and the error case sits at the bottom.
- **Condition:** `hasContinuationBit` replaces the inline bit test, so the code reads as intent.
- **Scope:** `current` is declared inside the loop, next to where it's used.

**Behavior is preserved**
- It reads at most 5 bytes.
- It throws `RuntimeException("VarInt too big")` only when the 5th byte still has its continuation bit set. The shift sequence is 0, 7, 14, 21, 28, and 35 fails the `< 32` check, exactly as before.
- Overflow bits from the 5th byte are still silently dropped by the `int` shift.
- A `BufferUnderflowException` from `buffer.get()` still propagates unchanged.

**Performance**
- I haven't run a profiler or benchmark here, so I can't prove it's no slower. The structure is equivalent, though. The constants are `static final` primitives, so they're compile-time inlined. `hasContinuationBit` is a tiny private static method that HotSpot inlines trivially. There are no allocations or extra branches.
- I deliberately did not split the loop into more helper methods, since this is the hot path.
- Please check it with a JMH benchmark against the old version before merging.

**Optional follow-ups** (they change behavior or add scope, so I left them out)
- Throw a more specific exception, such as a custom `VarIntTooBigException extends RuntimeException`, so callers can catch it precisely.
- If most VarInts in your traffic fit in one byte, a fast path at the top can cut the CPU cost. It would read the first byte and return immediately if the continuation bit is clear. Benchmark that on real packet data.