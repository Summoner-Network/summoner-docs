# <code style="background: transparent;">Summoner<b>.aurora</b></code> (aurora beta.1.1.2)

This page documents the **Aurora extension interface** layered on top of the core Python client SDK. Aurora introduces `SummonerAgent`, a subclass of `SummonerClient` that adds the following capabilities to the receive path:

* `@agent.keyed_receive(...)`: a receiver decorator that enforces per-entity mutual exclusion and optional replay protection.

A `SummonerAgent` behaves like a normal `SummonerClient` for connection lifecycle, hooks, routing, flow integration, reconnection, and travel. Aurora only changes how a receiver handler is *wrapped* at registration time.

> [!NOTE]
> In the `extension-agentclass` repository, local tests may import this module as `from tooling.aurora import SummonerAgent`. In a composed SDK, import from `summoner.aurora`.

## Typical usage

Aurora is useful when a client-side agent is acting as an orchestrator for shared state, and you want high concurrency without races. A typical example is a peer-to-peer game or simulation where an agent maintains a world model in memory: each player (or entity) produces events concurrently, but updates for the same entity must be applied in order and without overlap.

`@keyed_receive(...)` provides this pattern by serializing handler execution per `(route, key)` while still allowing different keys to run concurrently. If you also provide `seq_by`, the handler can drop stale or duplicated messages for the same key using an in-memory last-seen sequence cache.

For example, a client-side "game master" agent might receive frequent movement ticks and UI overlay events from many players. Aurora makes it possible to express that intent directly in the receive decorators, so the concurrency policy is visible next to the handler logic. For example, you can register:

* `@agent.keyed_receive("directions", key_by="pid")` to serialize movement updates per player, and
* `@agent.keyed_receive("overlay", key_by="pid", seq_by="seq")` to serialize overlays per player while dropping replays,

In the context of a MMO-style game, this would keep the world model consistent while still processing different players concurrently.


## `SummonerAgent`

`SummonerAgent` extends the base client by adding a keyed receiver decorator. The decorator serializes handler execution for messages that share the same `(route, key)` while preserving concurrency across different keys.

Aurora also maintains an in-memory sequence cache to drop stale or duplicate messages when an optional monotonic sequence extractor is configured.

### `SummonerAgent.__init__`

```python
def __init__(self, name: Optional[str] = None)
```

#### Behavior

Creates an agent client instance and prepares internal keyed-concurrency state.

* Calls `SummonerClient.__init__(name)` to initialize the core client behavior (event loop, registries, locks, flow support, lifecycle).
* Initializes keyed mutual exclusion state:

  * `self._key_mutex: Optional[AsyncKeyedMutex]` is set to `None` and is lazily constructed on first `@keyed_receive(...)` registration.
  * `self._seq_seen: dict[tuple[str, Hashable], int]` stores last-seen sequences per `(route, key)` for optional replay protection.

#### Inputs

##### `name`

* **Type:** `Optional[str]`
* **Meaning:** Human-readable identifier for logs and diagnostics.
* **Default behavior:** Delegated to the base client constructor.

#### Outputs

Returns a `SummonerAgent` instance.

#### Example

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")
```

### `SummonerAgent.keyed_receive`

```python
def keyed_receive(
    self,
    route: str,
    key_by: Union[str, Callable[[Any], Hashable]],
    priority: Union[int, tuple[int, ...]] = (),
    seq_by: Union[None, str, Callable[[Any], int]] = None,
)
```

#### Behavior

Registers an **async receiver handler** that enforces:

1. **Per-key mutual exclusion** within a Python process, and
2. Optional **replay protection** based on a monotonic sequence field.

The decorator wraps the user handler so that, for a given `(normalized_route, key)`, only one invocation runs at a time. Messages for different keys execute concurrently.

If `seq_by` is provided, the wrapper drops stale or duplicate messages whose sequence is less than or equal to the last sequence seen for that `(normalized_route, key)`.

At a high level, `keyed_receive(...)` does the following:

1. Strips leading and trailing whitespace from `route`.

2. Builds a key extractor from `key_by`:

   * If `key_by` is a string, it is treated as a dict key (when the payload is a dict) or an attribute name (otherwise).
   * If `key_by` is callable, it is invoked as `key_by(payload)`.
   * In both cases, failures and unhashable keys are treated as invalid and cause the message to be dropped.

3. Builds a sequence extractor from `seq_by`:

   * If `seq_by` is not provided, replay protection is disabled.
   * If `seq_by` is a string, it is treated as a dict key (when the payload is a dict) or an attribute name (otherwise).
   * If `seq_by` is callable, it is invoked as `seq_by(payload)`.
   * The result is converted to `int` best-effort. Failures produce `None` for that message, disabling replay checking for it.

4. Validates that the handler is `async` and raises `TypeError` if it is not.

5. Captures DNA metadata for the receiver in the same shape as the base class receiver capture.

6. Schedules a registration coroutine that:

   * lazily initializes `AsyncKeyedMutex` on first use,
   * resolves flow route parsing and normalization when flow is enabled,
   * installs the wrapped handler into the client receiver index.

##### Mutual exclusion semantics

* Lock granularity is `(normalized_route, key)`.
* Different routes do not share locks, even if they compute the same key.
* The lock covers the entire handler body.

##### Replay semantics

* Replay protection is enabled only when `seq_by` is provided and extraction returns an integer.
* For each `(normalized_route, key)`, the wrapper maintains `last_seen_seq` in memory.
* Any message with `seq <= last_seen_seq` is dropped.
* Sequence state is kept in `self._seq_seen` and resets on process restart.

##### Flow integration

When flow is enabled:

* The decorator attempts to parse the supplied `route`.
* If parsing succeeds, `str(parsed_route)` is used as the runtime route key and the parsed route is stored in the client for later use.
* If parsing fails, the raw route is registered and a warning is logged.

##### Error handling

The wrapper is defensive by default:

* Key extraction failures drop the message instead of raising into the dispatcher.
* Missing or unhashable keys drop the message.
* Sequence extraction failures disable replay checking for that message.
* Exceptions raised while executing the wrapped handler path are caught and logged, and the wrapper returns `None`.

#### Inputs

##### `route`

* **Type:** `str`
* **Meaning:** Logical route string, with the same semantics as `@receive`.
* **Normalization:** Leading/trailing whitespace is stripped.
* **Flow:** If flow is enabled, route parsing may normalize the effective route key.

##### `key_by`

* **Type:** `Union[str, Callable[[Any], Hashable]]`
* **Meaning:** Extractor used to compute the per-entity key.
* **String behavior:** Dict key (if payload is a dict) or attribute name (otherwise).
* **Callable behavior:** Called as `key_by(payload)`.
* **Validation:** Keys must be hashable. Missing, invalid, or unhashable keys cause the message to be dropped.
* **Required:** If `key_by` is `None`, `ValueError` is raised.

##### `priority`

* **Type:** `Union[int, tuple[int, ...]]`
* **Meaning:** Receiver priority, identical to `@receive`.
* **Default:** `()`
* **Normalization:** If an integer is provided, it is converted to a 1-tuple `(priority,)`.

##### `seq_by`

* **Type:** `Union[None, str, Callable[[Any], int]]`
* **Meaning:** Optional monotonic sequence extractor for replay protection.
* **String behavior:** Dict key (if payload is a dict) or attribute name (otherwise).
* **Callable behavior:** Called as `seq_by(payload)`.
* **Conversion:** Best-effort `int(...)`. Failures yield `None` for that message, disabling replay checking for it.
* **State:** Stored in-memory in `self._seq_seen` and resets on process restart.

#### Outputs

Returns a decorator. The decorated function is registered as a receiver handler, but the internal dispatcher executes a wrapped function that applies locking and optional replay logic.

#### Handler contract

The decorated handler must:

* be `async`
* accept exactly one argument (the payload)
* return `Optional[Event]` (or `None`), consistent with the base receiver contract

If the function is not async, `TypeError` is raised at decoration time.

#### Limitations and operational notes

* **Critical-section scope:** The lock covers the entire handler body. Keep work inside the lock short and move slow I/O out of the critical section when possible.
* **Fairness:** The underlying lock is not strictly FIFO.
* **Process scope:** Mutual exclusion is per Python process and event loop. It does not serialize work across processes or machines.
* **Sequence cache growth:** `self._seq_seen` is not pruned in the current implementation. For long-lived processes with many distinct keys, an eviction policy may be required.

#### Examples

##### Serialize per-player updates

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")

@agent.keyed_receive("game:move", key_by="player_id", priority=0)
async def on_move(payload):
    # Only one move per (route, player_id) runs at a time.
    return None
```

##### Drop replays using a monotonic sequence number

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")

@agent.keyed_receive("account:update", key_by="account_id", seq_by="seq")
async def on_account_update(payload):
    # Drops any payload with seq <= last seen for this (route, account_id).
    return None
```

##### Composite keys and derived sequences

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")

@agent.keyed_receive(
    "player:event",
    key_by=lambda p: (p["zone_id"], p["player"]["id"]),
    seq_by=lambda p: int(p["meta"]["ts_ns"]),
)
async def on_player_event(payload):
    return None
```

## `AsyncKeyedMutex` (not exposed)

`AsyncKeyedMutex` is an internal utility used by Aurora. It provides keyed mutual exclusion using `asyncio.Lock`, with automatic lock lifecycle management.

```python
class AsyncKeyedMutex:
    def lock(self, key: Hashable):
        ...
```

### `AsyncKeyedMutex.lock`

```python
def lock(self, key: Hashable)
```

#### Behavior

Returns an async context manager that enforces mutual exclusion for the given key.

The implementation:

* Maintains a mapping `key -> asyncio.Lock`.
* Maintains a reference count per key so locks are removed when no guards are active.
* Uses a global guard lock to serialize creation and deletion of per-key locks.
* Handles cancellation during lock acquisition by decrementing the key refcount and cleaning up the lock when needed.

This utility manages lock objects to reduce lock-table growth for keys that are no longer in use. It does not provide strict FIFO fairness beyond what `asyncio.Lock` provides.

#### Inputs

##### `key`

* **Type:** `Hashable`
* **Meaning:** Key that identifies the lock domain.

#### Outputs

Returns an async context manager usable as:

```python
async with mutex.lock(key):
    ...
```

#### Notes

* Fairness is inherited from `asyncio.Lock` and is not strictly FIFO.
* Mutual exclusion applies only within the current Python process and event loop.

<p align="center">
  <a href="index.md">&laquo; Previous: Agent Extensions</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="index.md">Next: Agent Extensions &raquo;</a>
</p>
