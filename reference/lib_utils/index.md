# Utility Extensions

`extension-utilities` is a companion repository of **optional modules** that can be merged into a composed Summoner SDK. Each module is self-contained, exposing a small public interface that can be added (or omitted) without changing the core runtime.

The intended workflow is:

* choose the utility modules you want (for example `visionary`, `curl_tools`, `gpt_guardrails`)
* add them to your SDK composition list (via `build.txt`)
* import them from the composed SDK like normal Python modules (for example `from summoner.visionary import ...`)

These utilities are protocol-level in the sense that they help you operate agents (visualization, parsing, budgeting, cryptographic helpers). They do not change the agent execution model or networking semantics implemented in `summoner-core`.

## Repository and import model

The `extension-utilities` repository follows the [`extension-template`](https://github.com/Summoner-Network/extension-template) layout, which implies that each utility lives under `tooling/<module>/`.

During local development, import from `tooling.*`:

```python
from tooling.visionary import ClientFlowVisualizer
```

During SDK composition, the builder copies `tooling/<module>/` into `summoner/<module>/` and rewrites imports of the form `from tooling.<module> ...` into the public namespace:

```python
from summoner.visionary import ClientFlowVisualizer
```

> [!NOTE]
> In the repository, the script `install.sh setup` boots a dev environment and installs `summoner-core`. It does not compose a new SDK.
> Composition happens in an SDK project via `build.txt`.


## Installation in a summoner-sdk workflow

For projects built using the [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk) template, you can include a module by adding it to `build.txt`. Each entry specifies the extension repository and the module name to merge during SDK composition.

Minimal pattern:

```text
https://github.com/Summoner-Network/extension-utilities.git:
<module_name>
```

Example:

```text
https://github.com/Summoner-Network/extension-utilities.git:
visionary
curl_tools
gpt_guardrails
```

After composition, you import from the `summoner.*` namespace:

```python
from summoner.curl_tools import CurlToolCompiler
from summoner.gpt_guardrails import count_chat_tokens
from summoner.visionary import ClientFlowVisualizer
```

> [!NOTE]
> Inside the `extension-utilities` repository itself, local tests may import modules directly from the repo layout (for example `from tooling.curl_tools import ...`). For normal SDK usage, always import from `summoner.<module>`.

## Visionary

* Visualization and state introspection tools for agent graphs and execution flow.
* *Status:* Stable.
* Link: [<code style="background: transparent;">visionary</code>](visionary.md)

## PDF Tools

* Utilities for reading, parsing, and extracting structured data from PDF files.
* *Status:* Experimental.
* Link: [<code style="background: transparent;">pdf_tools</code>](pdf_tools.md)

## Code Tools

* Utilities for reading, analyzing, and interpreting source code files.
* *Status:* In progress.
* Link: [<code style="background: transparent;">code_tools</code>](code_tools.md)

## cURL Tools

* Utilities for parsing and interpreting `curl` commands into structured protocol calls.
* *Status:* In progress.
* Link: [<code style="background: transparent;">curl_tools</code>](curl_tools.md)

## LLM Guardrails

* Cost control and safety utilities for managing LLM usage and execution constraints.
* *Status:* Experimental.
* Link: [<code style="background: transparent;">gpt_guardrails</code>](gpt_guardrails.md)

## Crypto Utils

* Cryptographic helpers for signing, verification, and secure protocol interactions.
* *Status:* Experimental.
* Link: [<code style="background: transparent;">crypto_utils</code>](crypto_utils.md)

<p align="center">
  <a href="../lib_agent/index.md">&laquo; Previous: Agent Extentions</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../../development/index.md">Next: Developer & Contribution &raquo;</a>
</p>
