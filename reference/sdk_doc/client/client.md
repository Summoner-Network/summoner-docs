# Module: `summoner.client.client`

High-level asynchronous client for Summoner servers. Handles:

* transport lifecycle (connect / run / retry / graceful shutdown)
* decorator-based registration for **receivers**, **senders**, and **hooks**
* optional **flow-aware routing** (Nodes/Routes/Triggers) and **reactive senders**
* state tape upload/download
* payload validation & typed (de)serialization
* concurrency control and back-pressure

> **Quick start** — minimal, file-free flow
>
> ```python
> from summoner.client.client import SummonerClient
> from summoner.protocol.triggers import Move
> from summoner.protocol.flow import Flow
>
> client = SummonerClient("demo-client")
>
> # Enable flow parsing and arrow styles (optional but recommended)
> client.flow().activate()
> client.flow().add_arrow_style('-', ('[', ']'), ',', '>')
>
> # Register a receiver on a route
> @client.receive("/all --[ hello ]--> B", priority=(1,))
> async def on_any(payload):
>     print("recv:", payload)
>     # return an Event to feed reactive senders; or None to do nothing
>     Trigger = client.flow().triggers(json_dict={"OK": {"minor": None}})
>     return Move(Trigger.minor)
>
> # Register a sender that fires after Move(minor) on the same route
> @client.send("/all --[ hello ]--> B", on_actions={Move})
> async def say_hi():
>     return {"msg": "hi"}
>
> client.run(host="127.0.0.1", port=8888, config_dict={"logger": {"level": "INFO"}})
> ```

---

## Public API surface

* Exception: **`ServerDisconnected`**
* Class: **`SummonerClient`**

  * Lifecycle: `run`, `run_client`, `handle_session`, `shutdown`, `set_termination_signals`
  * Flow: `flow`, `initialize`
  * Intents: `travel_to`, `quit`
  * State I/O decorators: `upload_states`, `download_states`
  * Decorators: `receive`, `send`, `hook`
  * Serialization: `dna`

---

## Exception

### `ServerDisconnected`

Raised by the recv loop when the server closes the connection (clean EOF), and used by retry logic.

---

## Class: `SummonerClient`

```python
class SummonerClient:
    DEFAULT_MAX_BYTES_PER_LINE = 64 * 1024
    DEFAULT_READ_TIMEOUT_SECONDS = None
    DEFAULT_CONCURRENCY_LIMIT = 50

    DEFAULT_RETRY_DELAY = 3
    DEFAULT_PRIMARY_RETRY_LIMIT = 3
    DEFAULT_FAILOVER_RETRY_LIMIT = 2

    DEFAULT_EVENT_BRIDGE_SIZE = 1000
    DEFAULT_MAX_CONSECUTIVE_ERRORS = 3

    core_version = "1.0.0"

    def __init__(self, name: str | None = None): ...
```

### Constructor

**Signature**

```python
SummonerClient.__init__(name: str | None = None)
```

**Parameters**

| Name   | Type  | Default | Description |                                                            |
| ------ | ----- | ------- | ----------- | ---------------------------------------------------------- |
| `name` | \`str | None\`  | `None`      | Name used by the logger; defaults to `"<client:no-name>"`. |

**Side effects**

* Creates a **new event loop** and sets it as current.
* Initializes locks, indices, worker bookkeeping, and a `Flow()` instance.

---

### Configuration

Settings are applied by `run()` via `_apply_config()` (not public) after loading a config file/dict. The effective schema:

| Path                                                | Type    | Default             | Notes                                                                    |                                                   |
| --------------------------------------------------- | ------- | ------------------- | ------------------------------------------------------------------------ | ------------------------------------------------- |
| `host`                                              | \`str   | None\`              | `None`                                                                   | Initial override for connection target.           |
| `port`                                              | \`int   | None\`              | `None`                                                                   | Initial override for connection target.           |
| `logger`                                            | `dict`  | `{}`                | Passed to `configure_logger`.                                            |                                                   |
| `hyper_parameters.reconnection.retry_delay_seconds` | `int`   | `3`                 | Sleep between attempts.                                                  |                                                   |
| `hyper_parameters.reconnection.primary_retry_limit` | \`int   | None\`              | `3`                                                                      | Attempts on primary host/port. `None` = infinite. |
| `hyper_parameters.reconnection.default_host`        | \`str   | None\`              | `host`                                                                   | Fallback host.                                    |
| `hyper_parameters.reconnection.default_port`        | \`int   | None\`              | `port`                                                                   | Fallback port.                                    |
| `hyper_parameters.reconnection.default_retry_limit` | \`int   | None\`              | `2`                                                                      | Attempts on fallback. `None` = infinite.          |
| `hyper_parameters.receiver.max_bytes_per_line`      | `int`   | `64*1024`           | Line-based protocol hard limit. Oversize lines are dropped with warning. |                                                   |
| `hyper_parameters.receiver.read_timeout_seconds`    | \`float | None\`              | `None`                                                                   | `None` waits indefinitely.                        |
| `hyper_parameters.sender.concurrency_limit`         | `int`   | `50`                | Number of async send workers. ≥ 1.                                       |                                                   |
| `hyper_parameters.sender.batch_drain`               | `bool`  | `True`              | `True` → writer drains after each batch; `False` → drain per message.    |                                                   |
| `hyper_parameters.sender.queue_maxsize`             | `int`   | `concurrency_limit` | Back-pressure capacity for send jobs. ≥ 1.                               |                                                   |
| `hyper_parameters.sender.event_bridge_maxsize`      | `int`   | `1000`              | Capacity of internal event bridge.                                       |                                                   |
| `hyper_parameters.sender.max_worker_errors`         | `int`   | `3`                 | Consecutive crashes before aborting sender loop. ≥ 1.                    |                                                   |

Validation errors raise `ValueError` with an explicit message.

---

## Flow control and triggers

```python
client.flow() -> Flow
client.initialize() -> None
```

* `flow()` exposes the internal `Flow` instance. To enable **route normalization** and **reactive senders**, call `client.flow().activate()` and add at least one `ArrowStyle` before `run()`.
* `initialize()` calls `Flow.compile_arrow_patterns()`; if the flow is not `in_use`, parsing still works but normalization/reactivity features are not enabled.

**Example**

```python
client.flow().activate()
client.flow().add_arrow_style('-', ('[', ']'), ',', '>')
client.initialize()
```

---

## Intents: travel & quit

```python
await client.travel_to(host: str, port: int) -> None
await client.quit() -> None
```

* Both are safe to call from handlers. They set internal flags under a lock; the current session exits and either **reconnects** (travel) or **shuts down** (quit).

---

## State synchronization

### `upload_states()` — decorator

Provide an async function that **returns the current state snapshot**. Used only when the flow is active.

**Signature**

```python
client.upload_states()(fn: Callable[[], Awaitable]) -> Callable
```

**Constraints (validated)**

* Must be `async def` with **no parameters**.
* Return types allowed: `None`, `str`,
  `list[str]`,
  `dict[str, str]`, `dict[str, list[str]]`, or `dict[str, str | list[str]]`.

The snapshot is normalized by `StateTape` and used to collect receiver activations.

**Example**

```python
@client.upload_states()
async def states():
    # examples:
    # return "A"  # SINGLE
    # return ["A", "B"]  # MANY
    return {"k0": ["A", "C"], "k1": ["/all"]}  # INDEX_MANY
```

---

### `download_states()` — decorator

Provide an async function that **receives** a normalized state view after each receiver batch when the flow is active.

**Signature**

```python
client.download_states()(fn: Callable[[Any], Awaitable]) -> Callable
```

**Constraints (validated)**

* Must be `async def`.
* Parameter may be any of: `None`, `Node`, `list[Node]`, `dict[str|None, Node|list[Node]]` (the method accepts multiple structurally equivalent typings).
* Return types allowed: `None`, `bool`, any.

**Example**

```python
@client.download_states()
async def observe(tape):
    # tape is list[Node] or dict[str, list[Node]] depending on initial shape
    print("tape:", tape)
```

---

## Decorators for handlers

### `hook(direction, priority=())`

Register a validation/transform **hook** that runs **before receivers** (on payload in) or **before writers** (on payload out).

**Signature**

```python
client.hook(
    direction: Direction,
    priority: int | tuple[int, ...] = (),
)(fn: Callable[[str | dict | Any | None], Awaitable[str | dict | None]])
```

**Rules**

* Must be `async def` taking **one argument** (payload) and returning either a modified payload or `None` to drop it.
* `direction` is `Direction.RECEIVE` or `Direction.SEND`.
* `priority` orders hooks lexicographically (lower tuples run first). A plain `int` is coerced to `(int,)`.

**Example**

```python
@client.hook(Direction.RECEIVE, priority=(0,))
async def reject_empty(payload):
    return None if payload in (None, "", {}) else payload
```

---

### `receive(route, priority=())`

Register an async **receiver** for a route. The function gets the **decoded payload** and returns an **`Event`** (to enable reactive senders) or `None`.

**Signature**

```python
client.receive(
    route: str,
    priority: int | tuple[int, ...] = (),
)(fn: Callable[[str | dict | Any], Awaitable[Event | None]])
```

**Validation**

* Must be `async def` and accept **exactly one parameter**.
* Allowed param types: any (`str`, `dict`, ...). Return type: `Event | None`.
* `route` must be a `str`.
* `priority` as in hooks.

**Flow-aware behavior**

* If `Flow.in_use` is **True**, the route is parsed & canonicalized; activations are collected from the current state-tape and batched by priority.
* Otherwise, receivers are just grouped by their declared priority.

**Example**

```python
@client.receive("A --[ f ]--> B", priority=(1,))
async def handle(payload):
    # do work and optionally emit an Event
    Trigger = client.flow().triggers(json_dict={"OK": None})
    return Event(Trigger.OK)  # or Move/Stay/Test
```

---

### `send(route, multi=False, on_triggers=None, on_actions=None)`

Register an async **sender** for a route. The function takes **no arguments** and returns a payload to transmit.

**Signature**

```python
client.send(
    route: str,
    multi: bool = False,
    on_triggers: set[Signal] | None = None,
    on_actions: set[type] | None = None,
)(fn: Callable[[], Awaitable])
```

**Validation**

* Must be `async def` with **no parameters**.
* When `multi=False`: return `None | Any | str | dict` (single payload).
* When `multi=True`: return `None | list[str] | list[dict] | list[str|dict]` (batch), each item becomes a send.
* `on_triggers` must be `None` **or** a `set` of `Signal`.
* `on_actions` must be `None` **or** a `set` drawn from `{Action.MOVE, Action.STAY, Action.TEST}`.

**Reactive senders (flow active)**

* If both `Flow.in_use` and at least one of `on_actions` / `on_triggers` is non-empty, the sender is **reactive**:

  * It is scheduled **only** when there exists a **pending activation** from a receiver whose `ParsedRoute` **matches** the sender route and whose returned **Event** passes `sender.responds_to(Event)`.
  * Matching uses route acceptance (`source`, `label`, `target`) and signal/action filters.
* If both are `None`, the sender is **non-reactive** and is scheduled each cycle.

**Example**

```python
from summoner.protocol.triggers import Move
Trigger = client.flow().triggers(json_dict={"OK": {"minor": None}})

@client.send("/all --[ hello ]--> B", on_actions={Move}, on_triggers={Trigger.minor})
async def greet():
    return {"event": "minor move seen"}
```

---

## Serialization and DNA

### `dna()`

Serialize all registered decorators into a JSON string that captures type (`receive`|`send`|`hook`), decorator parameters, module/function names, and the **source code** of each async function.

```python
client.dna() -> str
```

This is useful for reproducing or migrating client behavior.

---

## Running the client

### `run(host='127.0.0.1', port=8888, config_path=None, config_dict=None)`

Entry point that: loads config, applies settings, prepares the flow, installs termination signals, **awaits registration**, and runs the retry loop.

* Supply either `config_path` **or** `config_dict`. When both are omitted, defaults are used.
* Blocks the current thread until exit, then ensures workers and tasks are awaited, and closes the loop.

**Example**

```python
client.run(
    host="127.0.0.1", port=8888,
    config_dict={
        "logger": {"level": "INFO"},
        "hyper_parameters": {
            "sender": {"concurrency_limit": 10}
        }
    })
```

### `run_client` and `handle_session` (advanced)

* `run_client` implements the two-stage retry (primary → fallback) and examines `ClientIntent` after a successful session to decide whether to quit or travel.
* `handle_session` establishes a TCP connection, launches the **receiver** and **sender** loops, and coordinates their shutdown via a shared `asyncio.Event`.

---

## I/O loops (behavioral reference)

### Receiver loop

* Reads framed lines (`StreamReader.readline`), with optional timeout. Oversized lines are dropped.
* Decodes with `recover_with_types` to preserve JSON vs. plain string types.
* Applies **RECEIVE hooks** in priority order; `None` halts processing.
* Flow inactive → group receivers by priority and run.
* Flow active → build `StateTape` from `upload_states()`,
  collect **activations**, run each batch, compute **activated nodes** via `ParsedRoute.activated_nodes(event)`, and pass an optional **download** view to `download_states()`.
* Emits `(priority, key, parsed_route, event)` tuples onto an **event bridge** for the sender loop.

### Sender loop

* Builds a batch of `(route, sender)`

  * **Non-reactive**: always eligible each cycle.
  * **Reactive**: eligible only if any pending activation both **route-accepts** and **responds_to(event)**.
* Warns when the pending puts would exceed 80% of queue capacity (back-pressure).
* Queues work into `send_queue`. Workers consume, apply **SEND hooks**, wrap with `wrap_with_types(version=core_version)`, and write to the socket.
* Consecutive worker failures ≥ `max_worker_errors` cause a controlled shutdown of the sender loop.

---

## Error reference (common)

* Mis-typed decorator argument (e.g., `priority="high"`) → `ValueError` with details.
* Non-async handler in any decorator → `TypeError` (explicit message).
* `@receive` handler not accepting exactly one parameter → `TypeError`.
* `@send` handler with parameters → `TypeError`.
* Invalid `on_triggers`/`on_actions` types → `TypeError` with expected forms.
* Flow inactive while relying on reactive filters → sender is treated as non-reactive.

---

## End-to-end example (flow-aware, reactive)

```python
from summoner.client.client import SummonerClient
from summoner.protocol.triggers import Move, Stay

client = SummonerClient("agent-1")
client.flow().activate()
client.flow().add_arrow_style('-', ('[', ']'), ',', '>')
Trigger = client.flow().triggers(text="""
OK
  acceptable
  all_good
error
  minor
  major
""")

@client.upload_states()
async def states():
    return {"session": ["A", "C"], "peer": ["/all"]}

@client.download_states()
async def observe(view):
    print("view:", view)

@client.hook(Direction.RECEIVE, priority=0)
async def keep_json(payload):
    return payload  # no-op

@client.receive("A --[ hello ]--> B", priority=(1,))
async def recv(payload):
    if payload == {"cmd": "go"}:
        return Move(Trigger.minor)
    return None

@client.send("A --[ hello ]--> B", on_actions={Move}, on_triggers={Trigger.minor})
async def send_response():
    return {"ok": True}

client.run(host="127.0.0.1", port=8888, config_dict={"logger": {"level": "INFO"}})
```

---

## See also

* `summoner.protocol.triggers` — `Signal`, `Event`, `Action`, trigger loading
* `summoner.protocol.process` — `Node`, `ParsedRoute`, `StateTape`, `Receiver`, `Sender`
* `summoner.protocol.flow` — route parsing and arrow styles


<p align="center">
  <a href="../client.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.client</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="./merger.md">Next: <code style="background: transparent;">Summoner<b>.client.merger</b></code> &raquo;</a>
</p>