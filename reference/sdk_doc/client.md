# <code style="background: transparent;">Summoner<b>.client</b></code>

Decorator-based, async client runtime for Summoner. It handles connection lifecycle, payload hooks, **receivers** (inbound), **senders** (outbound), optional **flow-aware** routing/state, and **DNA** export for cloning/merging agents.

## Modules

- [<code style="background: transparent;">Summoner<b>.client.client</b></code>](./client/client.md) — Core client runtime: decorators (`@receive`, `@send`, `@hook`, `@upload_states`, `@download_states`), run/retry lifecycle, flow integration, batching & back-pressure.
- [<code style="background: transparent;">Summoner<b>.client.merger</b></code>](./client/merger.md) — Composition utilities:
  - `ClientMerger` to **merge** multiple clients into one.
  - `ClientTranslation` to **rebuild** a client from its DNA (`SummonerClient.dna()`).

## Pick the right entry

| You want to… | Go to |
|---|---|
| Register handlers to receive/send messages | `client.client` |
| Validate/transform payloads before recv/send | `client.client` → `@hook` |
| Use flow-aware routing (Nodes/Routes/Triggers) | `client.client` + `protocol.*` |
| Export the client's handlers as DNA | `client.client#dna()` |
| Merge several clients into a single one | `client.merger#ClientMerger` |
| Reconstruct a client from saved DNA | `client.merger#ClientTranslation` |

## 60-second quick start

```python
from summoner.client.client import SummonerClient
from summoner.protocol.flow import Flow
from summoner.protocol.triggers import Move

client = SummonerClient("demo")
client.flow().activate()
client.flow().add_arrow_style('-', ('[', ']'), ',', '>')

@client.receive("A --[ greet ]--> B", priority=1)
async def on_greet(payload):
    Trigger = client.flow().triggers(text="OK\n  minor")
    return Move(Trigger.minor)  # enables reactive senders

@client.send("A --[ greet ]--> B", on_actions={Move})
async def reply():
    return {"ok": True}

client.run(config_dict={"logger": {"level": "INFO"}})
```

## Capabilities at a glance

* Async **I/O loops** with concurrency control and back-pressure.
* **Flow-aware** batching: state tape upload/download, route normalization, reactive senders.
* **Hooks** for inbound/outbound payload validation/tranform with ordered priorities.
* Robust **retry** (primary → fallback), graceful shutdown, and **travel/quit** intents.
* **DNA** capture and **merge/translate** utilities for agent portability.


<p align="center">
  <a href="../index.md">&laquo; Previous: Core API (Intro) </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="server.md">Next: <code style="background: transparent;">Summoner<b>.server</b></code> &raquo;</a>
</p>