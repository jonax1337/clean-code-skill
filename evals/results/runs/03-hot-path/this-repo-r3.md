```java
private static final int PAYLOAD_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int PAYLOAD_BITS = 7;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    int shift = 0;
    while (true) {
        byte current = buf.get();
        value |= (current & PAYLOAD_MASK) << shift;
        if ((current & CONTINUATION_BIT) == 0) {
            return value;
        }
        shift += PAYLOAD_BITS;
        if (shift >= Integer.SIZE) {
            throw new RuntimeException("VarInt too big: more than 5 bytes");
        }
    }
}
```

**What changed**
- The magic numbers `0x7F`, `0x80` and `7` are now named constants, and `32` is `Integer.SIZE`. `javac` inlines `static final` primitives, so the bytecode for the arithmetic is the same.
- `pos` is now `shift`, which says what it is.
- The `while (true)` with `break` plus a separate `return` became a direct `return` at the termination point.
- `b` is declared where it is used.
- The exception message now says what the limit is.

**Performance**
I kept the loop shape, the single `buf.get()` per byte and the same operations in the same order, so nothing is added to the hot path. I did not benchmark or run it. If the 12 % matters, the real gains are probably elsewhere, for example a fast path that reads the common 1-byte case from a `byte[]` or avoids per-field `ByteBuffer` bounds checks. That needs a profile and is outside this cleanup.

**Left alone on purpose**
- It still throws plain `RuntimeException`, so any caller catching that keeps working. A dedicated exception type would be better, but it changes what callers can observe, so I'd do it separately.
- The fifth byte's high bits silently overflow into the sign bit (e.g. `FF FF FF FF 0F` gives `-1`). That matches the original and the usual VarInt wire format, so I did not touch it.

**Tests**
I haven't seen your test suite, so I haven't run anything. Since this has no visible tests, here is a characterization test to run against the original first, then against the cleaned version. It assumes JUnit 5, and `VarInts` is a placeholder for your class name:

```java
@ParameterizedTest
@CsvSource({
    "00, 0",
    "7F, 127",
    "8001, 128",
    "AC02, 300",
    "FFFFFF FF07, 2147483647",
    "FFFFFFFF0F, -1"
})
void readsVarInt(String hex, int expected) {
    ByteBuffer buf = ByteBuffer.wrap(HexFormat.of().parseHex(hex.replace(" ", "")));
    assertEquals(expected, VarInts.readVarInt(buf));
}

@Test
void rejectsVarIntLongerThanFiveBytes() {
    ByteBuffer buf = ByteBuffer.wrap(HexFormat.of().parseHex("808080808001"));
    assertThrows(RuntimeException.class, () -> VarInts.readVarInt(buf));
}
```

The `FFFFFF FF07` row has a space that the test strips; it's `FFFFFFFF07`.