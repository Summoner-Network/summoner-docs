# <code style="background: transparent;">Summoner<b>.protocol.process</b></code>

This page documents the **protocol-layer data structures** used by Summoner clients and flows.

The module defines:

* `Node`: a token model used as a **gate** (matching incoming state).
* `ArrowStyle` and `ParsedRoute`: a parsed representation of routes (objects or arrows).
* `Sender`, `Receiver`, `Direction`: protocol wrappers used by the client runtime.
* `StateTape`: an in-memory tape of active states, plus activation discovery.
* `ClientIntent`: a small enum used by the client lifecycle (quit vs travel vs abort).



## `class Node`

```python
class Node
```

### Behavior

Represents a token used as either:

* a **gate** (pattern) in a route source, or
* a **state** stored on a `StateTape`.

A `Node` is created from a single expression string and is normalized into:

* `kind` in `{ "plain", "all", "not", "oneof" }`
* `values` as `tuple[str]` or `None`

Accepted syntaxes:

* Plain token: `foo`, `ok_1`, `StateX`
* All wildcard: `/all`
* Negation set: `/not(a,b,c)`
* One-of set: `/oneof(a,b,c)`

Invalid syntax raises `ValueError`.

### Inputs

#### `expr`

* **Type:** `str`
* **Meaning:** Token expression that defines the node.

### Outputs

A `Node` instance.

### Examples

```python
from summoner.protocol.process import Node

Node("OK")
Node("/all")
Node("/not(minor,major)")
Node("/oneof(a,b,c)")
```



## `Node.accepts`

```python
def accepts(self, state: Node) -> bool
```

### Behavior

Checks whether this node (the gate) accepts another node (the state).

This is used when matching a parsed route's `source` nodes (gates) against states stored on a `StateTape`.

Key cases:

* `/all` accepts any state.
* A plain gate matches plain state if names match.
* A plain gate accepts `/oneof(...)` if the gate token is in the set.
* A plain gate accepts `/not(...)` if the gate token is not in the forbidden set.
* A `/oneof(...)` gate accepts a plain state if the state token is in the set.
* A `/oneof(...)` gate accepts another `/oneof(...)` if the sets intersect.
* A `/not(...)` gate accepts a plain state if the state token is not in the forbidden set.

If `state` is not a `Node`, raises `TypeError`.

### Inputs

#### `state`

* **Type:** `Node`
* **Meaning:** Concrete state node to test against this gate.

### Outputs

* **Type:** `bool`
* **Meaning:** `True` if accepted, else `False`.

### Examples

```python
from summoner.protocol.process import Node

gate = Node("/oneof(a,b)")
assert gate.accepts(Node("a")) is True
assert gate.accepts(Node("c")) is False

gate = Node("x")
assert gate.accepts(Node("/not(a,b)")) is True
assert gate.accepts(Node("/not(x,y)")) is False
```



## `class ArrowStyle`

```python
class ArrowStyle
```

### Behavior

Describes the syntax used to render an "arrow route" string. It defines:

* `stem`: single character used for the arrow shaft (example `-`)
* `brackets`: label delimiters (example `("[", "]")`)
* `separator`: token separator inside segments (example `","`)
* `tip`: arrow terminator (example `">"`)

The constructor validates:

* `stem` is exactly 1 character.
* all parts are non-empty strings.
* no part overlaps another (substring conflicts).
* `separator` does not contain reserved characters used by the parser or style.
* style parts are safe to use with `re.escape`.

### Inputs

#### `stem`

* **Type:** `str`
* **Meaning:** One-character arrow shaft marker.

#### `brackets`

* **Type:** `tuple[str, str]`
* **Meaning:** Left and right bracket strings for the label part.

#### `separator`

* **Type:** `str`
* **Meaning:** Separator for multiple tokens within a segment.

#### `tip`

* **Type:** `str`
* **Meaning:** Arrow head or terminator string.

### Outputs

An `ArrowStyle` instance.

### Examples

```python
from summoner.protocol.process import ArrowStyle

style = ArrowStyle(
    stem="-",
    brackets=("[", "]"),
    separator=",",
    tip=">",
)
```



## `class ParsedRoute`

```python
class ParsedRoute
```

### Behavior

Represents a parsed route in a structured form:

* `source`: tuple of gate `Node`s
* `label`: tuple of label `Node`s
* `target`: tuple of target `Node`s
* `style`: optional `ArrowStyle` used for rendering

The string form of the route is precomputed and used for equality and hashing.

Interpretation:

* If the route has `target` or `label`, it is treated as an **arrow route**.
* If it has no label and no target, it is treated as an **object route** (only source nodes).

### Inputs

#### `source`

* **Type:** `tuple[Node, ...]`

#### `label`

* **Type:** `tuple[Node, ...]`

#### `target`

* **Type:** `tuple[Node, ...]`

#### `style`

* **Type:** `Optional[ArrowStyle]`

### Outputs

A `ParsedRoute` instance.

### Examples

```python
from summoner.protocol.process import Node, ParsedRoute, ArrowStyle

style = ArrowStyle("-", ("[", "]"), ",", ">")

r = ParsedRoute(
    source=(Node("A"),),
    label=(Node("L"),),
    target=(Node("B"),),
    style=style,
)

assert r.is_arrow is True
assert r.has_label is True
```



## `ParsedRoute.has_label`

```python
@property
def has_label(self) -> bool
```

### Behavior

Returns `True` when the route has at least one label node.

### Outputs

`bool`



## `ParsedRoute.is_arrow`

```python
@property
def is_arrow(self) -> bool
```

### Behavior

Returns `True` when the route has a target or a label. This indicates an arrow route.

### Outputs

`bool`



## `ParsedRoute.is_object`

```python
@property
def is_object(self) -> bool
```

### Behavior

Returns `True` when the route is not an arrow route. This indicates an object route.

### Outputs

`bool`



## `ParsedRoute.is_initial`

```python
@property
def is_initial(self) -> bool
```

### Behavior

Returns `True` for arrow routes that have no source gates. These are "initial" routes that can fire without matching tape state.

### Outputs

`bool`



## `ParsedRoute.activated_nodes`

```python
def activated_nodes(self, event: Optional[Event]) -> tuple[Node, ...]
```

### Behavior

Given an event (typically one of `Action.MOVE`, `Action.STAY`, `Action.TEST`), returns the nodes that should be added to the tape.

Rules:

* **Object route** (`is_object`):

  * `Action.TEST`: activates nothing
  * any other `Event`: activates `source`
* **Arrow route** (`is_arrow`):

  * `Action.MOVE`: activates `label + target`
  * `Action.TEST`: activates `label`
  * `Action.STAY`: activates `source`
* Any other input returns `()`.

### Inputs

#### `event`

* **Type:** `Optional[Event]`
* **Meaning:** The event produced by a receiver or state machine step.

### Outputs

* **Type:** `tuple[Node, ...]`
* **Meaning:** Nodes to be appended to a `StateTape`.

### Examples

```python
from summoner.protocol.process import Node, ParsedRoute, ArrowStyle
from summoner.protocol.triggers import Action, Signal

style = ArrowStyle("-", ("[", "]"), ",", ">")
r = ParsedRoute(
    source=(Node("A"),),
    label=(Node("L"),),
    target=(Node("B"),),
    style=style,
)

sig = Signal((0,), "OK")
assert r.activated_nodes(Action.MOVE(sig)) == (Node("L"), Node("B"))
assert r.activated_nodes(Action.TEST(sig)) == (Node("L"),)
assert r.activated_nodes(Action.STAY(sig)) == (Node("A"),)
```



## `@dataclass Sender`

```python
@dataclass(frozen=True)
class Sender
```

### Behavior

Represents a sending handler registered by a client:

* `fn`: async callable that produces a payload (or multiple payloads)
* `multi`: whether `fn` returns a list of payloads
* `actions`: optional set of event classes that gate execution
* `triggers`: optional set of `Signal` values that gate execution

Senders are "reactive" when `actions` or `triggers` is set. The runtime calls `responds_to(event)` to decide whether a sender should run for a given event.

### Fields

* `fn`: `Callable[[], Awaitable]`
* `multi`: `bool`
* `actions`: `Optional[set[Type]]`
* `triggers`: `Optional[set[Signal]]`

### Examples

```python
from summoner.protocol.process import Sender
# In SDK usage, Sender is usually created internally by SummonerClient decorators.
```



## `Sender.responds_to`

```python
def responds_to(self, event: Any) -> bool
```

### Behavior

Checks whether `event` satisfies the sender's action and trigger filters:

* If `actions` is set: `event` must be an instance of at least one class in `actions`.
* If `triggers` is set: `extract_signal(event)` must equal at least one signal in `triggers`.

If a filter is `None`, it is treated as "no constraint".

### Inputs

#### `event`

* **Type:** `Any`
* **Meaning:** An event-like object produced by receiver logic, typically an `Event` or `Signal`.

### Outputs

`bool`



## `@dataclass Receiver`

```python
@dataclass(frozen=True)
class Receiver
```

### Behavior

Represents a receiving handler registered by a client:

* `fn`: async callable that consumes a payload and returns an optional `Event`
* `priority`: a tuple used for batch ordering

### Fields

* `fn`: `Callable[[Union[str, dict]], Awaitable[Optional[Event]]]`
* `priority`: `tuple[int, ...]`

### Examples

```python
from summoner.protocol.process import Receiver
# In SDK usage, Receiver is usually created internally by SummonerClient decorators.
```



## `class Direction`

```python
class Direction(Enum)
```

### Behavior

Indicates whether a hook or handler belongs to the sending side or receiving side.

Values:

* `Direction.SEND`
* `Direction.RECEIVE`

### Examples

```python
from summoner.protocol.process import Direction

assert Direction.SEND.name == "SEND"
```



## `@dataclass TapeActivation`

```python
@dataclass(frozen=True)
class TapeActivation
```

### Behavior

Represents one activation of a receiver due to a tape match.

Fields capture:

* `key`: the tape key that matched (or `None` for initial routes)
* `state`: the concrete tape state that matched (or `None` for initial routes)
* `route`: the parsed route that matched
* `fn`: the receiver function to execute

### Fields

* `key`: `Optional[str]`
* `state`: `Optional[Node]`
* `route`: `ParsedRoute`
* `fn`: `Callable[[Any], Awaitable]`



## `class TapeType`

```python
class TapeType(Enum)
```

### Behavior

Internal classification of tape input/output shapes:

* `SINGLE`: a single state
* `MANY`: a list of states
* `INDEX_SINGLE`: dict key → single state
* `INDEX_MANY`: dict key → list of states

This type is inferred by `StateTape` on construction and influences `revert()`.



## `class StateTape`

```python
class StateTape
```

### Behavior

Stores active states as a mapping:

* internal storage: `dict[str, list[Node]]`
* keys are prefixed by default with `tape:` (configurable by `with_prefix`)

Accepted constructor inputs:

* `None` or unrecognized: creates an empty index-many tape.
* `str` or `Node`: treated as `SINGLE`.
* `list[str|Node]` or `tuple[str|Node]`: treated as `MANY`.
* `dict[key -> str|Node]`: treated as `INDEX_SINGLE`.
* `dict[key -> (str|Node|list|tuple)]`: treated as `INDEX_MANY`.

The tape is used by flow-enabled clients to decide which receivers should run.

### Inputs

#### `states`

* **Type:** `Any`
* **Meaning:** Initial tape content, in one of the accepted shapes.

#### `with_prefix`

* **Type:** `bool`
* **Meaning:** Whether to prefix keys with `tape:` when building internal storage.
* **Default:** `True`

### Outputs

A `StateTape` instance.

### Examples

```python
from summoner.protocol.process import StateTape, Node

t1 = StateTape("A")                       # SINGLE
t2 = StateTape(["A", "B"])                # MANY
t3 = StateTape({"x": "A"})                # INDEX_SINGLE
t4 = StateTape({"x": ["A", Node("B")]})   # INDEX_MANY
```



## `StateTape.extend`

```python
def extend(self, states: Any) -> None
```

### Behavior

Extends the tape with additional states.

The method constructs a local `StateTape` from `states` (without adding prefixes), then merges:

* missing keys are created
* nodes are appended to existing lists

### Inputs

#### `states`

* **Type:** `Any`
* **Meaning:** Additional tape content in any accepted constructor shape.

### Outputs

Returns `None`.

### Examples

```python
from summoner.protocol.process import StateTape

tape = StateTape({"x": ["A"]})
tape.extend({"x": ["B"], "y": ["C"]})
```



## `StateTape.refresh`

```python
def refresh(self) -> StateTape
```

### Behavior

Creates a fresh tape with the same set of keys but empty node lists. The returned tape keeps the same inferred tape type.

This is commonly used to compute the "next tape" in a flow step.

### Outputs

A new `StateTape` instance.

### Examples

```python
from summoner.protocol.process import StateTape

tape = StateTape({"x": ["A"], "y": ["B"]})
fresh = tape.refresh()
assert fresh.revert() == {"x": [], "y": []}
```



## `StateTape.revert`

```python
def revert(self) -> Union[list[Node], dict[str, list[Node]], None]
```

### Behavior

Converts internal tape storage back into an external representation:

* For `SINGLE` and `MANY`: returns a single flattened `list[Node]`.
* For index types: returns `dict[str, list[Node]]` with prefixes removed.

### Outputs

* `list[Node]` or `dict[str, list[Node]]` depending on tape type.

### Examples

```python
from summoner.protocol.process import StateTape

assert StateTape("A").revert() == [StateTape("A").revert()[0]]
assert isinstance(StateTape({"x": "A"}).revert(), dict)
```



## `StateTape.collect_activations`

```python
def collect_activations(
    self,
    receiver_index: dict[str, Receiver],
    parsed_routes: dict[str, ParsedRoute],
) -> dict[tuple[int, ...], list[TapeActivation]]
```

### Behavior

Computes which receivers should run, based on current tape states and parsed route gates.

For each `route -> receiver` in `receiver_index`:

* Looks up `ParsedRoute` in `parsed_routes`. If missing, skips it.
* If the route is initial (`parsed_route.is_initial`), it activates once unconditionally.
* Otherwise, for every `(key, state)` on the tape, checks whether any gate in `parsed_route.source` accepts the state.

  * If a gate matches, produces a `TapeActivation(key, state, parsed_route, receiver.fn)`.

Returned activations are indexed by receiver priority (`receiver.priority`).

### Inputs

#### `receiver_index`

* **Type:** `dict[str, Receiver]`
* **Meaning:** Receiver registry keyed by route string.

#### `parsed_routes`

* **Type:** `dict[str, ParsedRoute]`
* **Meaning:** Parsed routes keyed by normalized route string.

### Outputs

* **Type:** `dict[tuple[int, ...], list[TapeActivation]]`
* **Meaning:** Activations grouped by priority.

### Examples

```python
from summoner.protocol.process import StateTape, Receiver, ParsedRoute, Node, ArrowStyle

async def recv(payload):
    return None

receiver_index = {"A": Receiver(fn=recv, priority=())}
parsed_routes  = {"A": ParsedRoute(source=(Node("A"),), label=(), target=(), style=None)}

tape = StateTape(["A", "B"])
acts = tape.collect_activations(receiver_index=receiver_index, parsed_routes=parsed_routes)

assert () in acts
assert len(acts[()]) >= 1
```



## `class ClientIntent`

```python
class ClientIntent(Enum)
```

### Behavior

Represents the client's lifecycle intent:

* `QUIT`: immediate exit
* `TRAVEL`: reconnect to a new host/port
* `ABORT`: abort due to error

This enum is typically produced by the client runtime logic, not by protocol parsing.

### Examples

```python
from summoner.protocol.process import ClientIntent

assert ClientIntent.TRAVEL.name == "TRAVEL"
```

---


<p align="center">
  <a href="./triggers.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.protocol.triggers</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="./flow.md">Next: <code style="background: transparent;">Summoner<b>.protocol.flow</b></code> &raquo;</a>
</p>