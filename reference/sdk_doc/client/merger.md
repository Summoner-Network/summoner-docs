# Module: `summoner.client.merger`

Tools for **composing** or **reconstructing** clients from code DNA:

* **`ClientMerger`** — combine multiple live `SummonerClient` instances into a single client by **replaying their handlers** and rebinding their module-level client variables to the merged instance.
* **`ClientTranslation`** — rebuild a client from a **DNA list** (the output of `SummonerClient.dna()`), inlining handlers back into their original modules.

> **Terminology**: *DNA* is the JSON-serializable capture of handlers produced by `SummonerClient.dna()`: it records type (`receive`/`send`/`hook`), decorator parameters, module & function names, and the full handler source.

---

## Public API surface

* Class: **`ClientMerger(SummonerClient)`**

  * `__init__(named_clients, name=None)`
  * `initiate_hooks()` · `initiate_receivers()` · `initiate_senders()`
* Class: **`ClientTranslation(SummonerClient)`**

  * `__init__(dna_list, name=None, var_name='agent')`
  * `initiate_hooks()` · `initiate_receivers()` · `initiate_senders()`
  * overrides: `shutdown()` · `quit()` · `run()`

Internal helpers (documented for completeness): `_clone_handler`, `_make_from_source`, `_apply_with_source_patch`, `_async_shutdown`.

---

## Class: `ClientMerger`

Merge multiple named clients into a single client by **replaying** their decorators on the merged instance. Each handler is **cloned** so that references to the original module-level client variable (e.g., `agent`) now point to the merged client.

### Constructor

```python
ClientMerger.__init__(
    named_clients: list[dict[str, SummonerClient]],
    name: str | None = None,
)
```

**Parameters**

| Name            | Type                              | Required | Description                                                                                                                                                                   |                                              |
| --------------- | --------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `named_clients` | `list[dict[str, SummonerClient]]` | ✓        | Each dict **must** contain keys: `{"var_name": str, "client": SummonerClient}` where `var_name` is the module-level variable the donor handlers use to refer to their client. |                                              |
| `name`          | \`str                             | None\`   |                                                                                                                                                                               | Name for the merged client (used by logger). |

**Behavior & side effects**

* Validates each entry; raises `TypeError` / `KeyError` with explicit messages.
* Cancels any pending registration tasks on donor clients and **closes their event loops** to avoid leftover tasks.
* Stores the cleaned list in `self.named_clients`.

> **Caution**: After merging, donor clients should be considered **retired** (their loops are closed).

### Handler replay

Each `initiate_*` scans the donor's captured DNA lists (`_dna_hooks`, `_dna_receivers`, `_dna_senders`), **clones** the original function object, and registers it on the merged client using the same decorator parameters.

#### `initiate_hooks()`

```python
ClientMerger.initiate_hooks(self) -> None
```

Replays all `@hook` handlers from donors with their original `direction` and `priority`.

#### `initiate_receivers()`

```python
ClientMerger.initiate_receivers(self) -> None
```

Replays all `@receive` handlers from donors with original `route` and `priority`.

#### `initiate_senders()`

```python
ClientMerger.initiate_senders(self) -> None
```

Replays all `@send` handlers with original `route`, `multi`, `on_triggers`, and `on_actions`.

> In `ClientMerger` the donors' `on_triggers` / `on_actions` are **live objects** (e.g., `set[Signal]`, `{Action.MOVE}`) because they're taken from the in-memory DNA (not the JSON). No conversion is needed.

### Internal: `_clone_handler`

```python
ClientMerger._clone_handler(self, fn: types.FunctionType, original_name: str) -> types.FunctionType
```

Clones `fn` so it shares its **module globals** and **closure**, but updates the function's module namespace to bind `original_name` to the **merged client** (`self`). Metadata (`__doc__`, `__annotations__`) is preserved.

**Raises**: logs a warning if the global rebinding fails but still returns a function.

### Minimal example — merge two clients

```python
from summoner.client.merger import ClientMerger

# Suppose these were built elsewhere and decorated with @receive/@send/@hook
agent_a = build_client_A()  # uses module-level name "agent" in its handlers
agent_b = build_client_B()  # uses module-level name "bot" in its handlers

merger = ClientMerger([
    {"var_name": "agent", "client": agent_a},
    {"var_name": "bot",   "client": agent_b},
], name="mega-client")

# Optional: enable flow and arrow styles on the merged client
merger.flow().activate()
merger.flow().add_arrow_style('-', ('[', ']'), ',', '>')

# Replay all handlers onto the merged instance
merger.initiate_hooks()
merger.initiate_receivers()
merger.initiate_senders()

# Run as a normal client
merger.run(config_dict={"logger": {"level": "INFO"}})
```

**Notes**

* If two donors refer to **the same module-level name** in the **same module**, the rebinding targets the **same global** — be mindful of collisions.
* Donor-specific module state (counters, caches) remains shared per module due to cloning with the same `__globals__` and closures.

---

## Class: `ClientTranslation`

Reconstructs a `SummonerClient` from a **DNA list** (parsed from `SummonerClient.dna()`), compiling each handler back into its original module namespace and registering it.

### Constructor

```python
ClientTranslation.__init__(
    dna_list: list[dict[str, Any]],
    name: str | None = None,
    var_name: str = "agent",
)
```

**Parameters**

| Name       | Type                   | Required | Description                                                                                                                                                 |                     |
| ---------- | ---------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| `dna_list` | `list[dict[str, Any]]` | ✓        | The parsed JSON list from `donor.dna()`.                                                                                                                    |                     |
| `name`     | \`str                  | None\`   |                                                                                                                                                             | Logger/client name. |
| `var_name` | `str`                  |          | Name bound into each original module so handlers referring to that module-level client variable now point to this translated instance (default: `"agent"`). |                     |

**Behavior**

* Validates types; raises `TypeError` on bad input.
* Stores DNA and `var_name` for later use in `initiate_*`.

### `initiate_hooks` / `initiate_receivers` / `initiate_senders`

Rebuilds each function from its **source** and registers it with the appropriate decorator.

```python
ClientTranslation.initiate_hooks(self) -> None
ClientTranslation.initiate_receivers(self) -> None
ClientTranslation.initiate_senders(self) -> None
```

* For each DNA entry of the matching `type`, `_make_from_source` loads the original **module**, binds `module_globals[var_name] = self`, then **executes only the `def` block** (decorators are stripped) so top-level module side effects are not rerun.
* Registration is wrapped by `_apply_with_source_patch` to temporarily override `inspect.getsource` so the client can record the exact handler text in its internal DNA capture.
* **Actions** are reconstructed via `getattr(Action, name)`.
* **Signals** are reconstructed as `{Signal[t] for t in names} or None`.

> **Important**: The provided `Signal[...]` lookup implies your environment exposes a **name→Signal** mapping via `Signal["NAME"]`. If you build triggers at runtime, you may need to adapt this resolution (e.g., `{getattr(Trigger, n) for n in names}`) to match your project's trigger loading. See the note below.

### Overrides for graceful shutdown

#### `shutdown()` → non-blocking

Schedules an async `_async_shutdown()` task (cancels handlers, awaits pending decorator registrations and workers, then stops the loop). Safe to call from SIGINT/SIGTERM handlers.

#### `quit()`

Calls the base `quit()` (so the session breaks out of the retry loop) then performs the same cleanup as `shutdown()`.

#### `run()`

Wraps the base `run()` so `KeyboardInterrupt` cancels any leftover registration tasks and exits cleanly (no "coroutine was never awaited").

### Internal helpers

#### `_make_from_source`

```python
ClientTranslation._make_from_source(self, entry: dict[str, Any]) -> types.FunctionType
```

* Imports or reuses the original module.
* Binds `module_globals[var_name] = self`.
* Extracts the `def name(...):` block from `entry["source"]` and `exec`s it in the module namespace.
* Returns the function object.

**Raises**: `ImportError` (module missing), `RuntimeError` (cannot find `def` or not a function after exec).

#### `_apply_with_source_patch`

Temporarily patches `inspect.getsource` so the decorator can record the correct source.

#### `_async_shutdown`

Async cleanup helper used by `shutdown()`/`quit()`.

### Minimal example — translate from DNA

```python
import json
from summoner.client.merger import ClientTranslation

# Donor → DNA (e.g., captured at runtime or stored)
dna_list = json.loads(donor_client.dna())

clone = ClientTranslation(dna_list, name="clone", var_name="agent")
clone.flow().activate()
clone.flow().add_arrow_style('-', ('[', ']'), ',', '>')

clone.initiate_hooks()
clone.initiate_receivers()
clone.initiate_senders()

clone.run(config_dict={"logger": {"level": "INFO"}})
```

### Signal-name resolution note

If your build does **not** provide `Signal["NAME"]` lookup, reconstruct triggers explicitly and adapt `initiate_senders` before calling it, for example:

```python
# Build a Trigger class first (same hierarchy as the donor used)
Trigger = clone.flow().triggers(text="""
OK
  acceptable
  all_good
error
  minor
  major
""")

# Monkey-patch a helper to convert DNA names → Signal objects
resolve = lambda names: {getattr(Trigger, n) for n in names}

# If needed, you can loop over clone._dna_list to pre-resolve `on_triggers` fields
# before calling clone.initiate_senders().
```

> **Security**: Translating from DNA executes **handler source code**. Only load DNA from trusted origins.

---

## Error reference

* Wrong `named_clients` shape → `TypeError`/`KeyError` with index and missing key details.
* Non-async decorators in donors are already rejected by `SummonerClient`; merge/translate only replay valid handlers.
* Module import failure in translation → `ImportError` with module name.
* Function extraction failure (cannot find `def`) → `RuntimeError`.

---

## See also

* `summoner.client.client.SummonerClient` — base class providing decorators and run loop
* `SummonerClient.dna()` — producing the DNA list consumed by `ClientTranslation`
* `summoner.protocol.triggers` — `Signal`, `Action`, trigger building


<p align="center">
  <a href="./client.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.client.client</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../client.md">Next: <code style="background: transparent;">Summoner<b>.client</b></code> &raquo;</a>
</p>