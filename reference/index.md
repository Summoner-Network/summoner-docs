# API Reference

> [!CAUTION]
> **Status and scope**
> This API reference is under active development. Sections will evolve as the SDK matures and as we finalize naming, semantics, and stability guarantees. For additional guidance, conceptual explanations, comprehensive walkthroughs, and end-to-end examples, see the **[Summoner SDK Guides](../guide_sdk/index.md)**.

## Core API

The Core API is stable enough for day-to-day development. It covers agent construction, transport, and protocol semantics.

* [<code style="background: transparent;">Summoner<b>.client</b></code>](sdk_doc/client.md)
  Build networked agents using a concise decorator model. Define **receive**, **send**, and **hook** behaviors; export and merge agent DNA; use flow-aware routing for structured interactions.

* [<code style="background: transparent;">Summoner<b>.server</b></code>](sdk_doc/server.md)
  Run a TCP relay with Python (**asyncio**) or Rust (**Tokio**) backends. Includes backpressure, rate limiting, and quarantine controls for reliability in production settings.

* [<code style="background: transparent;">Summoner<b>.protocol</b></code>](sdk_doc/proto.md)
  Work with trigger trees, flow parsing, typed routes, and state tapes to coordinate agent conversations with explicit structure and replayable state.

## Agent Libraries

Additional agent-level libraries will layer orchestration, memory, and tool integrations on top of the Core API.

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

---

<p align="center">
  <a href="../guide_app/features/launch_server.md">&laquo; Previous: Launch a Server (Desktop App)</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="sdk_doc/index.md">Next: Core API &raquo;</a>
</p>
