```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int MAX_VARINT_BYTES = 5;
private static final int MAX_SHIFT = MAX_VARINT_BYTES * PAYLOAD_BITS_PER_BYTE;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < MAX_SHIFT; shift += PAYLOAD_BITS_PER_BYTE) {
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
- Magic numbers (`0x7F`, `0x80`, `7`, `32`) are now named constants. They're `static final` primitives, so the JIT folds them at compile time.
- The `while (true)` with a `break` and a mid-loop `pos >= 32` check is now a bounded `for` loop. The limit of 5 bytes is visible in the loop header, and the happy path returns directly.
- `b` is declared inside the loop, and `pos` is renamed to `shift`, which describes what it is.
- The overflow throw is moved after the loop, where it's reached only when the 5th byte still has the continuation bit set.

**Behavior and performance**
- Behavior is identical: the same bytes are consumed, the same value is returned, and the same exception is thrown after the 5th byte with the continuation bit still set. In the original, `pos` reaches 35 at that point, which trips `>= 32`.
- It's no slower. The work per byte is the same: one `get()`, one mask, one shift, one OR and one branch. There are no allocations, no extra method calls and no multiplication (I kept the incrementing `shift` rather than computing `index * 7`). The loop bound is a compile-time constant, so the JIT can unroll it just as well as the original.

I can't run the profiler here, so check the 12 % figure with a quick JMH comparison. If the cost comes from `ByteBuffer.get()` bounds checks, the bigger win would be at the call site, such as a fast path that reads from a `byte[]` or checks `buf.remaining()` once. That would be a separate change from this cleanup.

I kept `RuntimeException` so existing `catch` blocks behave the same. A dedicated exception type (e.g. `MalformedPacketException`) would be cleaner if you can update the callers.