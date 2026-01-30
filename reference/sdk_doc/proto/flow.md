# <code style="background: transparent;">Summoner<b>.protocol.flow</b></code>

This page documents the **flow parser** used by Summoner to interpret route strings into structured `ParsedRoute` objects.

The module provides:

* `get_token_list`: tokenizes a segment using a separator while respecting parentheses.
* `Flow`: a parser configured by one or more `ArrowStyle`s.
* `Flow.triggers`: loads a dynamic `Trigger` class (signals tree) for use with flows.
* `Flow.parse_route` / `Flow.parse_routes`: converts route strings into `ParsedRoute`.

It depends on:

* `Node`, `ArrowStyle`, `ParsedRoute` from `summoner.protocol.process`
* `load_triggers` from `summoner.protocol.triggers`



## Route strings

A route string is parsed into three segments:

* `source`: gate nodes (match against tape state)
* `label`: nodes activated on `TEST` or `MOVE`
* `target`: nodes activated on `MOVE`

There are two categories:

### Object route (standalone)

No arrow syntax. Example:

```text
A,B,/not(x,y)
```

This produces a `ParsedRoute` with:

* `source=(Node("A"), Node("B"), Node("/not(x,y)"))`
* `label=()`, `target=()`, `style=None`

### Arrow route (style-dependent)

Arrow parsing requires at least one `ArrowStyle` registered on the `Flow`. A style defines:

* arrow stem character (doubled in syntax)
* label brackets
* token separator inside segments
* arrow tip

A labeled arrow looks like:

```text
<source>  <stem><stem><left_bracket> <label> <right_bracket><stem><stem><tip>  <target>
```

An unlabeled arrow looks like:

```text
<source>  <stem><stem><tip>  <target>
```

The parser also supports **dangling** variants where `source` or `target` may be empty.



## Token syntax

Individual tokens must match a conservative pattern:

* optional leading `/`
* identifier (`[A-Za-z_]\w*`)
* optional parentheses group `(...)` with no nesting

Examples of valid tokens:

* `A`
* `/all`
* `/not(x,y)`
* `/oneof(a,b,c)`
* `foo(bar,baz)` (tokenization respects parentheses)

Invalid tokens raise `ValueError` during parsing.



## `get_token_list`

```python
def get_token_list(input_string: str, separator: str) -> list[str]
```

### Behavior

Splits `input_string` by `separator`, but only at "top level":

* separators inside parentheses are ignored
* empty tokens are dropped
* tokens are stripped of surrounding whitespace

This is used for parsing `source`, `label`, and `target` segments.

### Inputs

#### `input_string`

* **Type:** `str`
* **Meaning:** The raw segment to split.

#### `separator`

* **Type:** `str`
* **Meaning:** The separator to split on (usually `","` or a style-specific separator).

### Outputs

* **Type:** `list[str]`
* **Meaning:** Non-empty tokens.

### Examples

```python
from summoner.protocol.flow import get_token_list

assert get_token_list("foo,bar(baz,qux),zap", ",") == ["foo", "bar(baz,qux)", "zap"]
assert get_token_list("  A  ,  B , ", ",") == ["A", "B"]
```



## `class Flow`

```python
class Flow
```

### Behavior

A configurable parser that converts route strings into `ParsedRoute`.

A `Flow` holds:

* `triggers_file`: optional filename for the triggers tree
* `in_use`: whether the flow is active (affects compilation behavior)
* `arrows`: a set of registered `ArrowStyle` instances
* internal regex cache compiled from arrow styles

The parser does not require a `Flow` for object routes, but arrow parsing is driven by the styles registered on the flow.

### Constructor

```python
def __init__(self, triggers_file: Optional[str] = None) -> None
```

#### Inputs

* `triggers_file`: optional triggers filename. If `None`, uses the default `"TRIGGERS"` behavior of `load_triggers()`.

#### Outputs

A `Flow` instance.

### Example

```python
from summoner.protocol.flow import Flow

flow = Flow().activate()
```



## `Flow.activate`

```python
def activate(self) -> Flow
```

### Behavior

Sets `in_use=True` and returns `self`.

This flag is used to decide whether regex patterns should be prepared/compiled (it is common for a client to activate a flow before registering routes).

### Outputs

* **Type:** `Flow`
* **Meaning:** `self`

### Example

```python
flow = Flow().activate()
assert flow.in_use is True
```



## `Flow.deactivate`

```python
def deactivate(self) -> Flow
```

### Behavior

Sets `in_use=False` and returns `self`.

### Outputs

* **Type:** `Flow`
* **Meaning:** `self`



## `Flow.add_arrow_style`

```python
def add_arrow_style(
    self,
    stem: str,
    brackets: tuple[str, str],
    separator: str,
    tip: str
) -> None
```

### Behavior

Constructs an `ArrowStyle` and registers it in `self.arrows`.

Side effects:

* invalidates the internal regex cache (`_regex_ready=False`)
* clears existing compiled patterns

All style validation happens in `ArrowStyle`.

### Inputs

#### `stem`

* **Type:** `str`
* **Meaning:** One-character arrow shaft marker. The syntax uses it doubled (`stem * 2`).

#### `brackets`

* **Type:** `tuple[str, str]`
* **Meaning:** Label delimiters.

#### `separator`

* **Type:** `str`
* **Meaning:** Token separator within each segment.

#### `tip`

* **Type:** `str`
* **Meaning:** Arrow tip / terminator.

### Outputs

* **Type:** `None`
* **Meaning:** Mutates the flow (registers an arrow style).

### Example

```python
from summoner.protocol.flow import Flow

flow = Flow().activate()
flow.add_arrow_style(stem="-", brackets=("[", "]"), separator=",", tip=">")
```

With this style, a labeled route may look like:

```text
A,B--[L]-->C,D
```

and an unlabeled route may look like:

```text
A>B
```

(Exact formatting depends on the style parts. The parser uses `stem * 2` inside patterns.)



## `Flow.triggers`

```python
def triggers(self, json_dict: Optional[dict[str, Any]] = None) -> type
```

### Behavior

Loads a dynamic `Trigger` class (signals tree) using `load_triggers`.

Priority:

* if `json_dict` is provided: `load_triggers(json_dict=json_dict)`
* else if `self.triggers_file` is set: `load_triggers(triggers_file=...)`
* else: `load_triggers()` using the default `TRIGGERS`

### Inputs

#### `json_dict`

* **Type:** `Optional[dict[str, Any]]`
* **Meaning:** A nested signal tree dict as accepted by `load_triggers`.

### Outputs

* **Type:** `type`
* **Meaning:** A dynamically built `Trigger` class (attributes are `Signal` instances).

### Example

```python
from summoner.protocol.flow import Flow

Trigger = Flow().triggers()
# Trigger.OK, Trigger.error, etc. depending on TRIGGERS content
```



## `Flow.compile_arrow_patterns`

```python
def compile_arrow_patterns(self) -> None
```

### Behavior

Compiles regex patterns from the currently registered `ArrowStyle`s.

* Safe to call multiple times.
* Does nothing unless `in_use=True`.
* Sets up internal pattern list used by `parse_route`.

In typical `SummonerClient` usage, compilation is handled automatically during handler registration, so manual calls are usually only needed in standalone parsing contexts.

### Outputs

* **Type:** `None`

### Example

```python
flow = Flow().activate()
flow.add_arrow_style("-", ("[", "]"), ",", ">")
flow.compile_arrow_patterns()
```



## `Flow.ready` (deprecated)

```python
def ready(self) -> None
```

### Behavior

Deprecated alias for `compile_arrow_patterns`.

* Emits a `DeprecationWarning`.
* Calls internal compilation when `in_use=True`.

### Outputs

* **Type:** `None`

### Migration

Use:

```python
flow.compile_arrow_patterns()
```



## `Flow.parse_route`

```python
def parse_route(self, route: str) -> ParsedRoute
```

### Behavior

Parses a single route string into a `ParsedRoute`.

Steps:

1. Trims whitespace.
2. Ensures arrow regex patterns are prepared (based on registered arrow styles).
3. Tries each compiled arrow pattern:

   * If matched:

     * extracts raw `source`, `label`, `target` strings (depending on variant)
     * tokenizes each segment using the style’s `separator` with `get_token_list`
     * validates tokens against the token regex
     * returns a `ParsedRoute(source=..., label=..., target=..., style=style)`
4. If no arrow pattern matches:

   * parses as a standalone object route using comma separator
   * returns `ParsedRoute(..., style=None)`

Token validation errors raise `ValueError`.

### Inputs

#### `route`

* **Type:** `str`
* **Meaning:** Route string in object or arrow form.

### Outputs

* **Type:** `ParsedRoute`

### Examples

#### Object route

```python
from summoner.protocol.flow import Flow

flow = Flow()
r = flow.parse_route("A,B,/not(x,y)")
assert r.is_object is True
assert str(r) == "A,B,/not(x,y)"
```

#### Arrow route (requires an arrow style)

```python
from summoner.protocol.flow import Flow

flow = Flow().activate()
flow.add_arrow_style(stem="-", brackets=("[", "]"), separator=",", tip=">")
flow.compile_arrow_patterns()

r = flow.parse_route("A--[L]-->B")
assert r.is_arrow is True
assert r.has_label is True
assert [str(n) for n in r.source] == ["A"]
assert [str(n) for n in r.label] == ["L"]
assert [str(n) for n in r.target] == ["B"]
```

#### Parentheses in tokens

```python
from summoner.protocol.flow import Flow

flow = Flow().activate()
flow.add_arrow_style("-", ("[", "]"), ",", ">")
flow.compile_arrow_patterns()

r = flow.parse_route("foo(x,y)--[lab(a,b)]-->bar")
assert [str(n) for n in r.source] == ["foo(x,y)"]
assert [str(n) for n in r.label] == ["lab(a,b)"]
assert [str(n) for n in r.target] == ["bar"]
```



## `Flow.parse_routes`

```python
def parse_routes(self, routes: list[str]) -> list[ParsedRoute]
```

### Behavior

Parses a list of routes by calling `parse_route` on each element.

### Inputs

#### `routes`

* **Type:** `list[str]`

### Outputs

* **Type:** `list[ParsedRoute]`

### Example

```python
from summoner.protocol.flow import Flow

flow = Flow().activate()
flow.add_arrow_style("-", ("[", "]"), ",", ">")

parsed = flow.parse_routes(["A,B", "A--[L]-->B"])
assert len(parsed) == 2
```



## Notes on failure modes

* If an arrow route uses a style that has not been registered, it will not match any arrow pattern and will fall back to object parsing. In that case, token validation may fail (for example, because the arrow symbols appear inside the "tokens").
* Token validation is strict by design. If you need richer syntax inside tokens, you must extend the parser constraints consistently across `Node` and the flow tokenizer.


<p align="center">
  <a href="./process.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.protocol.process</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../proto.md">Next: <code style="background: transparent;">Summoner<b>.protocol</b></code> &raquo;</a>
</p>