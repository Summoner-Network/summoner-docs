# Module: `summoner.protocol.flow`

Parses human readable routes into canonical `ParsedRoute` objects using configurable arrow styles. Also exposes a loader for the `Trigger` namespace built from TRIGGERS definitions.

**Typical workflow**

```python
from summoner.protocol.flow import Flow

flow = Flow().activate()
flow.add_arrow_style(stem='-', brackets=('[', ']'), separator=',', tip='>')
flow.add_arrow_style(stem='=', brackets=('{', '}'), separator=';', tip=')')
flow.compile_arrow_patterns()  # Optional: precompile arrow style(s) listed above

r1 = flow.parse_route('A --[ f, g ]--> B, C')
assert str(r1) == 'A--[f,g]-->B,C' and r1.is_arrow

r2 = flow.parse_route('/all')
assert str(r2) == '/all' and r2.is_object
```

---

## Quick map

* Tokenizer: `get_token_list`
* `Flow` lifecycle: `activate`, `deactivate`, `add_arrow_style`, `ready`
* Parsing: `parse_route`, `parse_routes`
* Triggers: `triggers` (delegates to `load_triggers`)
* Constants: `_TOKEN_RE` (token validation)

---

## Constants

### `_TOKEN_RE`

**Type**

`re.Pattern[str]`

**Pattern**

```
^/?[A-Za-z_]\w*(?:\([^)]*\))?$
```

**Description**

Validates a single token possibly prefixed with `/` and with an optional parenthesized suffix without nesting. Examples that match: `A`, `foo_bar`, `/all`, `/not(E,F)`, `/oneof(A,B)`.

---

## Functions

### `get_token_list`

**Summary**

Split a string on a top level separator while ignoring separators that appear inside parentheses. Returns trimmed, non empty tokens.

**Signature**

```python
summoner.protocol.flow.get_token_list(input_string: str, separator: str) -> list[str]
```

**Parameters**

| Name           | Type  | Required | Default | Description                                         |
| -------------- | ----- | -------- | ------- | --------------------------------------------------- |
| `input_string` | `str` | yes      | —       | The raw text to split.                              |
| `separator`    | `str` | yes      | —       | The character used to separate tokens at top level. |

**Returns**

* `list[str]`: list of tokens with whitespace removed around each token.

**Example**

```python
get_token_list('foo,bar(baz,qux), zap', ',')  # ['foo', 'bar(baz,qux)', 'zap']
```

---

## Class: `Flow`

**Summary**

Maintains parser configuration and converts route strings to canonical `ParsedRoute` objects. Also loads the dynamic `Trigger` class for signals.

**Constructor**

```python
summoner.protocol.flow.Flow(triggers_file: str | None = None)
```

**Parameters**

| Name            | Type  | Required | Default | Description |                                                                                                                                    |
| --------------- | ----- | -------- | ------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `triggers_file` | \`str | None\`   | no      | `None`      | Custom TRIGGERS filename used by `triggers()`. If `None`, uses the default adjacent `TRIGGERS` file from `triggers.load_triggers`. |

**Attributes**

| Name     | Type              | Access     | Description                                              |
| -------- | ----------------- | ---------- | -------------------------------------------------------- |
| `in_use` | `bool`            | read write | When `True`, `compile_arrow_patterns()` will compile regexes immediately. |
| `arrows` | `set[ArrowStyle]` | read write | Registered arrow styles used to build the parser.        |

**Methods**

### `activate`

**Signature**

```python
Flow.activate(self) -> Flow
```

**Description**

Mark the instance as in use and return `self` for chaining.

**Example**

```python
flow = Flow().activate()
```

---

### `deactivate`

**Signature**

```python
Flow.deactivate(self) -> Flow
```

**Description**

Mark the instance as not in use and return `self` for chaining.

---

### `add_arrow_style`

**Signature**

```python
Flow.add_arrow_style(
    self,
    stem: str,
    brackets: tuple[str, str],
    separator: str,
    tip: str,
) -> None
```

**Parameters**

| Name        | Type              | Required | Default | Description                                                                             |
| ----------- | ----------------- | -------- | ------- | --------------------------------------------------------------------------------------- |
| `stem`      | `str`             | yes      | —       | Single character for the shaft, for example `-` or `=`.                                 |
| `brackets`  | `tuple[str, str]` | yes      | —       | Label delimiters. For example `('[', ']')` or `('{', '}')`.                             |
| `separator` | `str`             | yes      | —       | Token separator inside source, label, and target. Must satisfy `ArrowStyle` validation. |
| `tip`       | `str`             | yes      | —       | Arrow head or terminator, for example `>` or `)`.                                       |

**Behavior**

Creates an `ArrowStyle`, adds it to `arrows`, and clears cached regex patterns to force rebuild on next parse.

**Raises**

* `ValueError` propagated from `ArrowStyle` on invalid parts or conflicts.

**Example**

```python
flow.add_arrow_style(stem='-', brackets=('[', ']'), separator=',', tip='>')
```

---

### `triggers`

**Signature**

```python
Flow.triggers(self, json_dict: dict[str, Any] | None = None) -> type
```

**Parameters**

| Name        | Type              | Required | Default | Description |                                                                                                                                            |
| ----------- | ----------------- | -------- | ------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `json_dict` | \`dict[str, Any] | None\`   | no      | `None`      | If provided, builds the `Trigger` class directly from this nested mapping. Otherwise reads from `triggers_file` or the default `TRIGGERS`. |

**Returns**

* `type`: the dynamic `Trigger` class with `Signal` attributes.

**Example**

```python
Trigger = flow.triggers()            # from file
Trigger2 = flow.triggers(json_dict={"OK": None})
```

---

### `compile_arrow_patterns`

**Signature**

```python
Flow.compile_arrow_patterns(self) -> None
```

**Description**

If `in_use` is `True`, compile regex patterns for all registered arrow styles. If `in_use` is `False`, parsing will still work because `parse_route` auto prepares on first use.

**Example**

```python
flow.activate() 
flow.add_arrow_style('-', ('[', ']'), ',', '>')
flow.compile_arrow_patterns()
```

---

### `parse_route`

**Signature**

```python
Flow.parse_route(self, route: str) -> ParsedRoute
```

**Parameters**

| Name    | Type  | Required | Default | Description                                                               |
| ------- | ----- | -------- | ------- | ------------------------------------------------------------------------- |
| `route` | `str` | yes      | —       | Raw route string to parse. Whitespace around tokens and parts is ignored. |

**Returns**

* `ParsedRoute`: canonical route. `str(result)` is normalized using registered style separators and no extraneous spaces.

**Behavior**

* Ensures regex patterns are prepared.
* Tries each labeled pattern, then unlabeled patterns for every `ArrowStyle`.
* On match, splits `source`, `label`, `target` using the style`s `separator`with`get_token_list`, validates tokens with `_TOKEN_RE`, and builds a `ParsedRoute\`.
* If none match, treats the input as a standalone object list separated by commas and validates with `_TOKEN_RE`.

**Raises**

* `ValueError` if any token fails `_TOKEN_RE` validation. The error message includes the offending token and the full route text.

**Examples**

```python
# Arrow with label and targets
flow = Flow().activate()
flow.add_arrow_style('-', ('[', ']'), ',', '>')

r = flow.parse_route('A, C --[ f, g ]--> B, K')
assert str(r) == 'A,C--[f,g]-->B,K'
assert r.is_arrow and r.has_label

# Standalone object
assert str(flow.parse_route(' /all ')) == '/all'

# Dangling right (no target)
assert flow.parse_route('E =={ f }==)').is_arrow

# Dangling left (no source)
assert flow.parse_route(' ==) F ').is_arrow
```

---

### `parse_routes`

**Signature**

```python
Flow.parse_routes(self, routes: list[str]) -> list[ParsedRoute]
```

**Parameters**

| Name     | Type        | Required | Default | Description                     |
| -------- | ----------- | -------- | ------- | ------------------------------- |
| `routes` | `list[str]` | yes      | —       | List of route strings to parse. |

**Returns**

* `list[ParsedRoute]`: parsed routes in the same order.

**Example**

```python
result = flow.parse_routes(['A --> B', '/all'])
[str(r) for r in result]  # ['A--[]-->B', '/all'] after normalization
```

---

## Route grammar

**Arrow styles**

An arrow style is defined by `stem`, `brackets`, `separator`, and `tip`. The shaft is the stem repeated twice. Examples:

* `--[ label ]-->` with separator `,`
* `=={ label }==)` with separator `;`

**Recognized forms per style**

* Labeled complete: `source  stem*2 left label right stem*2 tip  target`
* Labeled dangling left: `stem*2 left label right stem*2 tip  target`
* Labeled dangling right: `source  stem*2 left label right stem*2 tip`
* Unlabeled complete: `source  stem*2 tip  target`
* Unlabeled dangling left: `stem*2 tip  target`
* Unlabeled dangling right: `source  stem*2 tip`

Whitespace is optional around parts. Source, label, and target each hold zero or more tokens separated by the style separator.

**Tokens**

A token must match `_TOKEN_RE`. Examples:

* Plain: `A`, `foo_bar`
* Special with leading slash: `/all`, `/not(E,F)`, `/oneof(A,B)`

**Validation**

Invalid tokens raise `ValueError` with a message like: `Invalid token 'inv&alid' in route 'A --> inv&alid'`.

---

## See also

* `summoner.protocol.triggers` for building the `Trigger` class
* `summoner.protocol.process` for `ArrowStyle`, `Node`, and `ParsedRoute` semantics



<p align="center">
  <a href="./process.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.protocol.process</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../proto.md">Next: <code style="background: transparent;">Summoner<b>.protocol</b></code> &raquo;</a>
</p>