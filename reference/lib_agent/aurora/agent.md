# <code style="background: transparent;">Summoner<b>.aurora.agentclass</b></code> (Aurora v1.0.0)

This page documents **`SummonerAgent`**, the main Aurora client class.

Use `SummonerAgent` when you want one concrete client object that can do three Aurora-specific things on top of the core `SummonerClient` runtime:

* host a `SummonerIdentity`,
* process keyed receivers with per-key serialization and optional replay protection,
* export Aurora DNA that preserves keyed receiver behavior.

The core `SummonerClient` API for connection lifecycle, ordinary `@receive` and `@send` handlers, hooks, flow integration, reconnection, and run configuration remains documented in the [core SDK reference](../../sdk_doc/index.md). This page focuses only on what `summoner.aurora.agentclass` adds on top.

For the broader module overview, start at [<code style="background: transparent;">Summoner<b>.aurora</b></code>](../aurora.md).

## Import path

Import the module directly as:

```python
from summoner.aurora.agentclass import SummonerAgent
```

> [!NOTE]
> `SummonerAgent` is also re-exported from `summoner.aurora`. This page uses the direct module path so the reference matches the public Aurora modules.

Installation and `build.txt` setup are covered once in [Agent Extensions](../index.md).

## Typical workflow

Most applications use `SummonerAgent` in roughly this order:

1. Construct the agent.
2. Optionally attach a `SummonerIdentity` if the agent needs identity, session, or envelope features.
3. Register keyed receivers where messages for the same logical entity must not overlap.
4. Export Aurora DNA if the configured agent will later be merged or translated.

The sections below follow that same path.

## Minimal pattern

The snippet below shows the smallest useful Aurora shape before the detailed method reference begins.

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")

identity = agent.attach_identity(store_dir="./identity")
identity.id("id.json", password=b"strong-passphrase")

@agent.keyed_receive("account:update", key_by="account_id", seq_by="seq")
async def on_account_update(payload):
    return None

aurora_dna = agent.dna()
```

## `SummonerAgent.__init__`

```python
def __init__(self, name: Optional[str] = None) -> None
```

### Behavior

Constructs a `SummonerAgent` and prepares both the underlying core client state and the Aurora-specific state layered on top of it.

At a high level, construction does three things:

* creates the normal `SummonerClient` runtime,
* initializes `agent.identity` to `None`,
* prepares the keyed-receiver and DNA-export state Aurora needs later.

<details>
<summary>Internal Aurora state prepared during construction</summary>

Aurora sets up the following internal fields:

* `self._key_mutex: Optional[AsyncKeyedMutex]` starts as `None` and is created lazily when the first keyed receiver is registered.
* `self._seq_seen: dict[tuple[str, Hashable], int]` stores unbounded last-seen sequence numbers.
* `self._seq_seen_bounded: dict[str, dict[Hashable, int]]` stores bounded replay history per route when `seq_history_max_entries` is used.
* `self._seq_seen_lru: dict[str, OrderedDict[Hashable, None]]` tracks least-recently-updated keys for bounded eviction.
* `self._seq_seen_evictions: int` counts bounded replay-cache evictions.
* `self._dna_aurora_receivers: list[dict[str, Any]]` stores the Aurora-specific receiver metadata later needed for Aurora DNA export.

</details>

### Inputs

#### `name`

* **Type:** `Optional[str]`
* **Meaning:** Human-readable identifier for logs and diagnostics.
* **Default behavior:** Delegated to the base client constructor.

### Outputs

Returns a `SummonerAgent` instance.

### Example

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")
```

## `SummonerAgent.identity`

```python
identity: Optional[SummonerIdentity]
```

### Behavior

`SummonerAgent` exposes its attached identity through the `identity` attribute.

This attribute is `None` until you call `attach_identity(...)`. After attachment, it holds the exact `SummonerIdentity` instance currently hosted by the agent.

Attachment and identity-file initialization are separate steps. A newly attached identity may still need `id(...)` before session, envelope, peer-tracking, or continuity workflows are meaningful.

### Type

`Optional[SummonerIdentity]`

### Typical use

* Read `agent.identity` when you want the full identity engine after attachment.
* Call `agent.require_identity()` when the workflow should fail immediately if no identity is attached.
* Call `agent.has_identity()` when you only need to test whether one is present.

### Example

```python
identity = agent.attach_identity(store_dir="./identity")
public_id = identity.id("id.json", password=b"strong-passphrase")
```

## `SummonerAgent.identity_versions`

```python
@staticmethod
def identity_versions() -> dict[str, str]
```

### Behavior

Returns the public identity compatibility versions that `SummonerAgent` knows how to host.

This is mainly useful for diagnostics, audits, or compatibility logging. The returned dictionary tells you which public integration contract, controls API, identity-record format, envelope format, and built-in store formats are available through the current module build.

### Outputs

Returns a dictionary with the keys below:

* `integration`
* `controls`
* `id_record`
* `envelope`
* `payload_encryption`
* `history_proof`
* `sessions_store`
* `peer_keys_store`
* `replay_store`

### Example

```python
agent = SummonerAgent(name="aurora:agent")
versions = agent.identity_versions()
envelope_version = versions["envelope"]
```

## `SummonerAgent.attach_identity`

```python
def attach_identity(
    self,
    identity: Optional[SummonerIdentity] = None,
    controls: Optional[object] = None,
    **summoner_identity_kwargs: Any,
) -> SummonerIdentity
```

### Behavior

Attaches a `SummonerIdentity` to the current agent.

This is the normal way to give a `SummonerAgent` an active `SummonerIdentity`. The method supports two patterns:

1. attach an existing `SummonerIdentity` instance, or
2. construct a new `SummonerIdentity` from keyword arguments and attach it immediately.

If `controls` is provided, the method attaches those controls to the identity before storing it on `agent.identity`.

### Inputs

#### `identity`

* **Type:** `Optional[SummonerIdentity]`
* **Meaning:** Existing identity object to attach.
* **Default:** `None`

#### `controls`

* **Type:** `Optional[object]`
* **Meaning:** Optional controls object to attach before storing the identity on the agent.
* **Default:** `None`

#### `**summoner_identity_kwargs`

* **Type:** `Any`
* **Meaning:** Keyword arguments passed to `SummonerIdentity(...)` when `identity` is not supplied.
* **Validation:** If `identity` is provided, you must not also provide constructor kwargs.

### Outputs

Returns the attached `SummonerIdentity` instance.

### Error handling

* If both `identity` and `summoner_identity_kwargs` are provided, `ValueError` is raised.
* If `identity` is provided but is not a `SummonerIdentity`, `TypeError` is raised.

### Examples

#### Attach an existing identity

```python
from summoner.aurora import SummonerAgent, SummonerIdentity

agent = SummonerAgent(name="aurora:agent")
identity = SummonerIdentity(store_dir="./identity")
identity.id("id.json", password=b"strong-passphrase")

agent.attach_identity(identity)
```

#### Construct and attach in one step

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")
identity = agent.attach_identity(store_dir="./identity")
identity.id("id.json", password=b"strong-passphrase")
```

## `SummonerAgent.detach_identity`

```python
def detach_identity(self) -> Optional[SummonerIdentity]
```

### Behavior

Detaches the currently hosted identity, if any, and clears `agent.identity`.

The detached identity object itself is returned unchanged. The method does not close the identity, reset its internal stores, or remove attached controls. It only removes the host reference from the current agent.

### Outputs

Returns the detached `SummonerIdentity`, or `None` if no identity was attached.

### Example

```python
from summoner.aurora import SummonerAgent

identity = agent.detach_identity()

if identity is not None:
    other = SummonerAgent(name="aurora:other")
    other.attach_identity(identity)
```

## `SummonerAgent.require_identity`

```python
def require_identity(self) -> SummonerIdentity
```

### Behavior

Returns the currently attached identity.

Use this when the workflow requires an active identity and the absence of one should be treated as an immediate error instead of optional state.

This is an attachment check only. It does not verify that `id(...)` has already loaded or generated the local identity file.

### Outputs

Returns the current `SummonerIdentity`.

### Error handling

Raises `RuntimeError` if no identity is attached.

### Example

```python
identity = agent.require_identity()
```

## `SummonerAgent.has_identity`

```python
def has_identity(self) -> bool
```

### Behavior

Returns whether an identity is currently attached to the agent.

This is a lightweight attachment check only. It returns `True` as soon as `attach_identity(...)` stores a `SummonerIdentity` on the agent, even if `id(...)` has not been called yet.

### Outputs

Returns `True` when `agent.identity` is populated, otherwise `False`.

### Example

```python
if not agent.has_identity():
    agent.attach_identity(store_dir="./identity")
```

## `SummonerAgent.keyed_receive`

```python
def keyed_receive(
    self,
    route: str,
    key_by: Union[str, Callable[[Any], Hashable]],
    priority: Union[int, tuple[int, ...]] = (),
    seq_by: Union[None, str, Callable[[Any], int]] = None,
    seq_history_max_entries: Optional[int] = None,
)
```

### Behavior

Registers an **async receiver handler** that enforces two important guarantees for a given route/key pair:

1. **Per-key mutual exclusion** within the current Python process.
2. Optional **replay protection** based on a monotonic sequence field.

This is the Aurora feature most people reach for when one agent is responsible for many logical entities at once. It lets different keys run concurrently while still ensuring that updates for the same key do not overlap.

If `seq_by` is provided, the wrapper drops stale or duplicate messages whose sequence is less than or equal to the last sequence seen for that `(normalized_route, key)`.

<details>
<summary>Registration flow inside <code>keyed_receive(...)</code></summary>

At a high level, `keyed_receive(...)` does the following:

1. Validates that `route` is a string and strips leading/trailing whitespace.
2. Normalizes `seq_history_max_entries`.
3. Serializes the `key_by` and `seq_by` extractor specifications so Aurora can preserve keyed-receiver metadata in DNA exports.
4. Builds a key extractor from `key_by`.
5. Builds a sequence extractor from `seq_by`.
6. Validates that the decorated handler is `async`, accepts exactly one parameter, and matches the base receiver contract.
7. Normalizes `priority` into the tuple form used by the client receiver registry.
8. Captures Aurora-specific DNA metadata for the receiver.
9. Schedules the actual receiver registration.

</details>

### Mutual exclusion semantics

The list below describes what Aurora means by "keyed" in practice.

* Lock granularity is `(normalized_route, key)`.
* Different routes do not share locks, even if they compute the same key.
* The lock covers the entire handler body.

### Replay semantics

Aurora can also keep lightweight replay memory for each key when you supply `seq_by`.

* Replay protection is enabled only when `seq_by` is provided and extraction returns an integer.
* If `seq_history_max_entries` is not provided, the wrapper keeps last-seen state in `self._seq_seen` keyed by `(normalized_route, key)`.
* If `seq_history_max_entries` is provided, the wrapper stores replay state per route in `self._seq_seen_bounded` and evicts least-recently-updated keys using `self._seq_seen_lru`.
* Any message with `seq <= last_seen_seq` is dropped.
* Replay state resets on process restart and can also be cleared manually with `clear_keyed_receive_replay_state(...)`.

### Flow integration

When flow is enabled:

* the decorator attempts to parse the supplied `route`,
* if parsing succeeds, `str(parsed_route)` is used as the runtime route key,
* if parsing fails, the raw route is registered and a warning is logged.

### Error handling

Aurora is defensive by default:

* Invalid `route`, `key_by`, `seq_by`, `priority`, or `seq_history_max_entries` values raise during decoration or setup.
* Key extraction failures drop the message instead of raising into the dispatcher.
* Missing or unhashable keys drop the message.
* Sequence extraction failures disable replay checking for that message.
* Aurora awaits the wrapped handler directly and does not add an extra catch-and-log layer around exceptions from the handler body. Exception behavior otherwise follows the base client runtime.

### Inputs

#### `route`

* **Type:** `str`
* **Meaning:** Logical route string, with the same semantics as `@receive`.
* **Normalization:** Leading/trailing whitespace is stripped.
* **Flow:** If flow is enabled, route parsing may normalize the effective route key.

#### `key_by`

* **Type:** `Union[str, Callable[[Any], Hashable]]`
* **Meaning:** Extractor used to compute the per-entity key.
* **String behavior:** Dict key (if payload is a dict) or attribute name (otherwise).
* **Callable behavior:** Called as `key_by(payload)`.
* **Validation:** Keys must be hashable. Missing, invalid, or unhashable keys cause the message to be dropped.
* **Required:** If `key_by` is `None`, `ValueError` is raised.

#### `priority`

* **Type:** `Union[int, tuple[int, ...]]`
* **Meaning:** Receiver priority, identical to `@receive`.
* **Default:** `()`
* **Normalization:** If an integer is provided, it is converted to a 1-tuple `(priority,)`.

#### `seq_by`

* **Type:** `Union[None, str, Callable[[Any], int]]`
* **Meaning:** Optional monotonic sequence extractor for replay protection.
* **String behavior:** Dict key (if payload is a dict) or attribute name (otherwise).
* **Callable behavior:** Called as `seq_by(payload)`.
* **Conversion:** Best-effort `int(...)`. Failures yield `None` for that message, disabling replay checking for it.
* **State:** Stored in-memory and resets on process restart.

#### `seq_history_max_entries`

* **Type:** `Optional[int]`
* **Meaning:** Optional per-route cap for replay history when `seq_by` is enabled.
* **Default:** `None`
* **Behavior:** When omitted, replay state grows in an unbounded table keyed by `(route, key)`. When provided, Aurora keeps only the most recently updated keys for each route.
* **Validation:** Must be `None` or a positive integer. `bool` values are rejected. Providing it without `seq_by` raises `ValueError`.

### Outputs

Returns a decorator. The decorated function is registered as a receiver handler, but the internal dispatcher executes a wrapped function that applies locking and optional replay logic.

### Handler contract

The decorated handler must:

* be `async`
* accept exactly one argument (the payload)

For normal receiver code, Aurora recommends the same return shape used in the core SDK: `Optional[Event]` or `None`.

Decoration-time validation is looser than that recommendation:

* explicit `Any` return annotations are accepted,
* a missing return annotation only triggers a warning.

If the function is not async, `TypeError` is raised at decoration time.

If the function does not accept exactly one argument, `TypeError` is also raised at decoration time.

### Limitations and operational notes

* **Critical-section scope:** The lock covers the entire handler body. Keep work inside the lock short and move slow I/O out of the critical section when possible.
* **Fairness:** The underlying lock is not strictly FIFO.
* **Process scope:** Mutual exclusion is per Python process and event loop. It does not serialize work across processes or machines.
* **Unbounded replay state:** If you use `seq_by` without `seq_history_max_entries`, replay state grows with the number of distinct `(route, key)` pairs seen during the process lifetime.
* **Bounded replay state:** If you set `seq_history_max_entries`, Aurora evicts the least-recently-updated keys per route. An evicted key loses replay memory and is treated as unseen if it appears again later.

### Examples

#### Serialize per-player updates

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")

@agent.keyed_receive("game:move", key_by="player_id", priority=0)
async def on_move(payload):
    # Only one move per (route, player_id) runs at a time.
    return None
```

#### Drop replays using a monotonic sequence number

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")

@agent.keyed_receive("account:update", key_by="account_id", seq_by="seq")
async def on_account_update(payload):
    # Drops any payload with seq <= last seen for this (route, account_id).
    return None
```

#### Bound replay memory per route

```python
from summoner.aurora import SummonerAgent

agent = SummonerAgent(name="aurora:agent")

@agent.keyed_receive(
    "account:update",
    key_by="account_id",
    seq_by="seq",
    seq_history_max_entries=10_000,
)
async def on_account_update(payload):
    return None
```

#### Composite keys and derived sequences

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

## `SummonerAgent.clear_keyed_receive_replay_state`

```python
def clear_keyed_receive_replay_state(
    self,
    route: Optional[str] = None,
) -> None
```

### Behavior

Clears replay-protection state accumulated by `@keyed_receive(...)`.

* If `route` is `None`, Aurora clears all unbounded and bounded replay tables.
* If `route` is provided, Aurora strips surrounding whitespace and clears replay entries only for that normalized route.
* This is useful in test harnesses, process-local resets, or controlled operational workflows where you intentionally want to forget last-seen sequences.
* The cumulative eviction counter reported by `keyed_receive_replay_stats()` is not reset by this method.

### Inputs

#### `route`

* **Type:** `Optional[str]`
* **Meaning:** Optional route whose replay state should be cleared.
* **Default:** `None` (clear all routes)

### Outputs

Returns `None`.

### Example

```python
agent.clear_keyed_receive_replay_state("account:update")
agent.clear_keyed_receive_replay_state()
```

## `SummonerAgent.keyed_receive_replay_stats`

```python
def keyed_receive_replay_stats(self) -> dict[str, int]
```

### Behavior

Returns a lightweight summary of the replay caches currently maintained by Aurora across both unbounded and bounded modes.

This method is useful when you want to confirm that replay memory is staying within operational expectations or when you are debugging a keyed-receiver deployment.

The `routes` and `entries` counts reflect current in-memory replay state. The `evictions` value is cumulative since process start, so it can remain non-zero even after `clear_keyed_receive_replay_state(...)`.

### Outputs

Returns a dictionary with:

* `routes`: number of routes that currently have replay entries
* `entries`: total number of replay entries across all internal replay tables
* `evictions`: total number of bounded replay entries evicted since process start

### Example

```python
stats = agent.keyed_receive_replay_stats()
```

A typical result looks like `{"routes": 2, "entries": 145, "evictions": 12}`.

## `SummonerAgent.core_dna`

```python
def core_dna(
    self,
    include_context: bool = False,
    *,
    allow_lossy: bool = False,
) -> str
```

### Behavior

Exports a **core SDK DNA** JSON string.

This method is intentionally strict when Aurora keyed receivers are present:

* If the agent has no Aurora keyed receivers, `core_dna(...)` behaves like the normal core client DNA export.
* If the agent has Aurora keyed receivers and `allow_lossy=False`, Aurora raises `RuntimeError` instead of silently dropping keyed semantics.
* If the agent has Aurora keyed receivers and `allow_lossy=True`, Aurora downgrades each keyed receiver into a plain `receive` entry.

That lossy downgrade preserves the handler source metadata and route/priority information, but it does **not** preserve:

* per-key mutual exclusion,
* replay filtering via `seq_by`,
* bounded replay-table settings such as `seq_history_max_entries`.

Use this method only when the tool reading the DNA expects core DNA or when you intentionally want Aurora behavior stripped away.

### Inputs

#### `include_context`

* **Type:** `bool`
* **Meaning:** Whether to include context entries in the exported DNA.
* **Default:** `False`

#### `allow_lossy`

* **Type:** `bool`
* **Meaning:** Whether Aurora may downgrade keyed receivers into plain `receive` entries when exporting core DNA.
* **Default:** `False`

### Outputs

Returns a JSON string representing core DNA.

### Error handling

* If keyed receivers exist and `allow_lossy=False`, `RuntimeError` is raised.

## `SummonerAgent.aurora_dna`

```python
def aurora_dna(self, include_context: bool = False) -> str
```

### Behavior

Exports an **Aurora DNA** JSON string that preserves Aurora keyed-receiver behavior.

For each keyed receiver, Aurora writes an `aurora:keyed_receive` entry containing:

* the route and priority,
* serialized `key_by` and `seq_by` extractor specifications,
* optional `seq_history_max_entries`,
* handler source metadata used for replay.

Use this method when the DNA may later be replayed by Aurora-aware tools such as [Agent Merger and Translation](merger.md), or whenever keyed receiver semantics must survive export/import intact.

### Inputs

#### `include_context`

* **Type:** `bool`
* **Meaning:** Whether to include context entries in the exported DNA.
* **Default:** `False`

### Outputs

Returns a JSON string representing Aurora DNA.

## `SummonerAgent.dna`

```python
def dna(
    self,
    include_context: bool = False,
    *,
    flavor: str = "aurora",
    allow_lossy: bool = False,
) -> str
```

### Behavior

Aurora overrides the base `dna(...)` method with a `flavor` parameter.

* `flavor="aurora"` calls `aurora_dna(...)`.
* `flavor="core"` calls `core_dna(..., allow_lossy=allow_lossy)`.

The most important public behavior change is that Aurora defaults to `flavor="aurora"`, so plain `agent.dna()` exports Aurora DNA rather than core DNA.

### Choosing the right DNA flavor

* Use `agent.dna()` or `agent.aurora_dna()` when keyed receiver semantics must survive export/import.
* Use `agent.core_dna(..., allow_lossy=True)` only when a downstream consumer expects core DNA and you accept the loss of keyed locking and replay semantics.
* If you plan to use [Agent Merger and Translation](merger.md), prefer Aurora DNA.

### Inputs

#### `include_context`

* **Type:** `bool`
* **Meaning:** Whether to include context entries in the exported DNA.
* **Default:** `False`

#### `flavor`

* **Type:** `str`
* **Meaning:** Export flavor selector.
* **Allowed values:** `"aurora"` or `"core"`
* **Default:** `"aurora"`

#### `allow_lossy`

* **Type:** `bool`
* **Meaning:** Passed through to `core_dna(...)` when `flavor="core"`.
* **Default:** `False`

### Outputs

Returns a JSON string representing the selected DNA flavor.

### Error handling

* Unknown `flavor` values raise `ValueError`.
* `flavor="core"` may still raise `RuntimeError` if Aurora keyed receivers exist and `allow_lossy=False`.

<p align="center">
  <a href="../aurora.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.aurora</b></code></a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="merger.md">Next: <code style="background: transparent;">Summoner<b>.aurora.agentmerger</b></code> &raquo;</a>
</p>
