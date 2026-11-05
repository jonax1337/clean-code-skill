# Before and after

Short pairs that show how strongly to apply the rules. Each one names the heuristics involved.

## 1. Intent through names and conditionals (Python) — G16, G19, G25, G28

Before:

```python
def check(u):
    if u.age >= 18 and u.country in ("DE", "AT", "CH") and not u.banned and u.verified_at:
        return True
    return False
```

After:

```python
DACH_COUNTRIES = {"DE", "AT", "CH"}
ADULT_AGE = 18

def can_place_order(user: User) -> bool:
    is_adult = user.age >= ADULT_AGE
    ships_to_user = user.country in DACH_COUNTRIES
    in_good_standing = not user.banned and user.verified_at is not None
    return is_adult and ships_to_user and in_good_standing
```

The function got a name that says what is being decided. The `if/return True/return False` collapsed into the expression it was hiding. The rename is safe here because `check` was a module-private helper with two call sites, both updated in the same diff; for a public function, keep the old name as a deprecated alias or list the callers.

## 2. Flag argument (TypeScript) — F3, G15

Before:

```ts
function render(report: Report, asPdf: boolean): Buffer {
  const body = layout(report);
  if (asPdf) return pdf(body);
  return Buffer.from(html(body));
}

render(report, true); // true what?
```

After:

```ts
function renderPdf(report: Report): Buffer {
  return pdf(layout(report));
}

function renderHtml(report: Report): Buffer {
  return Buffer.from(html(layout(report)));
}
```

The call site now reads `renderPdf(report)`. Because the public signature changed, the reply has to list the call sites that were updated.

## 3. Errors in Go — swallowed error, missing context

Before:

```go
func LoadConfig(path string) Config {
    data, _ := os.ReadFile(path)
    var cfg Config
    json.Unmarshal(data, &cfg)
    return cfg
}
```

After:

```go
func LoadConfig(path string) (Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return Config{}, fmt.Errorf("read config %s: %w", path, err)
    }
    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return Config{}, fmt.Errorf("parse config %s: %w", path, err)
    }
    return cfg, nil
}
```

The book says "exceptions"; Go says `error` values. The intent is the same: no silent failure, and the error carries context. Adding a custom exception type or `panic` would fight the language.

## 4. Hot path (Java) — where the book bends

Code that runs for every entity on every server tick:

```java
for (int i = 0; i < count; i++) {
    switch (kinds[i]) {
        case 0 -> vy[i] -= 0.08;          // gravity
        case 1 -> vy[i] -= 0.04;          // floating items fall slower
        default -> { }
    }
    y[i] += vy[i];
}
```

Tempting but wrong here: a `Movable` interface with one subclass per kind, or `entities.stream().forEach(...)`. Both add virtual calls or allocations per element in the hottest loop.

Better:

```java
private static final double GRAVITY = 0.08;
private static final double ITEM_GRAVITY = 0.04;
private static final int KIND_LIVING = 0;
private static final int KIND_ITEM = 1;

// Runs per entity per tick: kept as a flat switch over primitive arrays on purpose.
for (int i = 0; i < count; i++) {
    switch (kinds[i]) {
        case KIND_LIVING -> vy[i] -= GRAVITY;
        case KIND_ITEM -> vy[i] -= ITEM_GRAVITY;
        default -> { }
    }
    y[i] += vy[i];
}
```

Names and constants improve; the structure stays because it is the fast one. The comment explains *why*, which is the kind of comment the book wants.

## 5. Scope discipline — the diff matters

Task: "Add an optional `discount` to `Order.total()`."

Bad diff: adds the parameter, also renames `calc_tax` to `compute_tax`, converts two loops to comprehensions, reorders imports and adds type hints to unrelated functions.

Good diff: adds `discount: Decimal = Decimal("0")`, applies it in `total()`, adds a test for a discounted order and one for a discount larger than the subtotal. The reply ends with: "Not changed: `calc_tax` and `compute_shipping` use different rounding; worth aligning separately."

## 6. Comments — C1, C3 and the narrating comment

Before:

```js
// Changed by agent: now uses the new cache
// Get the user
const user = cache.get(id) ?? (await db.users.find(id)); // fixed bug
```

After:

```js
// The cache is filled asynchronously after signup, so a miss right after registration is normal.
const user = cache.get(id) ?? (await db.users.find(id));
```

The first two comments restate the code or the edit history. The new one tells a future reader something the code cannot.

## 7. The direct form (TypeScript) — G19, G30

Before:

```ts
const seen = new Map<string, number>();
const keep = (sku: string, index: number) => seen.set(sku.trim().toUpperCase(), index);

for (const line of lines) {
  const at = seen.get(line.sku.trim().toUpperCase());
  if (at === undefined) keep(line.sku, cart.push({ ...line }) - 1);
  else cart[at].quantity += line.quantity;
}
```

After:

```ts
const indexBySku = new Map<string, number>();

for (const line of lines) {
  const sku = line.sku.trim().toUpperCase();
  const existing = indexBySku.get(sku);
  if (existing === undefined) {
    indexBySku.set(sku, cart.length);
    cart.push({ ...line });
  } else {
    cart[existing].quantity += line.quantity;
  }
}
```

Same behavior, same speed. The key is normalized once, the index is written where it is decided, and nothing depends on `push` returning the new length. A closure and an arithmetic trick saved two lines and cost every reader a pause.

## 8. When a name helps, and when it does not (Python, Kotlin) — G25, N1

A value gets a name when the reader cannot tell what it means at the use site:

```python
if attempts > 3:            # three what, and why three?
    lock_account(user)

MAX_FAILED_LOGINS = 3       # after this many, the account is locked
if attempts > MAX_FAILED_LOGINS:
    lock_account(user)
```

A unit factor next to its unit already says what it is. A shared constant for it widens the module's surface and sends the reader to another file:

```kotlin
// Before: a new export, imported by four files
const val MILLIS_PER_SECOND = 1000L
val timeoutMs = config.timeoutSeconds * MILLIS_PER_SECOND

// After: the unit is in both names
val timeoutMs = config.timeoutSeconds * 1000L
```

When a constant is needed in one file only, keep it private there. Promote it when the second file needs it.

## 9. Where new code goes (Python) — G5, G17

Task: add a function that formats a duration for the activity feed.

Not this:

```text
app/utils.py            (new)  format_duration()
app/feed/render_v2.py   (new)  copy of render.py with one call changed
```

This:

```text
app/feed/render.py      format_duration() next to format_timestamp(), its sibling
tests/feed/test_render.py  two cases for it
```

A `utils` module collects unrelated functions, and the next person cannot guess where anything lives. A `_v2` copy leaves two versions that drift apart. Put the function next to the code it belongs with and change the original in place.
