# <code style="background: transparent;">Summoner<b>.client</b></code>

The **client** layer is the decorator-based async runtime used to build agents. It manages connection lifecycle, inbound/outbound handlers, optional flow-aware routing (routes, tape, reactive senders), and DNA export for portability (clone, merge, translate).

Most users only need `SummonerClient`. Use `merger` when you want to compose multiple agents or rebuild agents from DNA.

## Modules

* [<code style="background: transparent;">Summoner<b>.client.client</b></code>](client/client.md) → Core runtime built around `SummonerClient`: use decorators (`@receive`, `@send`, `@hook`, `@upload_states`, `@download_states`), run the client with automatic retries, enable flow-aware routing, and export DNA for portability.


* [<code style="background: transparent;">Summoner<b>.client</b></code> configuration guide](client/configs.md) → How to tune `SummonerClient.run(...)`, including connection target precedence (`host`/`port`), reconnection policy, receiver limits, sender concurrency/backpressure, and logging.

* [<code style="background: transparent;">Summoner<b>.client.merger</b></code>](client/merger.md) → DNA composition utilities:

  * `ClientMerger`: merge handlers from multiple sources (clients or DNA) into one composite client.
  * `ClientTranslation`: reconstruct a fresh client from a DNA list.

## Pick the right module

| You want to…                                                                    | Go to                                    |
| ------------------------------------------------------------------------------- | ---------------------------------------- |
| Register inbound/outbound handlers (`@receive`, `@send`)                        | `client.client`                          |
| Validate/transform payloads before/after network I/O                            | `client.client` → `@hook`                |
| Configure connection, retries, concurrency, backpressure, or logging            | configuration guide                       |
| Use flow-aware routing (route parsing, tape-driven receivers, reactive senders) | `client.client` + `protocol.*`           |
| Export a client as DNA                                                          | `client.client` → `SummonerClient.dna()` |
| Merge several agents into one process                                           | `client.merger` → `ClientMerger`         |
| Rebuild a client from saved DNA                                                 | `client.merger` → `ClientTranslation`    |

## Capabilities at a glance

* **Async handler runtime**: receivers (inbound), senders (outbound), hooks (pre/post processing).
* **Flow-aware routing**: parse routes into `ParsedRoute`, maintain a `StateTape`, and trigger reactive senders from returned events.
* **Hooks with ordering**: structured interception on send/receive paths (priority tuples).
* **Lifecycle management**: reconnect strategy, graceful shutdown, travel/quit intents.
* **Portability**: `dna()` capture plus merge/translate utilities for cloning or composing agents.

## Quick start in one file

This shows the minimal pattern: configure flow parsing, register a receiver, register a reactive sender, then run.

```python
from summoner.client.client import SummonerClient
from summoner.protocol.triggers import load_triggers, Move

client = SummonerClient("demo")

# 1) Flow is optional, but required if you use arrow routes in handler decorators
flow = client.flow().activate()
flow.add_arrow_style(stem="-", brackets=("[", "]"), separator=",", tip=">")
flow.compile_arrow_patterns()

# 2) Triggers (Flow.triggers() does not take `text=...`; use load_triggers for that)
Trigger = load_triggers(text="""
OK
  minor
""")

# 3) Receiver: return an Event to drive flow-aware senders
@client.receive("A --[ greet ]--> B", priority=(1,))
async def on_greet(payload):  # payload is str|dict depending on your transport
    return Move(Trigger.minor)

# 4) Sender: fires when the matching action/signal occurs
@client.send("A --[ greet ]--> B", on_actions={Move})
async def reply():
    return {"ok": True}

client.run(config_dict={"logger": {"level": "INFO"}})
```

> [!TIP]
> Arrow routes in decorators (for example `A --[ x ]--> B`) require an `ArrowStyle` registered on the client’s `Flow`. If route parsing looks wrong while debugging, call `flow.compile_arrow_patterns()` to rebuild the internal patterns.

<p align="center">
  <a href="./index.md">&laquo; Previous: Core SDK (Intro)</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="server.md">Next: <code style="background: transparent;">Summoner<b>.server</b></code> &raquo;</a>
</p>
