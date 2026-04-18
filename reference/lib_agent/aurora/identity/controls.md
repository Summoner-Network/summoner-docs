# `SummonerIdentityControls` (<code style="background: transparent;">Summoner<b>.aurora.identity</b></code>)

This page documents **`SummonerIdentityControls`**, the reusable per-identity controls class exposed from this module.

`SummonerIdentityControls` is useful when one `SummonerIdentity` needs custom storage or trust behavior without changing every identity in the process. It does **not** replace the identity engine itself. Instead, it lets you bundle related hook callbacks and attach them later through `identity.attach_controls(...)`.

Controls callbacks may be synchronous or async, and they always receive the owning `SummonerIdentity` instance as their first argument.

## Import path

```python
from summoner.aurora import SummonerIdentityControls
```

## When to use controls

Use controls when you want a named, reusable group of callbacks for one identity object.

Skip controls when:

* the built-in local stores are sufficient,
* you only need a one-off local override on a single live object, or
* you want process-wide behavior, in which case class-level hooks on `SummonerIdentity` are a better fit.

The table below shows where controls fit compared with the identity runtime's other hook scopes.

| Hook scope | Use when | Typical registration style |
| --- | --- | --- |
| Class hooks | Every identity in one Python process should share the same rule | `@SummonerIdentity.*` |
| Controls object | One or several identities should share the same packaged rule set | `identity.attach_controls(controls)` |
| Instance-local hooks | One live identity needs a narrow override | `@identity.on_*` |

### Hook precedence and selection guidance

The runtime resolves hook behavior in this order:

1. instance-local `@identity.on_*`
2. attached `SummonerIdentityControls`
3. class-level `@SummonerIdentity.*`
4. built-in local logic

This means controls are stronger than process-wide class hooks, but still lower precedence than instance-local hooks attached directly to one live identity object.

One controls object may be reused across multiple identities. If it stores mutable state internally, that state is shared across those identities.

## `SummonerIdentityControls.version`

```python
@staticmethod
def version() -> str
```

### Behavior

Returns the public controls API version string.

This is mainly useful for audits, compatibility checks, or tooling that needs to assert exactly which controls API version is in use.

### Outputs

Returns the current public controls API version string.

### Example

```python
version = SummonerIdentityControls.version()
```

## `SummonerIdentityControls.configured_hooks`

```python
def configured_hooks(self) -> tuple[str, ...]
```

### Behavior

Returns the currently configured hook names on this controls object.

You will usually see some combination of the hook names below:

* `register_session`
* `reset_session`
* `verify_session`
* `get_session`
* `peer_key_store`
* `replay_store`

This method is primarily useful for debugging and introspection.

### Outputs

Returns a tuple of configured hook names in the runtime hook order:

* `register_session`
* `reset_session`
* `verify_session`
* `get_session`
* `peer_key_store`
* `replay_store`

### Example

```python
hooks = controls.configured_hooks()
```

## `SummonerIdentityControls.clear`

```python
def clear(self) -> None
```

### Behavior

Clears all configured callbacks on this controls object.

This does not detach the object from a `SummonerIdentity`. It only removes the callbacks stored on the controls package itself.

### Outputs

Returns `None`.

### Example

```python
controls.clear()
```

## `SummonerIdentityControls.on_register_session`

```python
def on_register_session(
    self,
    fn: Callable[..., bool | Awaitable[bool]],
) -> Callable[..., bool | Awaitable[bool]]
```

### Behavior

Registers the controls callback used to persist session state.

Expected callback shape:

```python
fn(identity, peer_public_id, local_role, session_record, new=False, use_margin=False)
```

Use this when one identity needs custom session persistence or archival behavior.

Important coupling rule:

* If this controls object defines `on_register_session`, it should also define `on_verify_session`.
* The runtime rejects a custom register hook when the active verify hook comes from a different hook scope.

### Inputs

#### `fn`

* **Type:** `Callable[..., bool | Awaitable[bool]]`
* **Meaning:** Callback to use for session registration in this controls object.

### Outputs

Returns the same callback after storing it on the controls object. This is what makes the method usable as a decorator.

### Error handling

Raises `TypeError` if `fn` is not callable.

## `SummonerIdentityControls.on_reset_session`

```python
def on_reset_session(
    self,
    fn: Callable[..., bool | Awaitable[bool]],
) -> Callable[..., bool | Awaitable[bool]]
```

### Behavior

Registers the controls callback used for force-reset semantics on one session lane.

Expected callback shape:

```python
fn(identity, peer_public_id, local_role)
```

Use this when reset behavior must differ from the built-in local session logic.

### Inputs

#### `fn`

* **Type:** `Callable[..., bool | Awaitable[bool]]`
* **Meaning:** Callback to use for reset handling in this controls object.

### Outputs

Returns the same callback after storing it on the controls object.

### Error handling

Raises `TypeError` if `fn` is not callable.

## `SummonerIdentityControls.on_verify_session`

```python
def on_verify_session(
    self,
    fn: Callable[..., Any | Awaitable[Any]],
) -> Callable[..., Any | Awaitable[Any]]
```

### Behavior

Registers the controls callback used to verify inbound session continuity.

Expected callback shape:

```python
fn(identity, peer_public_id, local_role, session_record, use_margin=False)
```

The callback may return either a boolean-like result or a normalized verification object, matching the broader `SummonerIdentity` hook contract.

### Inputs

#### `fn`

* **Type:** `Callable[..., Any | Awaitable[Any]]`
* **Meaning:** Callback to use for session verification in this controls object.

### Outputs

Returns the same callback after storing it on the controls object.

### Error handling

Raises `TypeError` if `fn` is not callable.

## `SummonerIdentityControls.on_get_session`

```python
def on_get_session(
    self,
    fn: Callable[..., Optional[dict] | Awaitable[Optional[dict]]],
) -> Callable[..., Optional[dict] | Awaitable[Optional[dict]]]
```

### Behavior

Registers the controls callback used to look up the current stored session link.

Expected callback shape:

```python
fn(identity, peer_public_id, local_role)
```

Application code does not call this decorator to perform a lookup. Runtime code uses `await identity.get_current_session(...)`, and the hook-aware runtime routes that call through the active hook path automatically.

### Inputs

#### `fn`

* **Type:** `Callable[..., Optional[dict] | Awaitable[Optional[dict]]]`
* **Meaning:** Callback to use for current-session lookup in this controls object.

### Outputs

Returns the same callback after storing it on the controls object.

### Error handling

Raises `TypeError` if `fn` is not callable.

## `SummonerIdentityControls.on_peer_key_store`

```python
def on_peer_key_store(
    self,
    fn: Callable[..., Optional[dict] | Awaitable[Optional[dict]]],
) -> Callable[..., Optional[dict] | Awaitable[Optional[dict]]]
```

### Behavior

Registers the controls callback used to read or update peer-key records.

Expected callback shape:

```python
fn(identity, peer_public_id, update=None)
```

Use this when peer identity learning or peer trust storage needs a custom store or service.

### Inputs

#### `fn`

* **Type:** `Callable[..., Optional[dict] | Awaitable[Optional[dict]]]`
* **Meaning:** Callback to use for peer-key lookup and update operations in this controls object.

### Outputs

Returns the same callback after storing it on the controls object.

### Error handling

Raises `TypeError` if `fn` is not callable.

## `SummonerIdentityControls.on_replay_store`

```python
def on_replay_store(
    self,
    fn: Callable[..., bool | Awaitable[bool]],
) -> Callable[..., bool | Awaitable[bool]]
```

### Behavior

Registers the controls callback used for replay detection and replay writes.

Expected callback shape:

```python
fn(identity, message_id, ttl, now, add)
```

Use this when replay state needs stronger durability, centralization, or audit integration than the built-in local replay store.

### Inputs

#### `fn`

* **Type:** `Callable[..., bool | Awaitable[bool]]`
* **Meaning:** Callback to use for replay checks and replay writes in this controls object.

### Outputs

Returns the same callback after storing it on the controls object.

### Error handling

Raises `TypeError` if `fn` is not callable.

## Example

The example below shows the most common pattern: attach controls to one identity and call the default verification helper inside the custom hook.

```python
from summoner.aurora import SummonerIdentity, SummonerIdentityControls

identity = SummonerIdentity()
identity.id("id.json")

controls = SummonerIdentityControls()
identity.attach_controls(controls)

@controls.on_verify_session
def verify(identity, peer_public_id, local_role, session_record, use_margin=False):
    return identity.verify_session_default(
        peer_public_id,
        local_role,
        session_record,
        use_margin=use_margin,
    )
```

<p align="center">
  <a href="identity.md">&laquo; Previous: SummonerIdentity</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="primitives.md">Next: Primitives and Version Constants &raquo;</a>
</p>
