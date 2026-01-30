# <code style="background: transparent;">Summoner<b>.client.client</b></code> (core v1.1.1)

This page documents the **Python SDK interface** for running a Summoner client via `SummonerClient`. It focuses on how to use the class and its methods, and what behavior to expect when you call them.

A Summoner client connects to a Summoner server over TCP, continuously receives newline-delimited messages, runs user-defined handlers registered via decorators (for receive/send/hooks/state sync), and optionally emits messages back to the server. The client also supports **reconnection**, **fallback**, and **agent travel** (switching host/port at runtime) through the SDK surface.

`SummonerClient` is the primary SDK entry point for running a client process. It handles configuration loading (from a file path or in-memory dict), logger initialization, termination signal handling (where supported), handler registration, and the overall client lifecycle (connect, run loops, shutdown).

## `SummonerClient.__init__`

```python
def __init__(self, name: Optional[str] = None) -> None
```

### Behavior

Creates a client instance and prepares internal state for running client sessions.

* Sets a logical `name` used for logging.

* Creates a dedicated asyncio event loop for this client instance and sets it as the current loop.

* Initializes internal registries and locks for:

  * route registration (receivers and senders),
  * hook registration (send/receive validation hooks),
  * active task tracking,
  * connection intent (travel/quit).

* Initializes flow support (`Flow`) used for route parsing and state-driven activation.

### Inputs

#### `name`

* **Type:** `Optional[str]`
* **Meaning:** A human-readable identifier for logs and diagnostics.
* **Default behavior:** If `name` is not a string, a placeholder is used (`"<client:no-name>"`).

### Outputs

This constructor returns a `SummonerClient` instance.

### Examples

#### Basic initialization

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")
```

## `SummonerClient.run`

```python
def run(
    self,
    host: str = "127.0.0.1",
    port: int = 8888,
    config_path: Optional[str] = None,
    config_dict: Optional[dict[str, Any]] = None,
) -> None
```

### Behavior

Starts the client and blocks the calling thread until the client stops.

At a high level, `run(...)` does six things:

1. Loads configuration (from `config_dict` or `config_path`).
2. Applies configuration to internal runtime settings (logger, reconnection, receiver/sender parameters).
3. Initializes flow parsing metadata.
4. Installs termination signal handlers (where supported).
5. Awaits completion of all decorator registrations scheduled before runtime.
6. Runs the client session loop with reconnection and fallback behavior.

This method is the normal entry point for SDK usage.

### Inputs

#### `host`

* **Type:** `str`
* **Meaning:** Initial target host to connect to.
* **Default:** `"127.0.0.1"`

#### `port`

* **Type:** `int`
* **Meaning:** Initial target port to connect to.
* **Default:** `8888`

#### `config_path`

* **Type:** `Optional[str]`
* **Meaning:** Path to a JSON configuration file.
* **When used:** Used when `config_dict` is not provided.

#### `config_dict`

* **Type:** `Optional[dict[str, Any]]`
* **Meaning:** In-memory configuration dictionary.
* **Precedence:** If provided, it is used instead of `config_path`.
* **Validation:** Must be a `dict` or `None`. Any other type raises `TypeError`.

#### Configuration keys used by `run(...)`

This method expects configuration keys such as:

* `host`, `port` (optional): default connection target (may be overridden by `run(host, port)` at the SDK call site).
* `logger` (optional): logging configuration.
* `hyper_parameters` (optional): client runtime tuning, including:

  * `hyper_parameters.reconnection`
  * `hyper_parameters.receiver`
  * `hyper_parameters.sender`

The full set of configuration keys is documented in the [configuration guide for the client](configs.md).

### Outputs

* Returns `None`.
* This call **blocks** until the client exits.
* The client attempts a clean shutdown on `KeyboardInterrupt` and cancellation.

### Examples

#### Minimal usage (no config file)

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")
client.run(host="127.0.0.1", port=8888)
```

#### Load from a JSON config file

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")
client.run(
    host="127.0.0.1",
    port=8888,
    config_path="client.json",
)
```

#### Pass config as a dictionary

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")
client.run(
    host="127.0.0.1",
    port=8888,
    config_dict={
        "logger": {"log_level": "INFO", "enable_console_log": True},
        "hyper_parameters": {
            "reconnection": {"primary_retry_limit": 3, "retry_delay_seconds": 2},
            "receiver": {"max_bytes_per_line": 65536, "read_timeout_seconds": None},
            "sender": {"concurrency_limit": 20},
        },
    },
)
```

## `SummonerClient.flow`

```python
def flow(self) -> Flow
```

### Behavior

Returns the `Flow` object owned by this client. This is the object used to define and parse routes and to enable flow-driven activation.

### Inputs

None.

### Outputs

Returns a `Flow` instance.

### Examples

#### Enable and configure flow before running

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")

flow = client.flow()
# flow.enable(...) or flow.add(...) depending on your Flow API
```

## `SummonerClient.initialize`

```python
def initialize(self) -> None
```

### Behavior

Initializes flow metadata by compiling route patterns used by the flow parser.

This is called by `run(...)` as part of startup. You usually do not need to call it directly unless you embed the client lifecycle manually.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

#### Manual initialization (advanced)

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")
client.initialize()
```

## `SummonerClient.upload_states`

```python
def upload_states(self) -> Callable[[Callable[[], Awaitable[Any]]], Callable[[], Awaitable[Any]]]
```

### Behavior

Decorator used to register an **async** function that returns the current state snapshot for the flow system.

If flow is enabled, the receiver loop can call this function to obtain state, build a `StateTape`, compute activations, and schedule receivers accordingly.

This decorator must be used before `client.run()`.

### Inputs

### Outputs

Returns a decorator. The decorated function is stored on the client as the upload-state provider.

### Examples

#### Register an upload-state function

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")

@client.upload_states()
async def upload():
    return {"stage": "idle", "room": "alpha"}
```

## `SummonerClient.download_states`

```python
def download_states(self) -> Callable[[Callable[[Any], Awaitable[Any]]], Callable[[Any], Awaitable[Any]]]
```

### Behavior

Decorator used to register an **async** function that receives a `StateTape`-compatible payload after receiver batches execute.

If flow is enabled, the client updates the tape during receiver execution and then calls this function with the updated snapshot.

This decorator must be used before `client.run()`.

### Inputs

### Outputs

Returns a decorator. The decorated function is stored on the client as the download-state consumer.

### Examples

#### Register a download-state function

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")

@client.download_states()
async def download(tape):
    # Persist tape to memory/DB if desired
    return None
```

## `SummonerClient.hook`

```python
def hook(
    self,
    direction: Direction,
    priority: Union[int, tuple[int, ...]] = (),
) -> Callable[[Callable[[Optional[Union[str, dict]]], Awaitable[Optional[Union[str, dict]]]]], Callable[..., Any]]
```

### Behavior

Decorator used to register an **async hook** that runs on payloads:

* **Direction.RECEIVE:** after a message is received and decoded, before receiver handlers run.
* **Direction.SEND:** before a payload is encoded and sent to the server.

Hooks are ordered by `priority`. A hook may:

* return a transformed payload (string/dict/other supported payload types), or
* return `None` to drop the payload (skip further processing for that payload).

This decorator must be used before `client.run()` (recommended) although registration is scheduled safely.

### Inputs

#### `direction`

* **Type:** `Direction`
* **Meaning:** Whether the hook applies on receive or send.

#### `priority`

* **Type:** `Union[int, tuple[int, ...]]`
* **Meaning:** Ordering key for hook execution. Lower priorities run earlier (based on the SDK's ordering rule).
* **Default:** `()`

### Outputs

Returns a decorator.

### Examples

#### Receive hook that drops messages

```python
from summoner.client import SummonerClient
from summoner.protocol.process import Direction

client = SummonerClient(name="summoner:client")

@client.hook(Direction.RECEIVE, priority=0)
async def drop_empty(payload):
    if payload is None:
        return None
    return payload
```

#### Send hook that normalizes payloads

```python
from summoner.client import SummonerClient
from summoner.protocol.process import Direction

client = SummonerClient(name="summoner:client")

@client.hook(Direction.SEND, priority=0)
async def normalize(payload):
    if isinstance(payload, dict) and "type" not in payload:
        payload["type"] = "message"
    return payload
```

## `SummonerClient.receive`

```python
def receive(
    self,
    route: str,
    priority: Union[int, tuple[int, ...]] = (),
) -> Callable[[Callable[[Union[str, dict]], Awaitable[Optional[Event]]]], Callable[..., Any]]
```

### Behavior

Decorator used to register an **async receiver handler** that is called when messages are received.

Receivers are grouped and executed in batches by `priority`. When flow is enabled, the route may be parsed and used for activation logic; otherwise the raw route is used as the index key.

The decorated function must:

* be `async`
* accept exactly one argument (the payload)
* return `Optional[Event]` (or `None`)

### Inputs

#### `route`

* **Type:** `str`
* **Meaning:** Logical route string used for indexing and (optionally) flow parsing.

#### `priority`

* **Type:** `Union[int, tuple[int, ...]]`
* **Meaning:** Batch ordering key.
* **Default:** `()`

### Outputs

Returns a decorator.

### Examples

#### Register a simple receiver

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")

@client.receive(route="chat.message", priority=0)
async def on_message(payload):
    # payload is typically a dict or string depending on upstream encoding
    return None
```

## `SummonerClient.send`

```python
def send(
    self,
    route: str,
    multi: bool = False,
    on_triggers: Optional[set[Signal]] = None,
    on_actions: Optional[set[Type]] = None,
) -> Callable[[Callable[[], Awaitable[Any]]], Callable[..., Any]]
```

### Behavior

Decorator used to register an **async sender handler** that produces outbound payloads.

Senders are executed by the sender loop and enqueue output payloads to be encoded and written to the server connection.

* If `multi=False`, the sender returns a single payload (or `None`).
* If `multi=True`, the sender returns a list of payloads (or `None` entries).

When flow is enabled, `on_triggers` / `on_actions` can be used to make a sender reactive to activation events. From an SDK perspective, these parameters declare when a sender is eligible to run.

### Inputs

#### `route`

* **Type:** `str`
* **Meaning:** Logical route string used for indexing and (optionally) flow parsing.

#### `multi`

* **Type:** `bool`
* **Meaning:** Whether the sender returns multiple payloads per invocation.
* **Default:** `False`

#### `on_triggers`

* **Type:** `Optional[set[Signal]]`
* **Meaning:** Optional trigger set that gates sender execution in flow-enabled mode.

#### `on_actions`

* **Type:** `Optional[set[Type]]`
* **Meaning:** Optional action set that gates sender execution in flow-enabled mode. This is validated against allowed action event classes.

### Outputs

Returns a decorator.

### Examples

#### Single-payload sender

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")

@client.send(route="chat.send")
async def send_one():
    return {"kind": "chat", "data": "hello"}
```

#### Multi-payload sender

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")

@client.send(route="chat.send", multi=True)
async def send_many():
    return [{"data": "a"}, {"data": "b"}, {"data": "c"}]
```

## `SummonerClient.travel_to`

```python
async def travel_to(self, host: str, port: int) -> None
```

### Behavior

Requests that the client **travel** to a new server address (host/port). This sets an internal intent flag checked by the session loops.

In typical use, you call this from within a receiver or sender handler to migrate the client to another server endpoint.

### Inputs

#### `host`

* **Type:** `str`
* **Meaning:** Destination host.

#### `port`

* **Type:** `int`
* **Meaning:** Destination port.

### Outputs

An awaitable coroutine. Returns `None`.

### Examples

#### Travel from inside a receiver

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")

@client.receive("control.travel")
async def on_travel(payload):
    await client.travel_to(host="127.0.0.1", port=9999)
    return None
```

## `SummonerClient.quit`

```python
async def quit(self) -> None
```

### Behavior

Requests that the client exit cleanly. This sets an internal intent flag that is checked by the session loops. In typical use, you call this from within a receiver or sender handler.

### Inputs

None.

### Outputs

An awaitable coroutine. Returns `None`.

### Examples

#### Quit from inside a receiver

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")

@client.receive("control.quit")
async def on_quit(payload):
    await client.quit()
    return None
```

## `SummonerClient.dna`

```python
def dna(self, include_context: bool = False) -> str
```

### Behavior

Serializes this client's registered behavior (decorated handlers and related metadata) into a JSON string called "DNA".

At the SDK level, DNA is used to support cloning and merging workflows by capturing:

* handler type (receive/send/hook/upload_states/download_states),
* route keys and priorities (where applicable),
* handler source code,
* optional context metadata when `include_context=True`.

### Inputs

#### `include_context`

* **Type:** `bool`
* **Meaning:** If `True`, includes a `__context__` header with best-effort imports/globals/recipes/missing bindings used by handlers.
* **Default:** `False`

### Outputs

Returns a JSON string.

### Examples

#### Export DNA (handlers only)

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")
dna_json = client.dna()
```

#### Export DNA with context

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")
dna_json = client.dna(include_context=True)
```

## `SummonerClient.set_termination_signals`

```python
def set_termination_signals(self) -> None
```

### Behavior

Installs process termination signal handlers on non-Windows platforms.

* Registers handlers for:

  * SIGINT (Ctrl+C)
  * SIGTERM (process termination)

* Each handler triggers `shutdown()`.

On Windows, signal handler installation is skipped.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

You normally do not call this directly because `run(...)` calls it as part of normal startup.

## `SummonerClient.shutdown`

```python
def shutdown(self) -> None
```

### Behavior

Triggers client shutdown by cancelling all tasks in the client's event loop.

This is typically invoked through signal handlers or process interruption.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

#### Programmatic shutdown (advanced)

```python
from summoner.client import SummonerClient

client = SummonerClient(name="summoner:client")
client.shutdown()
```

## `SummonerClient.run_client`

```python
async def run_client(self, host: str = "127.0.0.1", port: int = 8888) -> None
```

### Behavior

Runs the client's reconnection state machine.

This coroutine:

* attempts a "primary stage" connection loop using the provided `host`/`port`,
* on repeated failures, falls back to configured default host/port (if configured),
* exits cleanly on `/quit`,
* restarts primary behavior on `/travel`.

In typical SDK usage, you do not call this directly; it is run by `run(...)`.

### Inputs

#### `host`

* **Type:** `str`
* **Meaning:** Primary connection host.
* **Default:** `"127.0.0.1"`

#### `port`

* **Type:** `int`
* **Meaning:** Primary connection port.
* **Default:** `8888`

### Outputs

An awaitable coroutine. Returns `None` when the client finishes.

### Examples

This method is usually called internally by `run(...)`.

## `SummonerClient.handle_session`

```python
async def handle_session(self, host: str = "127.0.0.1", port: int = 8888) -> None
```

### Behavior

Runs a single connected session: one receiver loop and one sender loop concurrently.

* Opens a TCP connection to the current host/port (including dynamic overrides from travel).
* Starts background send workers to execute sender handlers.
* Runs `message_receiver_loop(...)` and `message_sender_loop(...)` concurrently.
* Ends the session when one side completes (disconnect, travel, quit), then cancels the other side.
* Closes the connection and cleans up workers and tracked tasks.

In typical SDK usage, you do not call this directly; it is used as part of the reconnection logic.

### Inputs

#### `host`

* **Type:** `str`
* **Meaning:** Session host (used as fallback if the client has no dynamic host override).
* **Default:** `"127.0.0.1"`

#### `port`

* **Type:** `int`
* **Meaning:** Session port (used as fallback if the client has no dynamic port override).
* **Default:** `8888`

### Outputs

An awaitable coroutine. Returns when the session ends.

### Examples

This method is usually called internally by `run_client(...)`.

## `SummonerClient.message_receiver_loop`

```python
async def message_receiver_loop(
    self,
    reader: asyncio.StreamReader,
    stop_event: asyncio.Event,
) -> None
```

### Behavior

Continuously reads messages from the server, applies receive hooks, and dispatches receiver handlers.

At a high level:

* Reads one newline-delimited message (with size and timeout controls).
* Decodes the message into a relayed payload type.
* Applies receiving hooks in priority order.
* Runs receiver handlers in batches (by priority). If flow is enabled, batches may be activation-driven.
* If flow is enabled, forwards activation events across the event bridge to the sender side.
* Exits when `stop_event` is set, the server disconnects, or the task is cancelled.

### Inputs

#### `reader`

* **Type:** `asyncio.StreamReader`
* **Meaning:** Read side of the TCP connection.

#### `stop_event`

* **Type:** `asyncio.Event`
* **Meaning:** Cooperative termination signal shared with the sender loop.

### Outputs

An awaitable coroutine. Returns when the session ends or raises `ServerDisconnected` on EOF, depending on shutdown path.

### Examples

This method is usually called internally by `handle_session(...)`.

## `SummonerClient.message_sender_loop`

```python
async def message_sender_loop(
    self,
    writer: asyncio.StreamWriter,
    stop_event: asyncio.Event,
) -> None
```

### Behavior

Continuously schedules and enqueues sender handlers for execution, then ensures outbound payloads are written to the server.

At a high level:

* Builds a sender batch from registered senders.
* If flow is enabled, may gate senders based on pending activation events and route matching.
* Enqueues work to a bounded queue (backpressure to producers when full).
* Waits for the queue batch to finish (`send_queue.join()`).
* Drains the writer according to `batch_drain`.
* Exits when `stop_event` is set, travel/quit intent is detected, or the task is cancelled.

### Inputs

#### `writer`

* **Type:** `asyncio.StreamWriter`
* **Meaning:** Write side of the TCP connection.

#### `stop_event`

* **Type:** `asyncio.Event`
* **Meaning:** Cooperative termination signal shared with the receiver loop.

### Outputs

An awaitable coroutine. Returns when the session ends.

### Examples

This method is usually called internally by `handle_session(...)`.

## End-to-end example

### Example: run a client with one receiver and one sender

#### client.py

```python
from summoner.client import SummonerClient
from summoner.protocol.process import Direction

client = SummonerClient(name="summoner:client")

@client.receive("chat.message", priority=0)
async def on_message(payload):
    client.logger.info(f"received: {payload!r}")
    return None

@client.send("chat.send")
async def send_message():
    # Return a payload to send; returning None sends nothing this cycle
    return {"kind": "chat", "data": "hello"}

client.run(
    host="127.0.0.1",
    port=8888,
    config_dict={
        "logger": {"log_level": "INFO", "enable_console_log": True},
        "hyper_parameters": {
            "sender": {"concurrency_limit": 10, "queue_maxsize": 10},
            "receiver": {"read_timeout_seconds": None},
        },
    },
)
```

#### behavior

* The client connects to the server at `127.0.0.1:8888`.
* Incoming messages are passed through receive hooks (if any) and then dispatched to `@receive` handlers.
* Outbound senders are executed by background workers and their payloads are written to the server connection.

---

<p align="center">
  <a href="../client.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.client</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="./configs.md">Next: <code style="background: transparent;">Summoner<b>.client</b></code> configuration guide &raquo;</a>
</p>