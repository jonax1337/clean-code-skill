Here is the cleaned-up version. I kept the loop structure and primitive arithmetic, so it does the same work per byte as before: no allocation, no extra calls, and the constants are inlined at compile time.

```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS_PER_BYTE = 7;
private static final int INT_BITS = 32;

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
        if (shift >= INT_BITS) {
            throw new RuntimeException("VarInt is longer than 5 bytes");
        }
    }
}
```

**What changed**
- The magic numbers `0x7F`, `0x80`, `7` and `32` now have names.
- `pos` is now `shift`, since it is a bit offset, not a position in the buffer.
- `b` is now `current` and is declared where it is used.
- The `break` plus trailing `return` became an early `return`, and the exit condition is checked first.
- The exception message now says what is wrong. I kept `RuntimeException` as the type because I can't see your callers, and changing it could affect a `catch`. If callers don't depend on it, a dedicated exception type would be a good follow-up.

**Behavior is unchanged, quirks included**
- A 5th byte with extra high bits is silently truncated, as before.
- A buffer that ends mid-VarInt still throws `BufferUnderflowException` from `buf.get()`.
- The "too big" error still fires only when the 5th byte has its continuation bit set.

**Performance:** I haven't benchmarked it, since I can't run anything here. The bytecode should be essentially equivalent: the same loop, the same operations, and constants folded at compile time. If the 12 % matters, the real gains are probably at the call site (for example, a fast path for single-byte values when `buf.hasArray()`). That would be a separate change that needs a profiler to justify.

**Tests:** I didn't see any tests for this method. Here is a characterization test that pins the current behavior, so you can check the refactoring against the original. I haven't compiled or run it.

```java
class VarIntTest {
    private static ByteBuffer bytes(int... values) {
        ByteBuffer buf = ByteBuffer.allocate(values.length);
        for (int v : values) buf.put((byte) v);
        buf.flip();
        return buf;
    }

    @Test void readsSingleByteValues() {
        assertEquals(0, readVarInt(bytes(0x00)));
        assertEquals(127, readVarInt(bytes(0x7F)));
    }

    @Test void readsMultiByteValues() {
        assertEquals(128, readVarInt(bytes(0x80, 0x01)));
        assertEquals(300, readVarInt(bytes(0xAC, 0x02)));
        assertEquals(Integer.MAX_VALUE, readVarInt(bytes(0xFF, 0xFF, 0xFF, 0xFF, 0x07)));
    }

    @Test void readsNegativeValueFromFiveBytes() {
        assertEquals(-1, readVarInt(bytes(0xFF, 0xFF, 0xFF, 0xFF, 0x0F)));
    }

    @Test void rejectsVarIntLongerThanFiveBytes() {
        assertThrows(RuntimeException.class,
                () -> readVarInt(bytes(0x80, 0x80, 0x80, 0x80, 0x80, 0x01)));
    }

    @Test void failsOnTruncatedInput() {
        assertThrows(BufferUnderflowException.class, () -> readVarInt(bytes(0x80)));
    }
}
```

Run these against the original first and then against the new version. Both should pass.