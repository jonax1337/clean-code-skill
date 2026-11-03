Here is the cleaned-up version. It behaves the same as your original and adds no work per call.

```java
private static final int VARINT_MAX_BYTES = 5;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int byteIndex = 0; byteIndex < VARINT_MAX_BYTES; byteIndex++) {
        byte current = buf.get();
        value |= (current & PAYLOAD_MASK) << (byteIndex * PAYLOAD_BITS_PER_BYTE);
        if ((current & CONTINUATION_BIT) == 0) {
            return value;
        }
    }
    throw new RuntimeException("VarInt too big");
}
```

**What changed**
- **Named constants** replace the magic numbers `0x7F`, `0x80`, `7` and `32`.
- **Bounded `for` loop** replaces `while (true)` with a `break`. The 5-byte limit is now visible in the loop header instead of being hidden in a `pos >= 32` check after the increment.
- **Early `return`** replaces the `break`, so there is no need to carry the loop state to a return at the end.
- **Narrower scope:** `b` is declared inside the loop as `current`, and the manual `pos += 7` bookkeeping is gone.

**Behavior and performance**
- **Same limit:** The original allowed 5 bytes and threw if the 5th still had the continuation bit set. The new loop does the same, with the same exception and message.
- **Same cost:** The constants are `static final` primitives, so javac inlines them. The loop is a fixed 5 iterations with one `buf.get()` per byte, which is the same work as before. The `byteIndex * 7` multiply is trivial, and the JIT turns it into a shift/add or unrolls the loop.
- **Not benchmarked:** I can't run a profiler here, so check it on your workload (e.g., with JMH) to confirm.

**Optional improvements** (these change the code beyond a cleanup, so I left them out)
- If most VarInts in your traffic are one byte, a fast path (`byte first = buf.get(); if (first >= 0) return first;`) would likely help the 12 % more than any restructuring.
- Throwing a dedicated exception, such as `VarIntTooBigException extends RuntimeException`, would be cleaner than a bare `RuntimeException` and stay compatible with existing `catch` blocks.