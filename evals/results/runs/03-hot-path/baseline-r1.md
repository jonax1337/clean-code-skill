```java
private static final int SEGMENT_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int BITS_PER_SEGMENT = 7;

public static int readVarInt(ByteBuffer buf) {
    for (int shift = 0; shift < Integer.SIZE; shift += BITS_PER_SEGMENT) {
        byte current = buf.get();
        value |= (current & SEGMENT_MASK) << shift;

        if ((current & CONTINUATION_BIT) == 0) {
            return value;
        }
    }
    throw new IllegalArgumentException("VarInt too big");
}
```

Oops, that snippet is missing the `value` declaration. Here is the correct version:

```java
private static final int SEGMENT_MASK = 0x7F;
private static final int CONTINUATION_BIT = 0x80;
private static final int BITS_PER_SEGMENT = 7;

public static int readVarInt(ByteBuffer buf) {
    int value = 0;
    for (int shift = 0; shift < Integer.SIZE; shift += BITS_PER_SEGMENT) {
        byte current = buf.get();
        value |= (current & SEGMENT_MASK) << shift;

        if ((current & CONTINUATION_BIT) == 0) {
            return value;
        }
    }
    throw new IllegalArgumentException("VarInt too big");
}
```

**What changed**
- Magic numbers (`0x7F`, `0x80`, `7`, `32`) are now named constants. They're `static final` primitives, so the JIT inlines them and the generated code is the same.
- The `while (true)` with a manual `pos` counter and a mid-loop `break` became a bounded `for` loop. The 5-segment limit is now visible in the loop header instead of a check buried in the body.
- The happy path returns directly from inside the loop. `b` is declared where it's used.
- The throw moved after the loop, so it reads as the "ran out of segments" case.

**Behavior and performance**
- Behavior is identical: shifts 0, 7, 14, 21 and 28 are read (5 bytes max). A continuation bit on the 5th byte throws, just as `pos` reaching 35 did before.
- There are no allocations, no extra calls and no extra branches. The loop does the same work per byte as before.
- I changed the exception from `RuntimeException` to `IllegalArgumentException`, which is more specific. It's a subclass, so existing `catch (RuntimeException)` handlers still work. If you'd rather not change the type at all, swap it back.

If the 12% is still a concern, the real cost is likely the per-byte `buf.get()` bounds checks. Most VarInts in packets fit in one byte, so a fast path (read one byte, return if the high bit is clear) could help. I haven't added it, since you asked for a cleanup, and it should be benchmarked first.