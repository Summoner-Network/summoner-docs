# SDK Reference

> [!CAUTION]
> This reference is still being refined as naming and semantics settle. The Core SDK is usable for day-to-day development, but some sections may change as we finalize stability guarantees. For walkthroughs and end-to-end examples, see the **[Summoner SDK Guides](../guide_sdk/index.md)**.

## Core SDK

The Core SDK provides the runtime building blocks for agents: the client runtime, the relay server, and the protocol primitives.

* [<code style="background: transparent;">Summoner<b>.client</b></code>](sdk_doc/client.md) → Use `SummonerClient` to build a networked agent with a decorator model: register **receive**, **send**, and **hook** handlers, optionally enable flow-aware routing, and export/merge the agent’s DNA for portability.

* [<code style="background: transparent;">Summoner<b>.server</b></code>](sdk_doc/server.md) → Use `SummonerServer` to run the TCP relay that clients connect to, either with a Python (**asyncio**) backend or a Rust (**Tokio**) backend, with backpressure, rate limiting, and quarantine controls for reliability under load.

* [<code style="background: transparent;">Summoner<b>.protocol</b></code>](sdk_doc/proto.md) → Use the protocol primitives behind flow-aware routing: define trigger trees, parse routes into typed structures, and use state tapes so agent interactions can be structured, debuggable, and replayable.


## Agent Extensions

Client-level extensions that augment the Core SDK runtime with additional orchestration, memory, and security capabilities. These are official enhancements to the core protocol, designed for advanced agent communication and execution patterns.

* **Aurora**

  * Extends the `SummonerClient` with advanced decorator-based handlers and orchestration controls.
  * *Status:* Available for testing (pre-release).
  * Link: [Aurora](lib_agent/aurora.md)


## Utility Extensions

Protocol-level utilities that provide optional tools, helpers, and operational safeguards for agents. These extensions add capabilities without modifying the core runtime.

* **Visionary**

  * Visualization and state introspection tools for agent graphs and execution flow.
  * *Status:* Stable.
  * Link: [<code style="background: transparent;">visionary</code>](lib_utils/visionary.md)

* **PDF Tools**

  * Utilities for reading, parsing, and extracting structured data from PDF files.
  * *Status:* Experimental.
  * Link: [<code style="background: transparent;">pdf_tools</code>](lib_utils/pdf_tools.md)

* **Code Tools**

  * Utilities for reading, analyzing, and interpreting source code files.
  * *Status:* In progress.
  * Link: [<code style="background: transparent;">code_tools</code>](lib_utils/code_tools.md)

* **cURL Tools**

  * Utilities for parsing and interpreting `curl` commands into structured protocol calls.
  * *Status:* In progress.
  * Link: [<code style="background: transparent;">curl_tools</code>](lib_utils/curl_tools.md)

* **LLM Guardrails**

  * Cost control and safety utilities for managing LLM usage and execution constraints.
  * *Status:* Experimental.
  * Link: [<code style="background: transparent;">llm_guardrails</code>](lib_utils/llm_guardrails.md)

* **Crypto Utils**

  * Cryptographic helpers for signing, verification, and secure protocol interactions.
  * *Status:* Experimental.
  * Link: [<code style="background: transparent;">crypto_utils</code>](lib_utils/crypto_utils.md)


<p align="center">
  <a href="../guide_app/features/launch_server.md">&laquo; Previous: Launch a Server (Desktop App)</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="sdk_doc/index.md">Next: Core SDK &raquo;</a>
</p>
