# Agent Extensions

`extension-agentclass` is a companion repository of **client-level extensions** that augment the composed Summoner SDK with higher-level orchestration features. Unlike utility extensions, these modules are meant to extend the *runtime surface* of the client (for example, by adding new decorators, handler patterns, or execution controls).

The intended workflow is:

* choose the agent extensions you want (for example `aurora`)
* add them to your SDK composition list (via `build.txt`)
* import them from the composed SDK as normal Python modules (for example `from summoner.aurora import ...`)

These extensions are "client-level" in the sense that they sit on top of `SummonerClient` and provide additional behavior for agent execution and communication. They are designed to remain compatible with the core protocol, while making advanced patterns easier to express.

## Repository and import model

The `extension-agentclass` repository follows the [`extension-template`](https://github.com/Summoner-Network/extension-template) layout, which implies that each extension lives under `tooling/<module>/`.

During local development, import from `tooling.*`:

```python
from tooling.aurora import AuroraClient
```

During SDK composition, the builder copies `tooling/<module>/` into `summoner/<module>/` and rewrites imports of the form `from tooling.<module> ...` into the public namespace:

```python
from summoner.aurora import AuroraClient
```

> [!NOTE]
> In the repository, the script `install.sh setup` boots a dev environment and installs `summoner-core`. It does not compose a new SDK.
> Composition happens in an SDK project via `build.txt`.

## Installation in a summoner-sdk workflow

For every project based on the [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk) template, you can include a module by adding it to `build.txt`. Each entry specifies the extension repository and the module name to merge during SDK composition.

Minimal pattern:

```text
https://github.com/Summoner-Network/extension-agentclass.git:
<module_name>
```

Example:

```text
https://github.com/Summoner-Network/extension-agentclass.git:
aurora
```

After composition, you import from the `summoner.*` namespace:

```python
from summoner.aurora import SummonerAgent
```

> [!NOTE]
> Inside the `extension-agentclass` repository itself, local tests may import modules directly from the repo layout (for example `from tooling.aurora import ...`). For normal SDK usage, always import from `summoner.<module>`.

## Aurora

* Extends the `SummonerClient` with advanced decorator-based handlers and orchestration controls.
* *Status:* Available for testing (pre-release `beta.1.1.2`).
* Link: [<code style="background: transparent;">aurora</code>](aurora.md)

<p align="center">
  <a href="../sdk_doc/proto.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.protocol</b></code></a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../lib_utils/index.md">Next: Utility Extensions &raquo;</a>
</p>

