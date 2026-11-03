Here is the cleaned-up version. It keeps the same loop and the same work per byte, so the hot path costs the same.

```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int MAX_VARINT_BITS = 32;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    int shift = 0;
    while (true) {
        byte current = buf.get();
        value |= (current & PAYLOAD_MASK) << shift;
        if ((current & CONTINUATION_BIT) == 0) {
            return value;
        }
        shift += PAYLOAD_BITS_PER_BYTE;
        if (shift >= MAX_VARINT_BITS) {
            throw new IllegalArgumentException(
                "VarInt longer than 5 bytes at buffer position " + buf.position());
        }
    }
}
```

**What changed**
- The magic numbers `0x7F`, `0x80`, `7` and `32` now have names, and `pos` is now `shift`, since it is a bit offset rather than a position.
- The method returns as soon as the last byte is read, so the `break` and the outer `byte b` declaration are gone.
- The error is now an `IllegalArgumentException` whose message says what is wrong and where in the buffer. It is still a `RuntimeException`, so any `catch (RuntimeException)` keeps working. Only code that matches the exact class or the old message text would notice.

**Why this doesn't slow it down**
- The constants are `static final` primitives, so `javac` inlines them and the bytecode is the same as with literals.
- The loop has the same per-byte operations: one `get()`, one mask and shift, and two branches.
- The message string is built only on the error path, which runs only for malformed input.
- I deliberately did not split the loop into helpers or add abstractions, since this is the measured hot spot.

**Behavior preserved**
- Overflow is detected at the same point as before, after a fifth byte that still has its continuation bit set.
- The high bits of the fifth byte are still silently truncated, as in the original.

**Not done**
- I couldn't compile, test or profile here, so none of this has been run. If you have tests for this method, please run them. If you don't, I'd add a few characterization tests: single-byte values, `0`, `127`/`128`, `Integer.MAX_VALUE`, `-1` (five bytes), and a six-byte input that should throw.
- Whether the 12% can be reduced is a separate question. Options would be a fast path for the one-byte case, or reading from the backing array instead of `buf.get()`. That would change the structure, so it should be decided from a benchmark.