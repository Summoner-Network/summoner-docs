# <code style="background: transparent;">Summoner<b>.aurora.agentmerger</b></code> (Aurora v1.0.0)

This page documents **`AgentMerger`** and **`AgentTranslation`**, the Aurora classes used to rebuild Aurora behavior from clients or DNA.

Use these classes when Aurora behavior already exists somewhere else and you want to reconstruct it inside a new Aurora client:

* **`AgentMerger`** combines several sources into one Aurora client.
* **`AgentTranslation`** rebuilds one fresh Aurora client from DNA alone.

The most important point is that the result is still an Aurora client. After reconstruction, you can attach a `SummonerIdentity`, inspect `agent.identity`, add keyed receivers, inspect replay state, and export Aurora DNA again.

Import the module directly as:

```python
from summoner.aurora.agentmerger import AgentMerger, AgentTranslation
```

> [!NOTE]
> Both names are also re-exported from `summoner.aurora`. This page uses the direct module path so the reference matches the public Aurora modules.

If you need the full baseline constructor semantics, read the core merger page alongside this one:

* [<code style="background: transparent;">Summoner<b>.client.merger</b></code>](../../sdk_doc/client/merger.md) → `ClientMerger`
* [<code style="background: transparent;">Summoner<b>.client.merger</b></code>](../../sdk_doc/client/merger.md) → `ClientTranslation`

## Choosing between the two classes

The table below gives a quick orientation before the method reference starts.

| Class | Start from | Use when |
| --- | --- | --- |
| `AgentMerger` | imported clients, DNA paths, DNA lists, or wrapped sources | You want one composite Aurora client assembled from several inputs |
| `AgentTranslation` | a DNA list | You want one fresh Aurora client reconstructed from DNA alone |

## Typical Aurora-specific pattern

The snippet below shows the Aurora part of the workflow. For a full reconstruction flow including hooks, senders, and state handlers, combine this page with the core merger docs.

```python
from summoner.aurora import AgentMerger

agent = AgentMerger([{"dna_path": "aurora_agent.json"}], name="aurora:merged")
agent.initiate_receivers()

identity = agent.attach_identity(store_dir="./identity")
identity.id("id.json", password=b"strong-passphrase")
```

## Security note

Like the core merger layer, Aurora merger and translation may execute code from DNA via `exec()` or `eval()`. Use only with **trusted DNA**.

### Aurora DNA preservation rules

Aurora keyed receivers are not the same as plain `@receive(...)` handlers.

To preserve keyed receiver behavior across DNA export and import:

* export Aurora DNA with `agent.dna(flavor="aurora")`, or
* export Aurora DNA with `agent.aurora_dna(...)`

The exact export contract is documented in [SummonerAgent](agent.md).

If you export using core DNA in a lossy mode:

* keyed receivers are downgraded to plain `receive` entries,
* lock and replay semantics are not reconstructible from that DNA alone,
* `AgentMerger` and `AgentTranslation` can only replay the plain receiver behavior that remains.

## `AgentMerger.__init__`

```python
def __init__(
    self,
    named_clients: list[Any],
    name: Optional[str] = None,
    rebind_globals: Optional[dict[str, Any]] = None,
    allow_context_imports: bool = True,
    verbose_context_imports: bool = False,
    close_subclients: bool = True,
) -> None
```

### Behavior

Creates an Aurora-aware composite client by inheriting the normal `ClientMerger` construction flow and layering Aurora receiver replay and Aurora client behavior onto it.

Normal merge behavior remains the same as the core merger:

* sources may be imported clients, DNA lists, DNA paths, or wrapper dicts,
* handler replay still happens later via `initiate_all()` or individual `initiate_*` methods,
* non-Aurora handlers follow the core merger behavior.

What Aurora adds is that the resulting object is itself an Aurora client:

* it can host a `SummonerIdentity`,
* it can replay Aurora keyed receivers during `initiate_receivers()`,
* it continues to expose the shared Aurora client helpers documented on [SummonerAgent](agent.md).

### Inputs

These inputs have the same meaning as in `ClientMerger.__init__`:

* `named_clients`
* `name`
* `rebind_globals`
* `allow_context_imports`
* `verbose_context_imports`
* `close_subclients`

For the full constructor contract, see [<code style="background: transparent;">Summoner<b>.client.merger</b></code>](../../sdk_doc/client/merger.md).

### Outputs

Creates an `AgentMerger` instance.

### Example

```python
from summoner.aurora import AgentMerger

agent = AgentMerger(
    [{"dna_path": "agent_dna.json"}],
    name="aurora:merged",
)
```

## `AgentTranslation.__init__`

```python
def __init__(
    self,
    dna_list: list[dict[str, Any]],
    name: Optional[str] = None,
    var_name: Optional[str] = None,
    rebind_globals: Optional[dict[str, Any]] = None,
    allow_context_imports: bool = True,
    verbose_context_imports: bool = False,
) -> None
```

### Behavior

Creates a fresh Aurora client from a DNA list by inheriting the normal `ClientTranslation` construction flow and layering Aurora receiver replay and Aurora client behavior onto it.

What Aurora adds is the same as for `AgentMerger`:

* hosted identity binding,
* replay of Aurora keyed receivers during `initiate_receivers()`,
* continued access to the shared Aurora client helpers documented on [SummonerAgent](agent.md).

### Inputs

These inputs have the same meaning as in `ClientTranslation.__init__`:

* `dna_list`
* `name`
* `var_name`
* `rebind_globals`
* `allow_context_imports`
* `verbose_context_imports`

For the full constructor contract, see [<code style="background: transparent;">Summoner<b>.client.merger</b></code>](../../sdk_doc/client/merger.md).

### Outputs

Creates an `AgentTranslation` instance.

### Example

```python
from summoner.aurora import AgentTranslation

agent = AgentTranslation(
    dna_list=aurora_dna_list,
    name="aurora:translated",
)
```

## `(AgentMerger | AgentTranslation).identity`

```python
identity: Optional[SummonerIdentity]
```

### Behavior

Both classes expose their attached identity through the `identity` attribute, just like `SummonerAgent`.

This attribute is `None` until you call `attach_identity(...)`. After attachment, it holds the exact `SummonerIdentity` instance currently hosted by the merged or translated client.

Attachment and identity-file initialization are separate steps. A newly attached identity may still need `id(...)` before session, envelope, peer-tracking, or continuity workflows are meaningful.

### Type

`Optional[SummonerIdentity]`

### Typical use

* Read `agent.identity` when you want the full identity engine after attachment.
* Call `require_identity()` when the workflow should fail immediately if no identity is attached.
* Call `has_identity()` when you only need to test whether one is present.

## `(AgentMerger | AgentTranslation).identity_versions`

```python
@staticmethod
def identity_versions() -> dict[str, str]
```

### Behavior

Returns the public identity compatibility versions exposed by these classes.

The contract is the same as on `SummonerAgent`. This is useful when the reconstructed client is part of a diagnostic, audit, or compatibility-reporting workflow.

### Outputs

Returns a dictionary with the keys:

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
from summoner.aurora import AgentMerger

versions = AgentMerger.identity_versions()
controls_version = versions["controls"]
```

## `(AgentMerger | AgentTranslation).attach_identity`

```python
def attach_identity(
    self,
    identity: Optional[SummonerIdentity] = None,
    controls: Optional[object] = None,
    **summoner_identity_kwargs: Any,
) -> SummonerIdentity
```

### Behavior

Attaches a `SummonerIdentity` to the merged or translated client.

The contract is the same as on `SummonerAgent`: you can either attach an existing identity or construct one inline from keyword arguments. If `controls` is provided, the method attaches those controls before storing the identity on `agent.identity`.

This is the usual step when a reconstructed Aurora client needs to operate under an active principal after merger or translation.

### Inputs

#### `identity`

* **Type:** `Optional[SummonerIdentity]`
* **Meaning:** Existing identity object to attach.
* **Default:** `None`

#### `controls`

* **Type:** `Optional[object]`
* **Meaning:** Optional controls object to attach before storing the identity on the client.
* **Default:** `None`

#### `**summoner_identity_kwargs`

* **Type:** `Any`
* **Meaning:** Keyword arguments passed to `SummonerIdentity(...)` when `identity` is not supplied.
* **Validation:** If `identity` is provided, you must not also provide constructor kwargs.

### Outputs

Returns the attached `SummonerIdentity`.

### Error handling

* If both `identity` and `summoner_identity_kwargs` are provided, `ValueError` is raised.
* If `identity` is provided but is not a `SummonerIdentity`, `TypeError` is raised.

### Example

```python
from summoner.aurora import AgentMerger

agent = AgentMerger([{"dna_path": "aurora_agent.json"}], name="aurora:merged")
identity = agent.attach_identity(store_dir="./identity")
identity.id("id.json", password=b"strong-passphrase")
```

The same pattern works on `AgentTranslation`.

## `(AgentMerger | AgentTranslation).detach_identity`

```python
def detach_identity(self) -> Optional[SummonerIdentity]
```

### Behavior

Detaches the currently hosted identity, if any, and clears `agent.identity`.

The detached identity object itself is returned unchanged. The method does not close the identity, reset its internal stores, or remove attached controls. It only removes the host reference from the current reconstructed client.

### Outputs

Returns the detached `SummonerIdentity`, or `None` if no identity was attached.

### Example

```python
from summoner.aurora import AgentMerger

identity = agent.detach_identity()

if identity is not None:
    standby = AgentMerger([{"dna_path": "standby_agent.json"}], name="aurora:standby")
    standby.attach_identity(identity)
```

## `(AgentMerger | AgentTranslation).require_identity`

```python
def require_identity(self) -> SummonerIdentity
```

### Behavior

Returns the currently attached identity.

Use this when the reconstructed client must already have an active identity and the absence of one should be treated as an immediate error.

This is an attachment check only. It does not verify that `id(...)` has already loaded or generated the local identity file.

### Outputs

Returns the current `SummonerIdentity`.

### Error handling

Raises `RuntimeError` if no identity is attached.

### Example

```python
identity = agent.require_identity()
```

## `(AgentMerger | AgentTranslation).has_identity`

```python
def has_identity(self) -> bool
```

### Behavior

Returns whether an identity is currently attached to the reconstructed Aurora client.

This is a lightweight attachment check only. It returns `True` as soon as `attach_identity(...)` stores a `SummonerIdentity` on the client, even if `id(...)` has not been called yet.

### Outputs

Returns `True` when `agent.identity` is populated, otherwise `False`.

### Example

```python
if not agent.has_identity():
    agent.attach_identity(store_dir="./identity")
```

## `AgentMerger.initiate_receivers`

```python
def initiate_receivers(self) -> None
```

### Behavior

Replays receiver handlers onto the merged client, including both:

* normal core `@receive(...)` handlers,
* Aurora `@keyed_receive(...)` handlers.

At a high level, `AgentMerger.initiate_receivers()` does two passes:

1. replays the normal core receivers,
2. performs an Aurora-specific pass for keyed receivers.

During the Aurora pass:

* imported-client sources are inspected for `client._dna_aurora_receivers`,
* DNA sources are inspected for entries whose `type` is `aurora:keyed_receive`,
* stored `key_by` and `seq_by` extractor specifications are resolved back into strings or callables,
* each keyed receiver is replayed onto the merged client via `self.keyed_receive(...)`.

### Imported-client behavior

For imported Aurora clients, the merger:

* clones the original handler into the merged client context,
* resolves the keyed extractor and optional sequence extractor,
* preserves `priority` and `seq_history_max_entries`.

### DNA-source behavior

For Aurora DNA entries, the merger:

* compiles the handler from stored source text in the DNA sandbox,
* reconstructs extractor specifications from the stored Aurora fields,
* replays the handler as a keyed receiver on the merged client.

### Error handling

For imported-client Aurora receivers, replay failures are logged with a warning and the merger continues with the remaining imported keyed receivers.

For Aurora DNA entries, replay errors propagate to the caller instead of being wrapped in a warning-and-continue path.

### Outputs

Returns `None`.

### Example

```python
from summoner.aurora import AgentMerger

agent = AgentMerger(
    [{"dna_path": "aurora_agent.json"}],
    name="aurora:merged",
)
agent.initiate_receivers()
```

## `AgentTranslation.initiate_receivers`

```python
def initiate_receivers(self) -> None
```

### Behavior

Replays receiver handlers from the DNA list onto the translated client, including both:

* normal core `receive` entries,
* Aurora `aurora:keyed_receive` entries.

At a high level, `AgentTranslation.initiate_receivers()`:

1. replays the normal core receivers,
2. scans the DNA list for Aurora keyed receiver entries,
3. compiles each handler from its stored source,
4. resolves the serialized `key_by` and `seq_by` extractor specifications,
5. replays the handler using `self.keyed_receive(...)`.

### Error handling

Errors while compiling a DNA handler or resolving serialized extractor specifications propagate to the caller.

### Outputs

Returns `None`.

### Example

```python
from summoner.aurora import AgentTranslation

agent = AgentTranslation(dna_list=aurora_dna_list, name="aurora:translated")
agent.initiate_receivers()
```

## Shared Aurora client methods after construction

After `AgentMerger` or `AgentTranslation` has been constructed, the resulting object still exposes the Aurora client helpers below. The exact contract for each helper is the same as on `SummonerAgent`, so this table points you to the page that expands those shared methods in full.

| Shared method family | Where the full contract is documented | Why you might use it here |
| --- | --- | --- |
| `keyed_receive(...)` | [SummonerAgent](agent.md) | Add new keyed handlers directly on the merged or translated client |
| `clear_keyed_receive_replay_state(...)` and `keyed_receive_replay_stats()` | [SummonerAgent](agent.md) | Inspect or reset replay memory for imported keyed receivers |
| `core_dna(...)`, `aurora_dna(...)`, and `dna(...)` | [SummonerAgent](agent.md) | Re-export the reconstructed client after additional edits |

## Operational notes

The list below is a useful final checklist when working with reconstructed Aurora clients.

* Aurora-aware receiver replay only applies when the source actually contains Aurora keyed receiver metadata.
* Plain receive handlers are still replayed by the inherited core merger logic.
* Identity binding works the same way here as on `SummonerAgent`, because the reconstructed object is still an Aurora client.

<p align="center">
  <a href="agent.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.aurora.agentclass</b></code></a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="identity/index.md">Next: <code style="background: transparent;">Summoner<b>.aurora.identity</b></code> &raquo;</a>
</p>
