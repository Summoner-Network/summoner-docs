# Module: `summoner.protocol.process`

Processing primitives for routing and event flow:

* **Node**: gate or state token used in routes and tapes
* **ArrowStyle**: canonicalization and validation of arrow syntax parts
* **ParsedRoute**: normalized representation of a route (object or arrow)
* **Sender** and **Receiver**: async call sites for emitting or consuming events
* **StateTape**: typed container for active states with activation collection
* **Enums**: `Direction`, `TapeType`, `ClientIntent`

The examples below mirror the simulations you shared.

---

## Quick map

* Tokens and regex constants: `_PLAIN_TOKEN_RE`, `_ALL_RE`, `_NOT_RE`, `_ONEOF_RE`
* Sentinel: `_WILDCARD`
* Classes: `Node`, `ArrowStyle`, `ParsedRoute`, `Sender`, `Receiver`, `TapeActivation`, `StateTape`
* Enums: `Direction`, `TapeType`, `ClientIntent`

---

## Constants

### `_PLAIN_TOKEN_RE`

**Type**

`re.Pattern[str]`

**Pattern**

`^[A-Za-z_]\w*$`

**Description**

Validates plain tokens such as `A`, `foo`, `bar_2`.

---

### `_ALL_RE`

**Type**

`re.Pattern[str]`

**Pattern**

`^/all$`

**Description**

Matches the special token `/all`.

---

### `_NOT_RE`

**Type**

`re.Pattern[str]`

**Pattern**

`^/not\(\s*([^)]*?)\s*\)$`

**Description**

Matches a negation list like `/not(E,F)` and captures the comma separated payload.

---

### `_ONEOF_RE`

**Type**

`re.Pattern[str]`

**Pattern**

`^/oneof\(\s*([^)]*?)\s*\)$`

**Description**

Matches a one-of list like `/oneof(A,B)` and captures the comma separated payload.

---

### `_WILDCARD`

**Type**

`object`

**Description**

Internal sentinel used by `Node.accepts` for match table entries. Not exported.

---

## Classes and data types

### `Node`

**Summary**

Parses and normalizes a single gate/state token. Supports four kinds: `all`, `plain`, `not`, `oneof`.

**Constructor**

```python
summoner.protocol.process.Node(expr: str)
```

**Parameters**

| Name   | Type  | Required | Default | Description                                                   |
| ------ | ----- | -------- | ------- | ------------------------------------------------------------- |
| `expr` | `str` | yes      | —       | Raw token string. Leading and trailing whitespace is ignored. |

**Normalization**

* `/all` → kind `all`
* `/not(E,F)` → kind `not`, values `("E", "F")`
* `/oneof(A,B)` → kind `oneof`, values `("A", "B")`
* `A` or `abc_123` → kind `plain`, values `(token,)`

**Raises**

* `ValueError` if the token syntax is invalid.

**Methods**

```python
Node.accepts(state: Node) -> bool
```

| Name    | Type   | Required | Default | Description                      |
| ------- | ------ | -------- | ------- | -------------------------------- |
| `state` | `Node` | yes      | —       | State to test against this gate. |

**Returns**

* `bool`: whether the gate accepts the state.

**Raises**

* `TypeError` if `state` is not a `Node`.
* `RuntimeError` for an unhandled match combination (should not occur with supported kinds).

**Acceptance semantics**

The decision is table-driven. Key cases:

* `all` accepts everything.
* `plain` vs `plain`: equal names match.
* `plain` vs `not(X,...)`: match if name not in the set.
* `plain` vs `oneof(...)`: match if name in the set.
* `not(E,...)` vs `plain`: match if state not in the set.
* `not(...)` vs any state type: wildcard entries allow matching in broad contexts.
* `oneof(S)` vs `plain`: match if state in `S`.
* `oneof(S)` vs `not(T)`: match if `S \ T` is non empty.
* `oneof(S)` vs `oneof(T)`: match if `S ∩ T` is non empty.

**String forms**

* `str(Node('/all')) == '/all'`
* `str(Node('A')) == 'A'`
* `str(Node('/not(E,F)')) == '/not(E,F)'`
* `str(Node('/oneof(A,B)')) == '/oneof(A,B)'`

**Example**

```python
Node('/all').accepts(Node('X'))           # True
Node('A').accepts(Node('A'))              # True
Node('A').accepts(Node('/not(A)'))        # False
Node('A').accepts(Node('/oneof(A,B)'))    # True
```

---

### `ArrowStyle`

**Summary**

Defines the syntactic parts of an arrow for route parsing and canonicalization.

**Constructor**

```python
summoner.protocol.process.ArrowStyle(
    stem: str,
    brackets: tuple[str, str],
    separator: str,
    tip: str,
)
```

**Parameters**

| Name        | Type              | Required | Default | Description                                                                |
| ----------- | ----------------- | -------- | ------- | -------------------------------------------------------------------------- |
| `stem`      | `str`             | yes      | —       | Single character used for the arrow shaft, for example `-` or `=`.         |
| `brackets`  | `tuple[str, str]` | yes      | —       | Left and right label delimiters, for example `("[", "]")` or `("{", ")")`. |
| `separator` | `str`             | yes      | —       | Separator for multi token lists. Must not include reserved characters.     |
| `tip`       | `str`             | yes      | —       | Arrow head or terminator, for example `>` or `)`.                          |

**Validation**

* Stem must be a single character.
* Brackets, separator, and tip must be non empty strings.
* Parts must not overlap each other.
* Separator cannot contain the stem, either bracket, the tip, or any of `(`, `)`, `/`.
* Each part must be regex safe.

**Raises**

* `ValueError` on any validation failure.

**Example**

```python
ArrowStyle(stem='-', brackets=('[', ']'), separator=',', tip='>')
```

---

### `ParsedRoute`

**Summary**

Normalized representation of a route. An object route has only `source`. An arrow route has optional `source`, optional `label`, and optional `target` depending on syntax.

**Constructor**

```python
summoner.protocol.process.ParsedRoute(
    source: tuple[Node, ...],
    label: tuple[Node, ...],
    target: tuple[Node, ...],
    style: ArrowStyle | None,
)
```

**Attributes**

| Name     | Type               | Access    | Description                                            |                                             |
| -------- | ------------------ | --------- | ------------------------------------------------------ | ------------------------------------------- |
| `source` | `tuple[Node, ...]` | read-only | Gate nodes on the left side. Empty for initial arrows. |                                             |
| `label`  | `tuple[Node, ...]` | read-only | Label nodes enclosed by brackets. May be empty.        |                                             |
| `target` | `tuple[Node, ...]` | read-only | Target nodes on the right side. May be empty.          |                                             |
| `style`  | \`ArrowStyle       | None\`    | read-only                                              | Arrow style used. `None` for object routes. |

**Derived properties**

```python
has_label: bool
is_arrow: bool
is_object: bool
is_initial: bool  # arrow with empty source
```

**Methods**

```python
ParsedRoute.activated_nodes(event: Event | None) -> tuple[Node, ...]
```

Routing rule:

* If `is_object`, returns `source`.
* If `is_arrow` and `event` is `Action.MOVE`, returns `label + target`.
* If `is_arrow` and `event` is `Action.TEST`, returns `label`.
* If `is_arrow` and `event` is `Action.STAY`, returns `source`.
* Otherwise returns empty tuple.

**Equality and hashing**

Two routes are equal if their canonical string representations match. `str(route)` yields the canonical form used for keys.

**Example**

```python
from summoner.protocol.process import Node, ArrowStyle, ParsedRoute

style = ArrowStyle('-', ('[', ']'), ',', '>')
route = ParsedRoute(
    source=(Node('A'), Node('C')),
    label=(Node('f'), Node('g')),
    target=(Node('B'),),
    style=style,
)
assert str(route) == 'A,C--[f,g]-->B'
route.activated_nodes(Action.MOVE(Signal((0,), 'OK')))  # returns (f, g, B)
```

---

### `Sender`

**Summary**

Async producer side bound to a route. Can filter on action class and signal set.

**Dataclass**

```python
@dataclass(frozen=True)
class Sender:
    fn: Callable[[], Awaitable]
    multi: bool
    actions: set[type] | None
    triggers: set[Signal] | None
    def responds_to(self, event: Any) -> bool: ...
```

**Parameters**

| Name       | Type                      | Required | Default | Description                                                                      |                                                                                                                     |
| ---------- | ------------------------- | -------- | ------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `fn`       | `Callable[[], Awaitable]` | yes      | —       | Async callable to execute when eligible. No arguments.                           |                                                                                                                     |
| `multi`    | `bool`                    | yes      | —       | Whether multiple instances may run or be scheduled. Semantics defined by caller. |                                                                                                                     |
| `actions`  | \`set\[type]              | None\`   | yes     | —                                                                                | Allowed event classes, for example `{Action.MOVE, Action.TEST}`. `None` means allow all. Empty set matches nothing. |
| `triggers` | \`set\[Signal]            | None\`   | yes     | —                                                                                | Allowed signals. `None` means allow all. Empty set matches nothing.                                                 |

**Method: `responds_to`**

Returns `True` when the event class is permitted by `actions` and the event signal is in `triggers` according to:

* If `actions is not None`, must have `isinstance(event, cls)` for some `cls` in `actions`.
* If `triggers is not None`, must have `extract_signal(event) in triggers`.

**Example**

```python
sender = Sender(fn=async_lambda, multi=False,
                actions={Action.MOVE, Action.TEST},
                triggers={Trigger.OK, Trigger.minor})
assert sender.responds_to(Action.TEST(Trigger.minor))
```

---

### `Receiver`

**Summary**

Async consumer side bound to a route. Yields an `Event` or `None`.

**Dataclass**

```python
@dataclass(frozen=True)
class Receiver:
    fn: Callable[[str | dict], Awaitable[Event | None]]
    priority: tuple[int, ...]
```

**Parameters**

| Name       | Type              | Required                | Default  | Description                                                                         |   |                                                                                    |
| ---------- | ----------------- | ----------------------- | -------- | ----------------------------------------------------------------------------------- | - | ---------------------------------------------------------------------------------- |
| `fn`       | \`Callable\[\[str | dict], Awaitable\[Event | None]]\` | yes                                                                                 | — | Async handler. Receives the decoded message payload. Returns an `Event` or `None`. |
| `priority` | `tuple[int, ...]` | yes                     | —        | Lexicographic priority used for batch ordering. Empty tuple means default priority. |   |                                                                                    |

**Example**

```python
recv = Receiver(fn=my_async_handler, priority=(1, 2))
```

---

### `Direction`

**Summary**

Dispatch direction.

**Enum members**

* `SEND`
* `RECEIVE`

---

### `TapeActivation`

**Summary**

Execution record produced when a `Receiver` is eligible for a given route and tape state.

**Dataclass**

```python
@dataclass(frozen=True)
class TapeActivation:
    key: str | None
    state: Node | None
    route: ParsedRoute
    fn: Callable[[Any], Awaitable]
```

**Fields**

| Name    | Type                         | Description                    |                                                             |
| ------- | ---------------------------- | ------------------------------ | ----------------------------------------------------------- |
| `key`   | \`str                        | None\`                         | Tape key that matched. `None` for initial arrows.           |
| `state` | \`Node                       | None\`                         | The concrete state that matched. `None` for initial arrows. |
| `route` | `ParsedRoute`                | The matched route.             |                                                             |
| `fn`    | `Callable[[Any], Awaitable]` | The receiver function to call. |                                                             |

---

### `TapeType`

**Summary**

Shape classification for `StateTape` content.

**Enum members**

* `SINGLE`          — a single Node
* `MANY`            — a list of Nodes
* `INDEX_SINGLE`    — mapping `key -> Node`
* `INDEX_MANY`      — mapping `key -> list[Node]`

---

### `StateTape`

**Summary**

Typed container for states used to drive activations. Supports flexible input shapes and stable reversion to either a list or an index mapping.

**Constructor**

```python
summoner.protocol.process.StateTape(
    states: Any = None,
    with_prefix: bool = True,
)
```

**Parameters**

| Name          | Type   | Required | Default | Description                                                            |                      |            |     |      |           |
| ------------- | ------ | -------- | ------- | ---------------------------------------------------------------------- | -------------------- | ---------- | --- | ---- | --------- |
| `states`      | `Any`  | no       | `None`  | One of: `None`, `str`, `Node`, \`list\[Node                            | str]`, or `dict\[str | None, Node | str | list | tuple]\`. |
| `with_prefix` | `bool` | no       | `True`  | If mapping input is given, add the `prefix` to keys as `"tape:<key>"`. |                      |            |     |      |           |

**Attributes**

| Name     | Type                    | Access     | Description                                      |
| -------- | ----------------------- | ---------- | ------------------------------------------------ |
| `states` | `dict[str, list[Node]]` | read-write | Internal normalized storage.                     |
| `_type`  | `TapeType`              | read-write | Shape classification that controls `revert`.     |
| `prefix` | `str`                   | read-only  | Prefix used for internal keys. Default `"tape"`. |

**Methods**

```python
StateTape.set_type(value: TapeType) -> StateTape
StateTape.refresh() -> StateTape
StateTape.extend(states: Any) -> None
StateTape.revert() -> list[Node] | dict[str, list[Node]] | None
StateTape.collect_activations(
    receiver_index: dict[str, Receiver],
    parsed_routes: dict[str, ParsedRoute],
) -> dict[tuple[int, ...], list[TapeActivation]]
```

**Behavior**

* Constructor normalizes input to `states: dict[str, list[Node]]` and classifies the shape using a private `_assess_type` helper.
* `refresh` creates an empty clone with the same keys and `_type` for batch-local accumulation.
* `extend` merges states from another `StateTape`-compatible input. Keys are used as is and values are `Node`-wrapped if needed.
* `revert` returns a list when `_type in {SINGLE, MANY}` or a key-stripped dict when `_type in {INDEX_SINGLE, INDEX_MANY}`.
* `collect_activations` builds a priority index. For each `Receiver` and each tape `(key, state)`:

  * If the route is `is_initial`, add one activation with `key=None, state=None`.
  * Else, for each gate in `route.source`, add an activation when `gate.accepts(state)`.

**Examples**

*Minimal normalize and revert*

```python
from summoner.protocol.process import StateTape, Node

# index-many input
st = StateTape({"k0": ["A", "B"], "k1": [Node("C")]})
assert st.revert() == {"k0": [Node("A"), Node("B")], "k1": [Node("C")]}

# many input
st2 = StateTape(["A", "B"]).set_type(TapeType.MANY)
assert isinstance(st2.revert(), list)
```

*Activation collection*

```python
from summoner.protocol.process import StateTape, Receiver
from summoner.protocol.flow import Flow

flow = Flow(); flow.activate(); flow.ready()
route = str(flow.parse_route("A --[ f ]--> B"))

async def rcvr(payload):
    return None

ri = {route: Receiver(fn=rcvr, priority=(1,))}
pr = {route: flow.parse_route(route)}
st = StateTape({"k0": ["A"]})
index = st.collect_activations(ri, pr)
# index is a dict keyed by (1,) containing TapeActivation entries
```

---

## Enums

### `Direction`

```python
from enum import Enum, auto
class Direction(Enum):
    SEND = auto()
    RECEIVE = auto()
```

### `ClientIntent`

```python
from enum import Enum, auto
class ClientIntent(Enum):
    QUIT = auto()      # immediate exit
    TRAVEL = auto()    # switch to a new host and port
    ABORT = auto()     # abort due to error
```

---

## See also

* `summoner.protocol.triggers` for `Signal`, `Event`, `Action`, and `extract_signal`
* `summoner.protocol.flow` for parser construction and canonicalization


<p align="center">
  <a href="./triggers.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.protocol.triggers</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="./flow.md">Next: <code style="background: transparent;">Summoner<b>.protocol.flow</b></code> &raquo;</a>
</p>