# `SummonerIdentity` (<code style="background: transparent;">Summoner<b>.aurora.identity</b></code>) 

This page documents **`SummonerIdentity`**, the main identity engine exposed from this module.

If you want one class to start with in this identity API, start here. `SummonerIdentity` is responsible for:

* loading or creating the local identity file,
* tracking session continuity and replay state,
* sealing and opening signed envelopes,
* maintaining the built-in local peer and session stores,
* exposing hook-aware runtime methods for custom storage or trust policy.

Most applications touch this class directly even when the active identity is later attached to a host such as `SummonerAgent`.

## Import path

```python
from summoner.aurora import SummonerIdentity
```

## Public attributes

After `id(...)` is called, these are the main public attributes application code usually reads.

The table below is meant as a quick orientation guide, not as a replacement for the method docs that follow.

| Attribute | Meaning |
| --- | --- |
| `ttl` | Default TTL in seconds used when creating sessions. |
| `margin` | Safety buffer used during expiry checks. |
| `enforce_created_at` | If `True`, rejects session timestamps earlier than sender `created_at`. |
| `max_clock_skew_seconds` | Optional future-skew limit for inbound session timestamps. |
| `store_dir` | Optional override for the built-in local JSON store directory. |
| `persist_local` | Whether built-in local session and peer-key stores are written to disk. |
| `load_local` | Whether built-in local stores are loaded from disk inside `id(...)`. |
| `persist_replay` | Whether replay state is persisted to `replay.json` instead of memory-only. |
| `public_id` | The signed public identity record, or `None` until `id(...)` is called. |
| `controls` | The attached controls object, if any. |
| `last_status` | The last structured lifecycle status emitted by the identity runtime. |

### Lifecycle return pattern

`id(...)` and `update_id_meta(...)` are synchronous methods.

Most session and envelope lifecycle methods are async. By default they return the requested data on success and `None` on failure. If `return_status=True`, they instead return a structured status object:

```python
{
    "ok": bool,
    "code": str,
    "phase": str,
    "data": ...,
}
```

That same object is also reflected in `last_status`.

## `SummonerIdentity.store_versions`

```python
@staticmethod
def store_versions() -> dict[str, str]
```

### Behavior

Returns the current versions of the built-in local store formats for:

* `sessions`
* `peer_keys`
* `replay`

Use this when you want a small runtime compatibility report without importing each constant individually from `summoner.aurora.identity`.

### Outputs

Returns a dictionary with:

* `sessions`
* `peer_keys`
* `replay`

### Example

```python
versions = SummonerIdentity.store_versions()
replay_store_version = versions["replay"]
```

## `SummonerIdentity.controls_version`

```python
@staticmethod
def controls_version() -> str
```

### Behavior

Returns the public controls API version used by `SummonerIdentityControls`.

This is mainly useful for diagnostics, audits, or compatibility assertions.

### Outputs

Returns the current public controls API version string.

### Example

```python
controls_version = SummonerIdentity.controls_version()
```

## `SummonerIdentity.__init__`

```python
def __init__(
    self,
    ttl: int = 86400,
    margin: int = 0,
    *,
    enforce_created_at: bool = False,
    max_clock_skew_seconds: Optional[int] = None,
    store_dir: Optional[str] = None,
    persist_local: bool = True,
    load_local: bool = True,
    persist_replay: bool = False,
)
```

### Behavior

Constructs the identity engine and configures its continuity and persistence policy.

This constructor does **not** load keys or create files. Call `id(...)` to load or create the actual identity.

### Inputs

#### `ttl`

* **Type:** `int`
* **Meaning:** Default session TTL in seconds used when creating sessions.
* **Default:** `86400`

#### `margin`

* **Type:** `int`
* **Meaning:** Safety buffer in seconds used during expiry checks.
* **Default:** `0`

#### `enforce_created_at`

* **Type:** `bool`
* **Meaning:** Whether inbound session timestamps earlier than the sender identity's `created_at` should be rejected.
* **Default:** `False`

#### `max_clock_skew_seconds`

* **Type:** `Optional[int]`
* **Meaning:** Optional future-skew limit for inbound session timestamps.
* **Default:** `None`

#### `store_dir`

* **Type:** `Optional[str]`
* **Meaning:** Optional override for the built-in local JSON store directory.
* **Resolution:** If relative, `id(...)` resolves it later using the same caller-relative path model used for `path`.
* **Default:** `None`

#### `persist_local`

* **Type:** `bool`
* **Meaning:** Whether the built-in local session and peer-key stores should be written to disk.
* **Default:** `True`

#### `load_local`

* **Type:** `bool`
* **Meaning:** Whether built-in local stores should be loaded from disk inside `id(...)`.
* **Default:** `True`

#### `persist_replay`

* **Type:** `bool`
* **Meaning:** Whether replay state should be persisted to `replay.json` instead of remaining memory-only.
* **Default:** `False`

### Outputs

Returns a `SummonerIdentity` instance.

At construction time, no identity file is loaded, no keys are generated, and `public_id` remains `None` until `id(...)` is called.

### Example

```python
identity = SummonerIdentity(
    ttl=86400,
    margin=5,
    store_dir="./identity",
    persist_replay=True,
)
```

## `SummonerIdentity.id`

```python
def id(
    self,
    path: str = "id.json",
    meta: Optional[Any] = None,
    *,
    password: Optional[bytes] = None,
) -> dict
```

### Behavior

Loads or creates an identity file at `path`.

If the file already exists, `id(...)` loads it and validates the signed public record. If it does not exist, `id(...)` generates a new X25519 keypair, a new Ed25519 keypair, and writes the new identity file.

If `meta` is provided and differs from the stored metadata, `id(...)` re-signs the public identity record and persists the updated file.

`id(...)` also initializes the built-in local store paths for:

* `sessions.json`
* `peer_keys.json`
* `replay.json`

If `load_local=True`, those stores are loaded at the same time.

### Path behavior

If `path` is relative, it is resolved relative to the caller file directory.

### Inputs

#### `path`

* **Type:** `str`
* **Meaning:** Identity-file path to load or create.
* **Default:** `"id.json"`

#### `meta`

* **Type:** `Optional[Any]`
* **Meaning:** Optional metadata to store in the signed public identity record.
* **Behavior:** If the file already exists and the stored metadata differs, the method re-signs and rewrites the public record.

#### `password`

* **Type:** `Optional[bytes]`
* **Meaning:** Optional password used to decrypt or encrypt the private section of the identity file.
* **Default:** `None`

### Outputs

Returns the signed public identity record and stores it on `self.public_id`.

The method also prepares the built-in local store paths and, when configured, loads the fallback JSON stores into memory.

### Error handling

Raises if the existing identity file is malformed, uses an unsupported format, or requires a password that is missing or incorrect.

### Example

```python
identity = SummonerIdentity(store_dir="./identity")
public_id = identity.id("id.json", password=b"strong-passphrase")
```

For metadata semantics, see [Metadata and Continuity](metadata.md).

## `SummonerIdentity.update_id_meta`

```python
def update_id_meta(
    self,
    meta: Optional[Any],
    *,
    password: Optional[bytes] = None,
) -> dict
```

### Behavior

Updates the persisted `meta` field of the current identity, re-signs the public record, and writes the updated identity file to disk.

This is the public method that commits metadata changes to the existing identity file. If the identity file is password-protected, a password is required before the method will rewrite it.

### Inputs

#### `meta`

* **Type:** `Optional[Any]`
* **Meaning:** Replacement metadata payload for the signed public identity record.

#### `password`

* **Type:** `Optional[bytes]`
* **Meaning:** Optional password used when rewriting an encrypted identity file.
* **Default:** `None`

### Outputs

Returns the updated signed public identity record.

It also updates `self.public_id`, `self._id_meta`, and the remembered password when one is provided.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* Raises `ValueError` if the identity path is unknown.
* Raises `ValueError` if the identity file is encrypted and no password is available.

### Example

```python
updated_public_id = identity.update_id_meta(
    {"tenant_id": "contoso-eu-prod"},
    password=b"strong-passphrase",
)
```

### Important note

Changing `meta` changes the signed public record, but it does not change the underlying cryptographic principal as long as the same keys remain in use. For the continuity implications, see [Metadata and Continuity](metadata.md).

## `SummonerIdentity.on_policy_event`

```python
def on_policy_event(
    self,
    phase: str,
) -> Callable[[Callable[[str, dict], Any]], Callable[[str, dict], Any]]
```

### Behavior

Registers a per-instance telemetry handler for one lifecycle phase.

Handlers may be synchronous or async. The runtime catches and logs handler failures so telemetry does not break the protocol path itself.

For the allowed phases, event schema, validation-stage model, and operational guidance, see [Policy Events](policy_events.md).

### Inputs

#### `phase`

* **Type:** `str`
* **Meaning:** Lifecycle phase to observe.
* **Allowed values:** `start_session`, `continue_session`, `advance_stream_session`, `seal_envelope`, `open_envelope`, `verify_discovery_envelope`

### Outputs

Returns a decorator that registers one handler for the chosen phase and then returns that same handler unchanged.

### Error handling

Raises `ValueError` if `phase` is not one of the allowed lifecycle phases.

### Example

```python
@identity.on_policy_event("open_envelope")
def on_open(event_name, context):
    if event_name != "ok":
        print(context.get("validation_stage"))
```

## `SummonerIdentity.attach_controls`

```python
def attach_controls(self, controls: Optional[Any] = None) -> Any
```

### Behavior

Attaches a per-identity controls object.

If `controls is None`, the method creates a new `SummonerIdentityControls()` instance and attaches it immediately.

Attached controls customize storage or trust behavior for this one identity instance. They do not change the identity keys or the cryptographic principal itself.

### Notes

* The same controls object may be reused across multiple identities.
* If the controls object carries mutable state, that state is shared across those identities.
* Controls callbacks receive the owning `SummonerIdentity` as their first argument.
* If another controls object is already attached, the new one replaces it.
* The identity runtime treats session registration and session verification as one policy decision. If you override `register_session` in a given hook scope, you must also override `verify_session` in that same scope. Mixed-scope register/verify combinations raise `ValueError` when runtime methods enter the session pipeline.

See [`SummonerIdentityControls`](controls.md) for the reusable controls API.

### Inputs

#### `controls`

* **Type:** `Optional[Any]`
* **Meaning:** Controls object to attach.
* **Default behavior:** When omitted, the method creates and attaches a new `SummonerIdentityControls()` instance.

### Outputs

Returns the attached controls object.

### Error handling

Raises `TypeError` if the provided object exposes one of the recognized hook names but that attribute is not callable.

### Examples

#### Attach default controls

```python
controls = identity.attach_controls()
```

#### Attach an existing controls object

```python
controls = SummonerIdentityControls()
identity.attach_controls(controls)
```

## `SummonerIdentity.detach_controls`

```python
def detach_controls(self) -> Optional[Any]
```

### Behavior

Detaches and returns the currently attached controls object, or `None` if no controls are attached.

This does not remove class-level hooks and does not clear instance-local hooks.

### Outputs

Returns the detached controls object, or `None` when no controls were attached.

### Example

```python
controls = identity.detach_controls()
```

## `SummonerIdentity.require_controls`

```python
def require_controls(self) -> Any
```

### Behavior

Returns the attached controls object.

Raises `RuntimeError` if no controls are attached. Use this when controls attachment is a programming invariant rather than optional state.

### Outputs

Returns the attached controls object.

### Error handling

Raises `RuntimeError` if no controls are attached.

### Example

```python
controls = identity.require_controls()
```

## `SummonerIdentity.has_controls`

```python
def has_controls(self) -> bool
```

### Behavior

Returns `True` when a controls object is currently attached.

### Outputs

Returns `True` when controls are attached, otherwise `False`.

### Example

```python
if not identity.has_controls():
    identity.attach_controls()
```

## `SummonerIdentity.clear_local_hooks`

```python
def clear_local_hooks(self) -> None
```

### Behavior

Clears all instance-local hooks registered with `@identity.on_*`.

This does not detach the controls object and does not affect class-level hooks.

### Hook precedence

The runtime resolves hook behavior in this order:

1. instance-local `@identity.on_*`
2. attached controls object
3. class-level `@SummonerIdentity.*`
4. built-in local logic

Outside hook definitions, use the hook-aware runtime methods:

* `await identity.get_current_session(...)`
* `await identity.verify_session_record(...)`
* `await identity.register_session_record(...)`
* `await identity.force_reset_session(...)`

### Outputs

Returns `None`.

### Example

```python
identity.clear_local_hooks()
```

## `SummonerIdentity.on_register_session` and related instance hook decorators

These instance methods register callbacks on one live `SummonerIdentity` object.

Use them when one identity instance needs a narrow override that should not affect other identities in the same process. These decorators are strongest in hook precedence because they sit directly on the active object.

### Available decorators

| Method | Expected callback shape | Typical use |
| --- | --- | --- |
| `identity.on_register_session(fn)` | `fn(peer_public_id, local_role, session_record, new=False, use_margin=False)` | Override session persistence for one live identity object. |
| `identity.on_reset_session(fn)` | `fn(peer_public_id, local_role)` | Override force-reset handling for one live identity object. |
| `identity.on_verify_session(fn)` | `fn(peer_public_id, local_role, session_record, use_margin=False)` | Override continuity verification for one live identity object. |
| `identity.on_get_session(fn)` | `fn(peer_public_id, local_role)` | Override current-link lookup for one live identity object. |
| `identity.on_peer_key_store(fn)` | `fn(peer_public_id, update=None)` | Override peer-key lookup and update behavior for one live identity object. |
| `identity.on_replay_store(fn)` | `fn(message_id, ttl, now, add)` | Override replay detection and replay writes for one live identity object. |

### Behavior

Each method stores one callback on the identity object and returns that same callback unchanged, which is why the API works as a decorator.

Runtime code does not call these registration methods to perform the work. Instead, methods such as `get_current_session(...)`, `start_session(...)`, `continue_session(...)`, `seal_envelope(...)`, and `open_envelope(...)` resolve the active hook path automatically.

### Inputs

#### `fn`

* **Type:** `Callable[..., Any]`
* **Meaning:** Hook callback to register on this live identity object.

### Outputs

Returns the same callback after storing it on the identity object.

### Error handling

Raises `TypeError` if `fn` is not callable.

Important coupling rule:

* If you register `on_register_session`, also register `on_verify_session` in the same instance-local scope.
* The runtime rejects mixed-scope register/verify combinations because write policy and verification policy must stay aligned.

### Example

```python
@identity.on_get_session
def get_session(peer_public_id, local_role):
    return identity.get_session_default(peer_public_id, local_role)
```

## `SummonerIdentity.register_session` and related class hook decorators

These class methods register process-wide hooks on `SummonerIdentity`.

Use them when one rule should apply to every `SummonerIdentity` object in the current Python process unless a narrower scope overrides it.

### Available decorators

| Method | Expected callback shape | Typical use |
| --- | --- | --- |
| `@SummonerIdentity.register_session` | `fn(peer_public_id, local_role, session_record, new=False, use_margin=False)` | Install one process-wide session persistence rule. |
| `@SummonerIdentity.reset_session` | `fn(peer_public_id, local_role)` | Install one process-wide reset policy. |
| `@SummonerIdentity.verify_session` | `fn(peer_public_id, local_role, session_record, use_margin=False)` | Install one process-wide continuity verification rule. |
| `@SummonerIdentity.get_session` | `fn(peer_public_id, local_role)` | Install one process-wide current-link lookup rule. |
| `@SummonerIdentity.peer_key_store` | `fn(peer_public_id, update=None)` | Install one process-wide peer-key lookup and update rule. |
| `@SummonerIdentity.replay_store` | `fn(message_id, ttl, now, add)` | Install one process-wide replay-store rule. |

### Behavior

Each class decorator stores one callback on the `SummonerIdentity` class and returns that same callback unchanged.

These decorators are lower precedence than instance-local hooks and attached `SummonerIdentityControls`, but higher precedence than the built-in local JSON and in-memory fallback logic.

### Inputs

#### `fn`

* **Type:** `Callable[..., Any]`
* **Meaning:** Hook callback to register at process scope on `SummonerIdentity`.

### Outputs

Returns the same callback after storing it on the class.

### Error handling

Raises `TypeError` if `fn` is not callable.

Important coupling rule:

* If you register `@SummonerIdentity.register_session`, also register `@SummonerIdentity.verify_session` at class scope.
* The runtime rejects mixed-scope register/verify combinations because write policy and verification policy must stay aligned.

### Example

```python
@SummonerIdentity.verify_session
def verify_session(peer_public_id, local_role, session_record, use_margin=False):
    return {"ok": True, "code": "ok"}
```

## Default delegate helpers for hook authors

`SummonerIdentity` exposes public default delegate methods for advanced hook authors.

These helpers:

* call the built-in local logic directly,
* bypass hook resolution on purpose,
* are synchronous helper methods even when the surrounding runtime APIs are async.

Use them inside custom hooks when you want the default behavior without re-entering the same hook path recursively.

Important coupling rule:

* If you provide custom `register_session` behavior, also provide `verify_session` behavior in the same hook scope.
* The relevant scopes are instance-local `@identity.on_*`, attached `SummonerIdentityControls`, and class-level `@SummonerIdentity.*`.
* The runtime rejects mixed-scope register/verify setups because write policy and verify policy must remain aligned.

### Available default delegates

The table below summarizes the helper methods you can call from inside custom hooks.

| Method | Purpose |
| --- | --- |
| `get_session_default(peer_public_id, local_role)` | Read the current link from the built-in local session store. |
| `verify_session_default(peer_public_id, local_role, session_record, use_margin=False)` | Run the built-in session verification and return the normalized verify result. |
| `register_session_default(peer_public_id, local_role, session_record, new=False, use_margin=False)` | Persist or clear current-link state through the built-in local session-register logic. |
| `reset_session_default(peer_public_id, local_role)` | Force-reset one session lane through the built-in local reset logic. |
| `peer_key_store_default(peer_public_id, update=None)` | Read or update the built-in local peer-key cache. |
| `replay_store_default(message_id, ttl=..., now=None, add=False)` | Query or write the built-in local replay store. |

## `SummonerIdentity.classify_session_record`

```python
def classify_session_record(self, session_record: Any) -> dict[str, Any]
```

### Behavior

Classifies a session-like object without mutating state.

This helper is useful in policy handlers, diagnostics, and stream-aware application logic that needs a fast answer about whether a record looks like a start-form session, a stream chunk, an expired frame, and so on.

### Returned field groups

The returned dictionary includes:

* shape and mode fields such as `valid_shape`, `mode`, `is_stream`, and `stream_fields_valid`
* stream identity fields such as `stream_id`, `stream_seq`, and `stream_phase`
* start/end interpretation such as `is_start_form`, `is_stream_start`, and `is_stream_end`
* TTL and expiry fields such as `ttl_valid`, `stream_ttl_valid`, `record_expired`, and `record_expiry_basis`

For stream-specific rules, see [Streaming](streaming.md).

### Inputs

#### `session_record`

* **Type:** `Any`
* **Meaning:** Candidate session-like object to classify.

### Outputs

Returns a dictionary containing shape, mode, stream, and expiry hints. Invalid inputs produce the same output shape with conservative falsey values.

### Example

```python
info = identity.classify_session_record(session_record)
if info["is_stream"] and info["record_expired"]:
    print("stream frame is stale")
```

## `SummonerIdentity.get_current_session`

```python
async def get_current_session(
    self,
    peer_public_id: Optional[dict],
    local_role: int,
) -> Optional[dict]
```

### Behavior

Returns the current stored link for the `(peer_public_id, local_role)` lane through the active hook path.

Use this in application code when you want `SummonerIdentity` to honor instance-local hooks, attached controls, class hooks, and its built-in local storage in the normal precedence order.

### Inputs

#### `peer_public_id`

* **Type:** `Optional[dict]`
* **Meaning:** Peer public identity for the continuity lane, or `None` for the generic public/discovery lane.

#### `local_role`

* **Type:** `int`
* **Meaning:** Local role lane to read, usually `0` or `1`.

### Outputs

Returns the current session link for that lane, or `None` if no current link exists.

## `SummonerIdentity.verify_session_record`

```python
async def verify_session_record(
    self,
    peer_public_id: Optional[dict],
    local_role: int,
    session_record: dict,
    *,
    use_margin: bool = False,
) -> dict
```

### Behavior

Verifies a session record through the active verification path and returns the normalized verification result.

This is the hook-aware runtime entry point corresponding to `@SummonerIdentity.verify_session`.

### Inputs

#### `peer_public_id`

* **Type:** `Optional[dict]`
* **Meaning:** Peer public identity for the lane being verified, or `None` for the generic public/discovery lane.

#### `local_role`

* **Type:** `int`
* **Meaning:** Local role lane that should accept or reject the record.

#### `session_record`

* **Type:** `dict`
* **Meaning:** Session proof candidate to verify.

#### `use_margin`

* **Type:** `bool`
* **Meaning:** Whether expiry checks should use the configured margin.
* **Default:** `False`

### Outputs

Returns the normalized verification result, typically a dictionary containing `ok`, `code`, and optionally `reason`.

## `SummonerIdentity.register_session_record`

```python
async def register_session_record(
    self,
    peer_public_id: Optional[dict],
    local_role: int,
    session_record: Optional[dict],
    *,
    new: bool = False,
    use_margin: bool = False,
) -> bool
```

### Behavior

Persists a session record through the active registration path.

This is the hook-aware runtime entry point corresponding to `@SummonerIdentity.register_session`.

### Inputs

#### `peer_public_id`

* **Type:** `Optional[dict]`
* **Meaning:** Peer public identity for the lane being updated, or `None` for the generic public/discovery lane.

#### `local_role`

* **Type:** `int`
* **Meaning:** Local role lane to update.

#### `session_record`

* **Type:** `Optional[dict]`
* **Meaning:** Session record to persist, or `None` to clear the current lane.

#### `new`

* **Type:** `bool`
* **Meaning:** Whether the registration should be treated as a new current-link transition.
* **Default:** `False`

#### `use_margin`

* **Type:** `bool`
* **Meaning:** Whether expiry-sensitive registration logic should use the configured margin.
* **Default:** `False`

### Outputs

Returns `True` when the session path accepts the write, otherwise `False`.

## `SummonerIdentity.force_reset_session`

```python
async def force_reset_session(
    self,
    peer_public_id: Optional[dict],
    local_role: int,
) -> bool
```

### Behavior

Force-resets a session lane through the active reset path.

This is the hook-aware runtime entry point corresponding to `@SummonerIdentity.reset_session`.

### Inputs

#### `peer_public_id`

* **Type:** `Optional[dict]`
* **Meaning:** Peer public identity for the lane to reset, or `None` for the generic public/discovery lane.

#### `local_role`

* **Type:** `int`
* **Meaning:** Local role lane to reset.

### Outputs

Returns `True` when the reset path accepts the reset, otherwise `False`.

## `SummonerIdentity.start_session`

```python
async def start_session(
    self,
    peer_public_id: Optional[dict] = None,
    ttl: Optional[int] = None,
    stream: bool = False,
    stream_ttl: Optional[int] = None,
    *,
    force_reset: bool = False,
    return_status: bool = False,
) -> Any
```

### Behavior

Creates a start-form session proof, always with `sender_role = 0`, and persists it.

If `peer_public_id` is provided, the method may include an encrypted `history_proof` so the peer can validate continuity against earlier history.

### Important behavior

* The method allows only one active role-0 lane per peer.
* `force_reset=True` clears the active lane when policy allows a reset.
* `stream=True` creates a stream start and requires both a peer identity and a positive `stream_ttl`.

For the full stream-mode contract, see [Streaming](streaming.md).

### Inputs

#### `peer_public_id`

* **Type:** `Optional[dict]`
* **Meaning:** Peer public identity for the new lane, or `None` for a generic public/discovery start.
* **Default:** `None`

#### `ttl`

* **Type:** `Optional[int]`
* **Meaning:** Session TTL override for the created start-form proof.
* **Default:** `None` (use `self.ttl`)

#### `stream`

* **Type:** `bool`
* **Meaning:** Whether to create a stream-start proof instead of a single-message proof.
* **Default:** `False`

#### `stream_ttl`

* **Type:** `Optional[int]`
* **Meaning:** Required non-end timeout for stream mode.
* **Default:** `None`

#### `force_reset`

* **Type:** `bool`
* **Meaning:** Whether a live incomplete role-0 lane may be force-cleared before starting a new session.
* **Default:** `False`

#### `return_status`

* **Type:** `bool`
* **Meaning:** Whether to return the structured lifecycle status instead of the session record.
* **Default:** `False`

### Outputs

* Default return: the created session record on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* Raises `ValueError` if a custom `register_session` hook is active without a matching custom `verify_session` hook in the same hook scope.
* Raises if `peer_public_id` is provided but is not a valid signed public identity.

## `SummonerIdentity.continue_session`

```python
async def continue_session(
    self,
    peer_public_id: Optional[dict],
    peer_session: dict,
    ttl: Optional[int] = None,
    use_margin: bool = True,
    *,
    stream: bool = False,
    stream_ttl: Optional[int] = None,
    return_status: bool = False,
) -> Any
```

### Behavior

Builds the next session proof for replying to a peer session proof.

The method derives the local role from the peer record, checks the current stored lane, validates that the incoming session matches the expected current link, and persists the reply proof.

### Important behavior

* If the current link is missing or stale, role `0` may restart through `start_session(...)`.
* Role `1` fails closed rather than silently restarting as role `0`.
* `stream=True` starts a responder-owned stream turn.
* `peer_public_id=None` uses the generic public/discovery lane rather than a durable per-peer continuity lane.

For the stream-specific contract, see [Streaming](streaming.md).

### Inputs

#### `peer_public_id`

* **Type:** `Optional[dict]`
* **Meaning:** Peer public identity for the continuity lane, or `None` for the generic public/discovery lane.

#### `peer_session`

* **Type:** `dict`
* **Meaning:** Peer session proof being answered.

#### `ttl`

* **Type:** `Optional[int]`
* **Meaning:** Session TTL override for the reply proof.
* **Default:** `None` (use `self.ttl`)

#### `use_margin`

* **Type:** `bool`
* **Meaning:** Whether expiry checks should use the configured margin while evaluating the current lane.
* **Default:** `True`

#### `stream`

* **Type:** `bool`
* **Meaning:** Whether to begin a responder-owned stream turn.
* **Default:** `False`

#### `stream_ttl`

* **Type:** `Optional[int]`
* **Meaning:** Required non-end timeout for stream mode.
* **Default:** `None`

#### `return_status`

* **Type:** `bool`
* **Meaning:** Whether to return the structured lifecycle status instead of the next session record.
* **Default:** `False`

### Outputs

* Default return: the next session record on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* Raises `ValueError` if a custom `register_session` hook is active without a matching custom `verify_session` hook in the same hook scope.
* Raises if `peer_public_id` is provided but is not a valid signed public identity.

## `SummonerIdentity.advance_stream_session`

```python
async def advance_stream_session(
    self,
    peer_public_id: Optional[dict],
    session: dict,
    *,
    end_stream: bool = False,
    ttl: Optional[int] = None,
    stream_ttl: Optional[int] = None,
    return_status: bool = False,
) -> Any
```

### Behavior

Advances an active stream for the same sender role.

The method requires a valid active stream, enforces contiguous sequence progression, and increments the stream sequence by exactly one step.

### Important behavior

* `peer_public_id` is required.
* `end_stream=False` requires a positive `stream_ttl`.
* `end_stream=True` closes the stream and returns to normal session TTL handling.

For the complete stream state machine, see [Streaming](streaming.md).

### Inputs

#### `peer_public_id`

* **Type:** `Optional[dict]`
* **Meaning:** Peer public identity for the active stream lane.

#### `session`

* **Type:** `dict`
* **Meaning:** Current stream-mode session record being advanced.

#### `end_stream`

* **Type:** `bool`
* **Meaning:** Whether the next frame should close the stream.
* **Default:** `False`

#### `ttl`

* **Type:** `Optional[int]`
* **Meaning:** Normal handoff TTL used for the end frame.
* **Default:** `None` (use `self.ttl` when closing)

#### `stream_ttl`

* **Type:** `Optional[int]`
* **Meaning:** Required timeout for non-end stream frames.
* **Default:** `None`

#### `return_status`

* **Type:** `bool`
* **Meaning:** Whether to return the structured lifecycle status instead of the next session record.
* **Default:** `False`

### Outputs

* Default return: the next stream session record on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* Raises if `peer_public_id` is provided but is not a valid signed public identity.

## `SummonerIdentity.seal_envelope`

```python
async def seal_envelope(
    self,
    payload: Optional[Any],
    session: dict,
    to: Optional[dict] = None,
    *,
    id_meta: Optional[Any] = None,
    return_status: bool = False,
) -> Any
```

### Behavior

Builds a signed envelope.

If `to` is provided, the method derives a symmetric key for that peer and encrypts the payload before signing the envelope. If `to is None`, the payload remains plaintext but is still covered by the envelope signature.

The method also verifies that the provided session proof matches the currently stored current link before sending.

### Important behavior

* `id_meta` updates the in-memory public identity used by the current process, but it does not persist to disk.
* Stream mode requires a peer identity and valid stream fields.
* Public discovery envelopes (`to=None`) are for discovery/broadcast semantics, not durable peer continuity.

For metadata behavior, see [Metadata and Continuity](metadata.md). For security notes, see [Security Notes](security.md).

### Inputs

#### `payload`

* **Type:** `Optional[Any]`
* **Meaning:** JSON-serializable payload to sign and optionally encrypt.

#### `session`

* **Type:** `dict`
* **Meaning:** Current session proof to embed in the envelope.

#### `to`

* **Type:** `Optional[dict]`
* **Meaning:** Recipient public identity for encrypted delivery, or `None` for plaintext discovery/broadcast semantics.
* **Default:** `None`

#### `id_meta`

* **Type:** `Optional[Any]`
* **Meaning:** Optional in-memory metadata override for the sender identity used in this process.
* **Default:** `None`

#### `return_status`

* **Type:** `bool`
* **Meaning:** Whether to return the structured lifecycle status instead of the envelope.
* **Default:** `False`

### Outputs

* Default return: the signed envelope on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* Raises `ValueError` if `payload` is not JSON-serializable.
* Raises `ValueError` if a custom `register_session` hook is active without a matching custom `verify_session` hook in the same hook scope.
* Raises if `to` is provided but is not a valid signed public identity.

## `SummonerIdentity.open_envelope`

```python
async def open_envelope(
    self,
    envelope: dict,
    *,
    return_status: bool = False,
) -> Any
```

### Behavior

Verifies and opens an inbound envelope.

The method validates the sender identity, verifies the envelope signature, checks session continuity, decrypts the payload when necessary, applies replay protection, commits accepted continuity state, and marks the peer as verified for session use.

### Important behavior

* If `to` is present, it must match the local identity.
* If replay or continuity verification fails, the envelope is rejected.
* Successful `open_envelope(...)` can promote a peer into the verified-peer set.
* Policy events for `open_envelope` carry high-signal context such as validation stage and replay mode.

For policy telemetry, see [Policy Events](policy_events.md). For security posture and operational assumptions, see [Security Notes](security.md).

### Inputs

#### `envelope`

* **Type:** `dict`
* **Meaning:** Envelope candidate to verify, decrypt when needed, and commit into continuity state.

#### `return_status`

* **Type:** `bool`
* **Meaning:** Whether to return the structured lifecycle status instead of the opened payload.
* **Default:** `False`

### Outputs

* Default return: the opened payload on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* Raises `ValueError` if a custom `register_session` hook is active without a matching custom `verify_session` hook in the same hook scope.
* Most envelope-validation failures return `None` or a structured status object rather than raising directly.

## `SummonerIdentity.verify_discovery_envelope`

```python
async def verify_discovery_envelope(
    self,
    envelope: dict,
    *,
    return_status: bool = False,
) -> Any
```

### Behavior

Verifies a discovery/public envelope without committing session continuity state.

This method is for public discovery ingress only. It requires:

* `to=None`
* a role-0 start-form session proof
* non-stream semantics

It still verifies the sender identity, verifies the envelope signature, updates peer knowledge, and applies replay protection.

### Important behavior

This helper does **not** call session verification or session registration hooks. It is narrower than `open_envelope(...)` and is meant for discovery paths, not normal peer continuity.

### Inputs

#### `envelope`

* **Type:** `dict`
* **Meaning:** Discovery/public envelope candidate to verify without continuity commit.

#### `return_status`

* **Type:** `bool`
* **Meaning:** Whether to return the structured lifecycle status instead of the opened payload.
* **Default:** `False`

### Outputs

* Default return: the opened payload on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* Most discovery-validation failures return `None` or a structured status object rather than raising directly.

## `SummonerIdentity.list_known_peers`

```python
def list_known_peers(self) -> list[dict]
```

### Behavior

Returns peer public identities from the local peer-key cache.

This is a discovery-oriented view, not a trust boundary. A peer can appear here simply because the runtime learned its self-signed public identity.

With custom peer-key controls, this built-in local view may be incomplete unless your application keeps the built-in cache synchronized.

### Outputs

Returns a list of known peer public identity records.

### Example

```python
for public_id in identity.list_known_peers():
    print(public_id.get("meta"))
```

## `SummonerIdentity.list_verified_peers`

```python
def list_verified_peers(self) -> list[dict]
```

### Behavior

Returns the peers that the built-in verification logic currently treats as verified conversation peers.

This is stricter than `list_known_peers()`. The runtime promotes peers here only after explicit verification signals such as successful session-based opening or discovery verification.

With custom peer-key or session controls, this built-in local view may be incomplete unless your application mirrors those trust signals.

### Outputs

Returns a list of peer public identity records currently treated as verified conversation peers.

### Example

```python
for public_id in identity.list_verified_peers():
    print(public_id.get("pub_sig_b64"))
```

## `SummonerIdentity.find_peer`

```python
def find_peer(self, text: str) -> list[dict]
```

### Behavior

Convenience search over `list_known_peers()` using substring matching on `str(public_id)`.

This is a UX helper, not a trust primitive.

### Inputs

#### `text`

* **Type:** `str`
* **Meaning:** Substring to search for inside the string form of each known public identity record.

### Outputs

Returns the matching peer public identity records.

### Example

```python
matches = identity.find_peer("tenant_id")
```

<p align="center">
  <a href="index.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.aurora.identity</b></code></a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="controls.md">Next: <code>SummonerIdentityControls</code> &raquo;</a>
</p>
