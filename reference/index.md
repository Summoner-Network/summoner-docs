# SDK Reference

> [!CAUTION]
> This reference is still being refined as naming and semantics settle. The Core SDK is usable for day-to-day development, but some sections may change as we finalize stability guarantees. For walkthroughs and end-to-end examples, see the **[Summoner SDK Guides](../guide_sdk/index.md)**.

## [Core SDK](sdk_doc/index.md)

The Core SDK provides the runtime building blocks for agents: the client runtime, the relay server, and the protocol primitives.

* [<code style="background: transparent;">Summoner<b>.client</b></code>](sdk_doc/client.md) → Use `SummonerClient` to build a networked agent with a decorator model: register **receive**, **send**, and **hook** handlers, optionally enable flow-aware routing, and export/merge the agent's DNA for portability.

* [<code style="background: transparent;">Summoner<b>.server</b></code>](sdk_doc/server.md) → Use `SummonerServer` to run the TCP relay that clients connect to, either with a Python (**asyncio**) backend or a Rust (**Tokio**) backend, with backpressure, rate limiting, and quarantine controls for reliability under load.

* [<code style="background: transparent;">Summoner<b>.protocol</b></code>](sdk_doc/proto.md) → Use the protocol primitives behind flow-aware routing: define trigger trees, parse routes into typed structures, and use state tapes so agent interactions can be structured, debuggable, and replayable.


## [Agent Extensions](lib_agent/index.md)

Client-level extensions that augment the Core SDK runtime with additional orchestration, memory, and security capabilities. These are official enhancements to the core protocol, designed for advanced agent communication and execution patterns.

* **Aurora**

  * Extends the `SummonerClient` with keyed orchestration, Aurora-aware merger APIs, and a dedicated identity API.
  * *Status:* Stable (`1.0.0`).
  * Link: [<code style="background: transparent;">Summoner<b>.aurora</b></code>](lib_agent/aurora.md)


## [Utility Extensions](lib_utils/index.md)

Protocol-level utilities that provide optional tools, helpers, and operational safeguards for agents. These extensions add capabilities without modifying the core runtime.

* **Visionary**

  * Visualization and state introspection tools for agent graphs and execution flow.
  * *Status:* Stable.
  * Link: [<code style="background: transparent;">visionary</code>](lib_utils/visionary.md)

* **cURL Tools**

  * Utilities for parsing and interpreting `curl` commands into structured protocol calls.
  * *Status:* In progress.
  * Link: [<code style="background: transparent;">curl_tools</code>](lib_utils/curl_tools.md)

* **LLM Guardrails**

  * Cost control and safety utilities for managing LLM usage and execution constraints.
  * *Status:* Experimental.
  * Link: [<code style="background: transparent;">gpt_guardrails</code>](lib_utils/gpt_guardrails.md)


<p align="center">
  <a href="../guide_app/features/launch_server.md">&laquo; Previous: Launch a Server (Desktop App)</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="sdk_doc/index.md">Next: Core SDK &raquo;</a>
</p>
