# SDK Reference

> [!CAUTION]
> This reference is still being refined as naming and semantics settle. The Core SDK is usable for day-to-day development, but some sections may change as we finalize stability guarantees. For walkthroughs and end-to-end examples, see the **[Summoner SDK Guides](../guide_sdk/index.md)**.

## Core SDK

The Core SDK provides the runtime building blocks for agents: the client runtime, the relay server, and the protocol primitives.

* [<code style="background: transparent;">Summoner<b>.client</b></code>](sdk_doc/client.md) → Use `SummonerClient` to build a networked agent with a decorator model: register **receive**, **send**, and **hook** handlers, optionally enable flow-aware routing, and export/merge the agent’s DNA for portability.

* [<code style="background: transparent;">Summoner<b>.server</b></code>](sdk_doc/server.md) → Use `SummonerServer` to run the TCP relay that clients connect to, either with a Python (**asyncio**) backend or a Rust (**Tokio**) backend, with backpressure, rate limiting, and quarantine controls for reliability under load.

* [<code style="background: transparent;">Summoner<b>.protocol</b></code>](sdk_doc/proto.md) → Use the protocol primitives behind flow-aware routing: define trigger trees, parse routes into typed structures, and use state tapes so agent interactions can be structured, debuggable, and replayable.


## Agent Libraries

Additional agent-level libraries will layer orchestration, memory, and tool integrations on top of the Core SDK.

* **Aurora** (planned)
  - High-level patterns for orchestration, memory, and tools.
  - *Status:* Not yet available. This page will go live when Aurora ships.
  - Link: [Aurora update](./lib_agent/aurora.md)

## Protocol Libraries

Protocol-level extensions are defined but not actively developed at this time.

* **Smart tools** (paused)
  - Protocol-level tool calling and schema contracts.
  - *Status:* Paused. The page remains as a placeholder.
  - Link: [Smart tools](./lib_proto/smart_tools.md)


<p align="center">
  <a href="../guide_app/features/launch_server.md">&laquo; Previous: Launch a Server (Desktop App)</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="sdk_doc/index.md">Next: Core SDK &raquo;</a>
</p>
