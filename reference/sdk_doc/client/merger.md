# <code style="background: transparent;">Summoner<b>.client.merger</b></code>

This page documents the **Python SDK interface** for composing clients from other clients or from DNA artifacts. It focuses on how to use the public classes and their methods, and what behavior to expect when you call them.

This module provides two related utilities built on top of `SummonerClient`:

* **`ClientMerger`**: build a single composite client by replaying handlers from multiple sources (live imported clients and/or DNA).
* **`ClientTranslation`**: reconstruct a fresh client from a DNA list by compiling handlers into an isolated sandbox module.

## Security note

Both classes may execute code found in DNA via `exec()` / `eval()` (context imports, recipes, handler bodies). Use only with **trusted DNA** (typically produced by your own agents). Do not run untrusted DNA.

## `ClientMerger.__init__`

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

Creates a composite client that can later replay handlers from multiple sources.

A "source" can be any of:

* an imported `SummonerClient` instance (live object),
* a DNA list (`list[dict]`),
* a DNA JSON file path,
* or a dict wrapper with one of: `{"client": ...}`, `{"dna_list": ...}`, `{"dna_path": ...}`.

The merger **does not** automatically register handlers on construction. You must call `initiate_all()` (or individual `initiate_*` methods) before calling `run(...)`.

If `close_subclients=True`, the merger attempts to **clean up imported template clients** after extracting their handlers (to reduce pending-task and event-loop warnings when importing agent scripts as templates).

### Inputs

#### `named_clients`

* **Type:** `list[Any]`
* **Meaning:** List of sources to merge.
* **Accepted entry formats:**

  * `SummonerClient` instance
  * DNA list (`list[dict]`)
  * dict with one of:

    * `{"client": SummonerClient, "var_name": Optional[str]}`
    * `{"dna_list": list[dict], "var_name": Optional[str]}`
    * `{"dna_path": str, "var_name": Optional[str]}`

#### `name`

* **Type:** `Optional[str]`
* **Meaning:** Logical name used for logging.
* **Default behavior:** Falls back to `SummonerClient`'s default placeholder if not provided.

#### `rebind_globals`

* **Type:** `Optional[dict[str, Any]]`
* **Meaning:** Extra globals injected into:

  * sandbox globals for DNA sources, and
  * handler globals for imported-client sources.
* **Typical use:** supply "missing" symbols referenced by handlers (shared objects, Trigger/Action-like bindings, utilities).

#### `allow_context_imports`

* **Type:** `bool`
* **Meaning:** Whether to execute import lines recorded in DNA `__context__` headers.
* **Default:** `True`

#### `verbose_context_imports`

* **Type:** `bool`
* **Meaning:** Whether to log successful context imports as well as failures.
* **Default:** `False`

#### `close_subclients`

* **Type:** `bool`
* **Meaning:** Whether to attempt best-effort cleanup of imported template clients after extraction.
* **Default:** `True`

### Outputs

Creates a `ClientMerger` instance (subclass of `SummonerClient`).

### Examples

#### Merge two imported clients

```python
from summoner.client.client import SummonerClient
from summoner.client.merger import ClientMerger

a = SummonerClient(name="a")
b = SummonerClient(name="b")

agent = ClientMerger([a, b], name="merged")
agent.initiate_all()
agent.run(host="127.0.0.1", port=8888)
```

#### Merge imported client + DNA file

```python
from summoner.client.client import SummonerClient
from summoner.client.merger import ClientMerger

template = SummonerClient(name="template")

agent = ClientMerger(
    [
        template,
        {"dna_path": "agent_dna.json"},
    ],
    name="merged",
    rebind_globals={"SOME_SHARED": object()},
)
agent.initiate_all()
agent.run(host="127.0.0.1", port=8888)
```

## `ClientMerger.initiate_all`

```python
def initiate_all(self) -> None
```

### Behavior

Replays all supported handler types from every source onto the merged client, in a standard order:

1. `upload_states`
2. `download_states`
3. `hook`
4. `receive`
5. `send`

This should be called before `run(...)`.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

#### Standard merger usage pattern

```python
from summoner.client.merger import ClientMerger

agent = ClientMerger([{"dna_path": "a.json"}, {"dna_path": "b.json"}], name="merged")
agent.initiate_all()
agent.run(host="127.0.0.1", port=8888)
```

## `ClientMerger.initiate_upload_states`

```python
def initiate_upload_states(self) -> None
```

### Behavior

Replays `@upload_states()` handlers from every source onto the merged client.

* For imported-client sources: clones the handler, rebinding the original client variable name (commonly `"agent"`) to the merged client and injecting `rebind_globals`.
* For DNA sources: compiles the function in the DNA sandbox and registers it onto the merged client.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientMerger

agent = ClientMerger([{"dna_path": "a.json"}], name="merged")
agent.initiate_upload_states()
```

## `ClientMerger.initiate_download_states`

```python
def initiate_download_states(self) -> None
```

### Behavior

Replays `@download_states()` handlers from every source onto the merged client.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientMerger

agent = ClientMerger([{"dna_path": "a.json"}], name="merged")
agent.initiate_download_states()
```

## `ClientMerger.initiate_hooks`

```python
def initiate_hooks(self) -> None
```

### Behavior

Replays `@hook(Direction, priority=...)` handlers from every source onto the merged client.

* Imported-client sources keep module-backed execution (their original globals dict).
* DNA sources compile hooks into the per-source sandbox and then register them normally.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientMerger

agent = ClientMerger([{"dna_path": "a.json"}], name="merged")
agent.initiate_hooks()
```

## `ClientMerger.initiate_receivers`

```python
def initiate_receivers(self) -> None
```

### Behavior

Replays `@receive(route, priority=...)` handlers from every source onto the merged client.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientMerger

agent = ClientMerger([{"dna_path": "a.json"}], name="merged")
agent.initiate_receivers()
```

## `ClientMerger.initiate_senders`

```python
def initiate_senders(self) -> None
```

### Behavior

Replays `@send(route, multi, on_triggers, on_actions)` handlers from every source onto the merged client.

For DNA sources, triggers/actions are stored by **name** and are resolved as follows:

* **Triggers**:

  * prefers a `Trigger` binding present in the sandbox globals (often provided by context or `rebind_globals`),
  * otherwise falls back to default trigger loading (`load_triggers()`).

* **Actions**:

  * resolved by name against the protocol `Action` container.

If trigger/action names cannot be resolved, replay may fail for that sender.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

#### Merge DNA that references `Trigger` via context

```python
from summoner.client.merger import ClientMerger

agent = ClientMerger([{"dna_path": "agent_dna.json"}], name="merged")
agent.initiate_senders()
```

#### Merge DNA that requires a `Trigger` binding via `rebind_globals`

```python
from summoner.client.merger import ClientMerger
from summoner.protocol.triggers import load_triggers

Trigger = load_triggers()

agent = ClientMerger(
    [{"dna_path": "agent_dna.json"}],
    name="merged",
    rebind_globals={"Trigger": Trigger},
)
agent.initiate_senders()
```

## `ClientTranslation.__init__`

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

Constructs a new `SummonerClient` from a DNA list by compiling handlers into a dedicated sandbox module, then preparing them for replay via `initiate_*`.

Key properties of translation:

* Handlers are not executed in their original modules.
* Handlers run in the translation sandbox with explicit bindings:

  * `var_name` (often `"agent"`) is bound to the translated client,
  * optional context (imports/globals/recipes) may be applied,
  * optional `rebind_globals` may be injected.

This class also attempts best-effort cleanup of "template clients" that may have been created as a side effect of importing modules referenced by DNA entries.

### Inputs

#### `dna_list`

* **Type:** `list[dict[str, Any]]`
* **Meaning:** Parsed DNA entries (already JSON-decoded).
* **Note:** If the DNA begins with a `__context__` entry, it may be applied into the sandbox.

#### `name`

* **Type:** `Optional[str]`
* **Meaning:** Logical name used for logging.

#### `var_name`

* **Type:** `Optional[str]`
* **Meaning:** The global name used inside handler source code to reference the client (for example `"agent"`).
* **Default behavior:** uses `__context__.var_name` if present, otherwise `"agent"`.

#### `rebind_globals`

* **Type:** `Optional[dict[str, Any]]`
* **Meaning:** Extra globals injected into the sandbox to satisfy referenced symbols (shared objects, Trigger bindings, etc.).

#### `allow_context_imports`

* **Type:** `bool`
* **Meaning:** Whether to execute import lines from a DNA `__context__` entry.
* **Default:** `True`

#### `verbose_context_imports`

* **Type:** `bool`
* **Meaning:** Whether to log successful context imports.
* **Default:** `False`

### Outputs

Creates a `ClientTranslation` instance (subclass of `SummonerClient`).

### Examples

#### Translate from an in-memory DNA list

```python
import json
from summoner.client.merger import ClientTranslation

dna_list = json.loads(open("agent_dna.json", "r", encoding="utf-8").read())

agent = ClientTranslation(dna_list, name="translated")
agent.initiate_all()
agent.run(host="127.0.0.1", port=8888)
```

## `ClientTranslation.initiate_all`

```python
def initiate_all(self) -> None
```

### Behavior

Replays all handler types from the DNA list onto this translated client, in the standard order:

1. `upload_states`
2. `download_states`
3. `hook`
4. `receive`
5. `send`

Call this before `run(...)`.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientTranslation

agent = ClientTranslation(dna_list, name="translated")
agent.initiate_all()
agent.run(host="127.0.0.1", port=8888)
```

## `ClientTranslation.initiate_upload_states`

```python
def initiate_upload_states(self) -> None
```

### Behavior

Replays `@upload_states()` from DNA onto this translated client.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientTranslation

agent = ClientTranslation(dna_list, name="translated")
agent.initiate_upload_states()
```

## `ClientTranslation.initiate_download_states`

```python
def initiate_download_states(self) -> None
```

### Behavior

Replays `@download_states()` from DNA onto this translated client.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientTranslation

agent = ClientTranslation(dna_list, name="translated")
agent.initiate_download_states()
```

## `ClientTranslation.initiate_hooks`

```python
def initiate_hooks(self) -> None
```

### Behavior

Replays `@hook(...)` entries from DNA onto this translated client.

Direction and priorities are interpreted from the DNA entries and applied to the normal `SummonerClient.hook(...)` decorator.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientTranslation

agent = ClientTranslation(dna_list, name="translated")
agent.initiate_hooks()
```

## `ClientTranslation.initiate_receivers`

```python
def initiate_receivers(self) -> None
```

### Behavior

Replays `@receive(...)` entries from DNA onto this translated client.

Routes and priorities are interpreted from the DNA entries and applied to the normal `SummonerClient.receive(...)` decorator.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

```python
from summoner.client.merger import ClientTranslation

agent = ClientTranslation(dna_list, name="translated")
agent.initiate_receivers()
```

## `ClientTranslation.initiate_senders`

```python
def initiate_senders(self) -> None
```

### Behavior

Replays `@send(...)` entries from DNA onto this translated client.

Triggers and actions are stored in DNA by name and are resolved as follows:

* **Triggers**:

  * uses a `Trigger` binding found in the sandbox globals (possibly from context or `rebind_globals`),
  * otherwise uses `load_triggers()`.

* **Actions**:

  * resolved by name against the protocol `Action` container.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

#### Provide Trigger via `rebind_globals`

```python
from summoner.client.merger import ClientTranslation
from summoner.protocol.triggers import load_triggers

Trigger = load_triggers()

agent = ClientTranslation(
    dna_list,
    name="translated",
    rebind_globals={"Trigger": Trigger},
)
agent.initiate_senders()
```

## End-to-end examples

### Example: merge two DNA files into one runnable client

#### merge_and_run.py

```python
import json
from summoner.client.merger import ClientMerger

a = json.loads(open("a.json", "r", encoding="utf-8").read())
b = json.loads(open("b.json", "r", encoding="utf-8").read())

agent = ClientMerger([a, b], name="merged")
agent.initiate_all()
agent.run(host="127.0.0.1", port=8888)
```

### Example: translate DNA into a fresh client, then run

#### translate_and_run.py

```python
import json
from summoner.client.merger import ClientTranslation

dna_list = json.loads(open("agent_dna.json", "r", encoding="utf-8").read())

agent = ClientTranslation(dna_list, name="translated")
agent.initiate_all()
agent.run(host="127.0.0.1", port=8888)
```

---


<p align="center">
  <a href="./configs.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.client</b></code> configuration guide</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../client.md">Next: <code style="background: transparent;">Summoner<b>.client</b></code> &raquo;</a>
</p>