```java
private static final int DATA_BITS_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int BITS_PER_BYTE = 7;
private static final int INT_BITS = 32;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < INT_BITS; shift += BITS_PER_BYTE) {
        byte current = buf.get();
        value |= (current & DATA_BITS_MASK) << shift;
        if (isLastByte(current)) {
            return value;
        }
    }
    throw new RuntimeException("VarInt too big");
}

private static boolean isLastByte(byte current) {
    return (current & CONTINUATION_BIT) == 0;
}
```

**What changed**
- **Magic numbers became named constants**: `0x7F`, `0x80`, `7` and `32` now say what they mean.
- **Control flow is simpler**: the `while (true)` with `break` and a mid-loop `pos` update became a bounded `for` loop. The limit now sits in the loop header, and the happy path is an early `return`.
- **`pos` is now `shift`**, which is what it is used for.
- **The continuation check has a name**: `isLastByte` replaces the bit test. It is a tiny static method that the JIT will inline.

**Behavior and performance**
- **Same behavior**: shifts are still 0, 7, 14, 21, 28, so at most 5 bytes are read. If the 5th byte still has the continuation bit set, it throws the same `RuntimeException("VarInt too big")`. Overflow bits in the 5th byte are dropped as before.
- **Same cost**: the `static final int` constants are compile-time inlined, there are no allocations, and the loop does one `get()`, one mask and one compare per byte, same as before. The helper is trivially inlinable, but I haven't run a benchmark, so please confirm with your profiler or a JMH run.

**Suggestions**
- **Throw a specific exception**: a dedicated unchecked exception like `VarIntTooBigException extends RuntimeException` would be clearer. I kept `RuntimeException` so callers that catch it see no change.
- **Tests to add before merging**: values 0, 127, 128, `Integer.MAX_VALUE` and -1 (5 bytes), a 6-byte input that must throw, and a truncated buffer that must throw `BufferUnderflowException`.