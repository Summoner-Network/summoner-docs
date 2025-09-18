# Summoner Agent Design Handbook

> A principle-based guide to designing robust agents with the Summoner SDK.

<p align="center">
  <img width="350px" src="../../assets/img/summoner_agent_design_rounded.png" />
</p>

This handbook is repository-agnostic. It explains principles first. When relevant, it includes **optional example links** to public implementations for reference only. Your own agents can live in any repository, provided each agent folder follows the `agent_<some_name>/agent.py` convention if you use the desktop app.

## The mental model: receive → transition → send

A Summoner agent is a small state machine that reacts to messages. You **receive** an input, **transition** local state, then **send** outputs when the new state requires it. Keep these steps explicit in code. Avoid hiding transitions in side effects. When a state change does not imply an outgoing message, record the change and return.

Practical implications:

* Keep handlers small. If you must update state **and** emit later, store what is needed and let a tick/hub sender emit. Do not call senders directly.
* Treat every handler as an interrupt: grab minimal context, validate, update, return.

## Skeleton of a production-ready agent

Keep each agent in a self-contained folder with a predictable entry point and clear dependencies. This simplifies local testing, CI, and discovery by tools.

```sh
agents/
  agent_<some_name>/
    agent.py           # entry point with a SummonerClient instance
    requirements.txt   # local deps for this agent only
    README.md          # what it does, how to run, scenarios
    configs/
      client_config.json   # optional runtime overrides per environment
      server_config.json   # optional test orchestration
    state/             # optional DB files or migrations
    utils.py           # optional helpers (pure functions preferred)
```

**Naming for desktop compatibility.** If you use the desktop app, name folders with the `agent_` prefix (for example, `agent_MyAgent`). The desktop scans `agents/agent_*` for launchable entries and expects `agent.py` and `requirements.txt` inside each agent folder.

**Entry point.** Your `agent.py` should expose a single `main()` that parses an optional `--config`, builds the client, wires handlers and hooks, **declares** `@upload_states` / `@download_states` (and initializes any in-memory variables those functions read), then calls `client.run(...)`. Keep CLI flags thin. Drive behavior from config so environments can change without code edits.

**Configuration practice.** Keep addresses, retry limits, timeouts, queue sizes, and logging settings in `configs/client_config.json`. The launch code should provide safe defaults but defer to the config file when present. Keep secrets out of the repo and load them at startup if the SDK supports it.

**Persistence.** If the agent needs durable state, place lightweight DB files under `state/` and use async drivers. Avoid synchronous file I/O in handlers. Centralize writes so that state is consistent even when the process restarts.

**Utilities.** Restrict `utils.py` to pure helpers (parse, validate, format). Side effects should live in well-named modules that you can mock in tests.

> **If you will use arrow-style flow routes later:** activate the flow, declare an arrow style, and call `flow.ready()` **before** any decorators that use arrow routes register. The dedicated [**State and flows**](#state-and-flows-explicit-automata-over-implicit-flags) section covers this in detail.

## Concurrency: cooperative I/O, bounded work

Summoner clients run on `asyncio` with non-blocking sockets. Handlers must `await` I/O and keep CPU work short. If a handler does CPU-heavy work that could block the loop, move it to a thread or process. Prefer queues and tasks over sleeps.

**Send and receive are concurrent.** Input and output progress independently. Treat them as decoupled loops that may observe state at slightly different times. Avoid races by coordinating through routes and flows rather than mutating shared state from both sides.

**Race-reduction patterns.**

* Keep `@receive` handlers small and mostly pure. Validate, normalize, and compute outcomes. Defer side effects.
* Commit state in one place per key. If you use the flows API, consolidate commits in `@download_states` and run post-effects via hub senders gated by actions/triggers.
* Use a single driver task per data domain (for example, a periodic retry sender) to serialize expensive or out-of-order work.

**Split send loops to tame races.** A practical pattern is to separate a periodic **tick sender** (maintenance like register, finalize retries, reconnect) from an **event-driven hub** (chatty steps tied to triggers/actions). This ensures receivers finish clearing or updating transient fields (like nonces) before new outbound payloads mint fresh values.

**Backpressure.** On the send side, rely on the writer's drain semantics (the SDK drains either per batch or per payload, depending on configuration). On the receive side, return quickly under surge and push heavier work to tasks or queues.

## Messaging primitives and idioms

The SDK gives you three surfaces: **receivers** (ingest & decide), **senders** (emit), and **hooks** (cross-cutting filters). Keep each surface small and predictable so you can layer flows on top cleanly.

**Receiving.** Use `@receive` for narrow, intention-revealing handlers. A receive handler is `async`, takes **exactly one** argument (the payload), and returns an `Event` (`Move`/`Stay`/`Test`) or `None`. Keep the body mostly pure: normalize, validate, and compute an outcome. Defer side effects to senders or to your download commit.

```python
from typing import Any, Optional

@client.receive(route="/msgs/text")
async def on_text(payload: Any) -> Optional["Event"]:
    user, text = parse_payload(payload)   # pure helper
    if not allow_peer(user):              # guard
        return None                       # drop quietly
    remember_last_text(user, text)        # your state store
    return None                           # (if flows are off, Events have no effect)
```

> If flows are **on**, route tokens must be valid **Node** names (plain tokens like `opened`, `locked`, plus reserved forms such as `/all`, `/oneof(...)`, `/not(...)`). Avoid embedding `/` in ordinary node names. Slash-prefixed forms are reserved by the DSL. If flows are **off**, route strings are just labels and match exactly.

**Sending.** Use `@send` for outbound paths. A send handler is `async`, takes **no arguments**, and **returns** either a single payload (str/dict) or, with `multi=True`, a **list** of payloads. Returning `None` means "stay quiet this tick." Never `yield`. Generators are not supported by the SDK.

```python
@client.send(route="/msgs/text", multi=True)
async def broadcast_text() -> list[dict]:
    targets = get_targets()
    body = build_payload()
    return [{"to": t, **body} for t in targets]
```

**Hooks.** Use `@hook(Direction.RECEIVE|SEND)` for cross-cutting concerns: schema checks, replay drop, reputation, signing/encryption. A hook is `async`, accepts **one** payload, and returns a (possibly modified) payload or `None` to drop it. Keep hooks free of business logic. They should be small, deterministic filters. (You can order multiple hooks with the `priority` tuple. Lower tuples run earlier.)

```python
from summoner.protocol import Direction

@client.hook(direction=Direction.RECEIVE)
async def verify_signature(payload):
    if not isinstance(payload, dict):
        return None
    return payload if has_valid_signature(payload) else None
```

Idioms that repeat across agents:

* Prefer `return None` over sending empty frames. Silence is a valid outcome.
* Put addressing in **payload fields**, not in route strings (routes describe behavior, not recipients).
* Keep parse/validate/format helpers **pure** so they are easy to test and reuse.

## State and flows: explicit automata over implicit flags

<p align="center">
  <img width="280px" src="../../assets/img/fundamentals_orchest_rounded.png" />
</p>


A flow turns your agent into a small, explicit automaton. Instead of sprinkling boolean flags, you **name nodes** and write **arrow routes** that say who runs when. Receivers **propose** moves or stays. A single consolidation point **commits** the winning node. This keeps behavior visible, debuggable, and safe to extend.

### Step 0: Minimal setup (do this *before* any arrow-route decorators register)

This flips on the flow engine and defines the arrow syntax so your route strings become a real DSL (nodes, labels, transitions). It then compiles the patterns and loads your **Trigger** tokens. If you skip this before registering `@receive/@send` with arrows, those routes will be treated as plain labels and will not participate in state-based routing or hub matching.

```python
from summoner.protocol import Move, Stay, Node
from summoner.client import SummonerClient

client = SummonerClient(name="Agent")

flow = client.flow().activate()
flow.add_arrow_style(stem="-", brackets=("[", "]"), separator=",", tip=">")
flow.ready()
Trigger = flow.triggers()  # e.g., Trigger.ok, Trigger.error

# ... then register any @receive / @send that use arrows ...
```

> [!NOTE]
> When flows are on, node tokens must be valid names, alphanumeric or underscore, or reserved forms like `/all`, `/oneof(...)`, `/not(...)`.

### Step 1: Upload/Download — the shape-preserving contract

Think of `@upload_states` as your agent's **self-report** and `@download_states` as the **commit point**. On each tick (with flows active), the runtime:

1. calls **upload** to learn where you are (a node, a list, or a per-key map).
2. runs receivers whose **source** gates accept that upload, collecting their returned `Event`s.
3. computes the **possible next nodes**, preserving your upload's shape.
4. calls **download** once with those proposals so *you* choose what to commit.

The mapping is shape-preserving:

* `"node"` → `list[Node]`
* `["n1","n2"]` → `list[Node]`
* `{key: "node"}` → `{key: list[Node]}`
* `{key: ["n1","n2"]}` → `{key: list[Node]}`

Keep `download` small and deterministic: pick **one** winner per key (or keep the current one), do any durable writes, and return. Commit exactly **once per key**.

#### Single-key minimal example (prefer "exchange" over "ready")

```python
from typing import Any
from summoner.protocol import Node

current = "ready"

@client.upload_states()
async def upload(_: Any) -> str:
    return current  # report the current gate

@client.download_states()
async def commit(candidates: list[Node]) -> None:
    global current
    current = "exchange" if Node("exchange") in candidates else "ready"
```

#### Per-key example (per-peer lanes with a preference order)

```python
from typing import Any, Optional
from summoner.protocol import Node

# peer_id -> node; peers default to "ready"
slots: dict[str, str] = {}
PREFS = ["finalize", "exchange", "ready"]  # highest to lowest

@client.upload_states()
async def upload(_: Any) -> dict[str, str]:
    return {peer: slots.get(peer, "ready") for peer in slots.keys()}

@client.download_states()
async def commit(proposed: dict[Optional[str], list[Node]]) -> None:
    # proposed includes peer_id buckets. Left-dangling proposals may arrive under key=None
    for peer, options in proposed.items():
        if peer is None:
            # left-dangling bucket. Apply by policy if you use those routes
            continue
        names = {str(n) for n in options}
        slots[peer] = next((p for p in PREFS if p in names), slots.get(peer, "ready"))
```

> **Notes**
>
> • **Left-dangling routes** (e.g., `"--> boot"`) deliver proposals under `None` when your upload is a dict. Handle that bucket explicitly if you want it to affect a specific key.
> • Keep **upload** fast and side-effect-free. Do durable writes in **download** so you consolidate multiple receiver outcomes before committing.

### Step 2: Gate behavior with routes (state-gated receivers)

With flows active, routes become selectors. Only receivers whose **source** matches what you uploaded are eligible to run. Each receiver returns an `Event` (`Move`/`Stay`) that *proposes* the next node. **Download** commits the winner.

In this example, `on_confirm` proposes **`ready → exchange`** on a valid confirm. `on_exchange` proposes to **stay** in `exchange` for chatty messages. Another receiver would later propose **`exchange → finalize`**.

```python
from typing import Optional
from summoner.protocol import Move, Stay

# ... flow activated above ...

@client.receive(route="ready --> exchange")
async def on_confirm(payload) -> Optional["Event"]:
    if is_valid_confirm(payload):
        return Move(Trigger.ok)

@client.receive(route="exchange --> finalize")
async def on_exchange(payload) -> Optional["Event"]:
    if still_chatty(payload):
        return Stay(Trigger.ok)
```

### Advanced route shapes (when you need more than simple arrows)

* **Left-dangling** `--> target`: eligible on **every** inbound message (state-agnostic). Use it to bootstrap or "wake" a graph.
* **Right-dangling** `source -->`: eligible only while in `source`. Returning `Move(...)` **prunes** that lane (contributes no nodes).
* **Object routes** (no arrow) like `"opened,notify"` select by source only. They never propose a target.
* `"/all --> /all"` hubs match **any complete arrow** (labeled or unlabeled) but **not** object or dangling routes.

### Reactive hubs (send after specific outcomes)

> [!CAUTION]
> Hubs require flows to be **activated**. If flows are off, `on_actions` / `on_triggers` filters will not match anything.

Hubs are `@send` paths that fire **right after** matching receiver events:

* `on_actions` filters by event kind: `{Action.MOVE, Action.STAY, Action.TEST}`.
* `on_triggers` filters by **Trigger** values from `flow.triggers()`.
* A hub fires only when **both** filters (if provided) match.
* The runtime **deduplicates** hub firings once per tick by `(route, key, sender_fn)`, so you do not get duplicates for the same activation.

This lets you keep receivers pure (just propose outcomes) while doing side effects *after* the state decision is made.

## Composing behaviors

<p align="center">
  <img width="280px" src="../../assets/img/fundamentals_compose_rounded.png" />
</p>

You rarely ship a single, monolithic "behavior." Robust agents are **compositions**. You put transport-level guarantees (handshakes) *under* your domain decisions, and you put **gates** (explicit flow nodes and routes) *around* those decisions. The layers do not bleed into each other. Hooks harden the wire. Flows govern who may act and when. Business handlers stay thin. That clean separation is what keeps restarts, reconnections, and orchestration predictable.

### Building on top of handshakes

When peers are untrusted or links are flaky, put a **handshake layer** *under* your domain logic. The point is to stabilize transport-level invariants first (liveness, identity, replay safety), then run business flows on top. Practically, you validate on the way **in** (hooks), record minimal state, and only after the echo or signature checks succeed do you let domain receivers fire.

Start simple with a **nonce echo** (prove freshness and drop replays). Where integrity matters, move to **DID-based identity** and signatures. Treat these as transport guarantees enforced in hooks, not sprinkled across business handlers. With a clean base, your buy/sell or chat flows become a thin **overlay**. Their states (offers, counters, acceptances) remain independent from the transport handshake (nonces, keys, references). This separation makes restarts and reconnection behavior predictable.

For complete, public illustrations of layered designs, see:

* [agents/agent_HSAgent_0](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_HSAgent_0): Nonce-echo handshake with finalize/reconnect and replay protection.
* [agents/agent_HSAgent_1](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_HSAgent_1): Handshake upgraded with DID signatures; identity verified in hooks.
* [agents/agent_HSBuyAgent_0](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_HSBuyAgent_0): Buyer negotiation overlay (offer/counter/accept) atop the handshake.
* [agents/agent_HSSellAgent_0](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_HSSellAgent_0): Seller negotiation overlay (quote/accept) atop the handshake.

> [!TIP]
> Small mental workflow representation:
>
> **echo → (optional) sign → overlay.**
>
> Keep the first two in hooks. Keep the overlay in routes and flows.

### Command gating your agent

Sometimes you want operators (or even other agents) to **control** an agent by sending commands. Ask it to **travel** to a different server, **quit** cleanly, **activate** a behavior (start a crawler, enable a buyer), or **stop/pause** it. Those controls are powerful, so they need guardrails. The clean pattern is **command = parse → ask permission (gate) → propose transition**. You enforce the gate with flow nodes (for example, `opened/locked` or `idle/active/paused`) so a stray or out-of-policy message cannot flip state.

Self-commands (local control like `client.quit()` / `client.travel_to(...)`) are always available. **Remote** commands must consult the current gate and log a short reason when closed. After a transition is proposed, your `@download_states` commits exactly once per key so other receivers and hubs route correctly on the next tick.

> [!NOTE]
> The snippet below assumes flows are **activated**, an arrow style is **declared**, `flow.ready()` has been called, and `Trigger = flow.triggers()` is loaded. `@receive` returns `Move/Stay` (or `None` to drop). The engine aggregates proposals and then calls your `@download_states` to commit.

```python
from typing import Optional
from summoner.protocol import Move

# Example gates: opened → closed and back
@client.receive(route="opened --> locked")
async def on_lock(payload) -> Optional["Event"]:
    if not allow_lock(payload):     # parse + gate check
        return None                 # drop quietly
    return Move(Trigger.ok)         # propose opened → locked

@client.receive(route="locked --> opened")
async def on_open(payload) -> Optional["Event"]:
    if not allow_open(payload):
        return None
    return Move(Trigger.ok)         # propose locked → opened
```

Common command families you can gate this way:

* **Liveness/placement:** `travel_to`, `quit`
* **Behavior toggles:** `start_<feature>`, `stop_<feature>`, `pause`, `resume`
* **Mode switches:** `idle ↔ active`, `read-only ↔ write-enabled`
* **Rate controls:** `set_rate`, `throttle`, `unthrottle`

#### Addressing, travel, and the control surface (concrete patterns)

Agents may switch servers at runtime and expose **self-commands** and **remote orders**. Treat location as state and gate remote orders via your flow. This is where the abstract "command gating" meets concrete methods (`quit()` / `travel_to(...)`) and careful routing so registrations do not collide.

> [!NOTE]
> If you use arrow routes anywhere (e.g., `/all --> /all`), be sure you have **activated flows** and declared an arrow style *before* decorator registration:
>
> ```python
> flow = client.flow().activate()
> flow.add_arrow_style(stem="-", brackets=("[", "]"), separator=",", tip=">")
> flow.ready()
> Trigger = flow.triggers()
> ```

**Local self-commands (no wire)**
Use distinct routes to avoid accidental registration overlap and to keep intent clear (Note: the SDK **does** allow multiple senders on the same route). These senders take **no arguments** and return `None`. They call the SDK's async control methods directly.

```python
# Quit the client gracefully
@client.send(route="control.self.quit")
async def self_quit():
    await client.quit()    # sets intent; session exits cleanly
    return None            # nothing is sent on the wire

# Travel to a new server (host, port)
@client.send(route="control.self.travel")
async def self_travel():
    await client.travel_to(host="127.0.0.2", port=9999)  # sets travel intent
    return None
```

**Behavior.** Both methods are `async` and thread-safe. They set internal intent flags. The current session shuts down **cleanly** at the next safe point. On `client.travel_to(host, port)`, the client reconnects to the new `(host, port)` and resumes. On `client.quit()`, the client exits after cleanup.

**Remote orders (receive then act)**
If you accept orders over the wire, validate and then call the methods. Keep the control API uniform across agents so orchestration tools can script them.

```python
from summoner.protocol import Stay

@client.receive(route="home --> work")
async def on_remote_order(payload):
    content = payload.get("content", {}) if isinstance(payload, dict) else {}
    if content.get("intent") == "self.travel":
        await client.travel_to(content.get("host"), int(content.get("port", 0)))
        return Stay(Trigger.ok)  # no graph change required
    if content.get("intent") == "self.quit":
        await client.quit()
        return Stay(Trigger.ok)
```

**Reference example.** Orders over the wire (like `/travel` and `/quit`) are demonstrated in [agents/agent_ChatAgent_1](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_ChatAgent_1).

For public agent implementations that demonstrate gated commands and control surfaces, see:

* [agents/agent_ChatAgent_1](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_ChatAgent_1): remote orders like `/travel` and `/quit` over the wire.
* [agents/agent_ChatAgent_2](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_ChatAgent_2): activates automaton routing via `@upload_states` to gate commands (`opened/locked`).
* [agents/agent_ChatAgent_3](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_ChatAgent_3): explicit transitions with `Move/Stay`; remote/self `travel` and `quit`; lock/open gates.

## Orchestration Principles

### Asynchronous programming in Summoner

Summoner runs on `asyncio`, and each client owns its own event loop. Treat your agent as a cooperative, non-blocking participant in that loop. Await I/O, keep CPU work short, and do setup/teardown on the same loop so ownership is clear.

* **One loop per client.** The SDK creates a fresh event loop per `SummonerClient` and sets it for the current thread. If you need multiple clients, give each its **own thread or process** so loops do not clash.
* **No blocking in handlers.** Avoid `time.sleep` and tight CPU loops. Always `await` I/O and offload heavy CPU elsewhere.
* **Setup/teardown.** Run pre-run async setup on the client's loop (for example, `client.loop.run_until_complete(setup())`) **before** `client.run(...)`. Close files, DBs, and tasks after `run(...)` returns.
* **Task management.** Schedule background tasks on the client's loop. The SDK will cancel worker pools and active tasks cleanly on shutdown.
* **Signal handling.** On non-Windows, SIGINT/SIGTERM handlers are installed for graceful termination.

### Configuration & runtime defaults

Configuration lives in JSON and drives the runtime. Treat it as the single source of truth for limits and addresses so code stays stable across environments.

* **Receiver:**

  * `max_bytes_per_line=65536` (64 KiB),
  * `read_timeout_seconds=None` (block until data).

* **Sender:**

  * `concurrency_limit=50` (default),
  * `batch_drain=True` by default,
  * `queue_maxsize=concurrency_limit`,
  * `event_bridge_maxsize=1000`,
  * `max_worker_errors=3`.

* **Reconnection:**

  * `retry_delay_seconds=3`,
  * `primary_retry_limit=3`,
  * `default_retry_limit=2`,
  * plus optional `default_host`/`default_port` for failover.

* **Precedence:** If the config provides `host`/`port`, those populate `self.host`/`self.port` and **override** the `run(...)` host/port at connection time.

The sender warns when the queue is about to exceed **80%** capacity. Take that as your cue to slow producers, increase capacity, or batch more aggressively.

### Validation, reputation, and replay safety

Treat every inbound frame as untrusted until proven otherwise. Run a short, deterministic validation chain **before** any state change so downstream code never sees malformed input.

* **Schema and type checks** for every field you will read later.
* **Replay drop**, using a nonce or timestamp window. Keep a small in-memory LRU for fast paths. Persist when you need durability across restarts.
* **Allowance/ban lists** keyed by peer identity with stable reason strings in logs.

On the outbound side, centralize signing and (optional) encryption in a single helper so business handlers never juggle keys. Cache reads to avoid I/O in hot paths and fail closed when credentials are missing.

For public agent implementations that illustrate validation hooks, replay handling, and basic reputation/ban mechanics, see:

* [agents/agent_RecvAgent_1](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_RecvAgent_1): Early drop of bad frames with clear deny reasons.
* [agents/agent_RecvAgent_2](https://github.com/Summoner-Network/summoner-agents/blob/main/agents/agent_RecvAgent_2): Adds reputation and ban outcomes to the same path.
* [agents/agent_EchoAgent_2](https://github.com/Summoner-Network/summoner-agents/blob/main/agents/agent_EchoAgent_2): Validates on ingress and enforces signed egress for end-to-end policy.


### Queues, batching, and delayed work

Queues are your shock absorbers. Use them to decouple hot receive paths from heavier aggregation or fan-out, and to shape bursty workloads into predictable sends.

* **Batch and summarize.** Collect items for *N* seconds, emit one consolidated report.
* **Fan-out with backpressure.** Enqueue jobs and let a single sender task respect `multi=True` semantics and queue limits.

Create queues at startup, own them on the agent object, and provide a `close()` that signals consumers, drains gently, and exits cleanly.

For public agent implementations that apply queue-backed send/receive and state-gated flows, see:

* [agents/agent_EchoAgent_0](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_EchoAgent_0): Decouples receive from send with a small queue.
* [agents/agent_EchoAgent_1](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_EchoAgent_1): Introduces lightweight shaping before queuing to smooth bursts.
* [agents/agent_EchoAgent_2](https://github.com/Summoner-Network/summoner-agents/tree/main/agents/agent_EchoAgent_2): Reuses the queue pattern with policy checks on both sides.
* [agents/agent_ChatAgent_2](https://github.com/Summoner-Network/summoner-agents/blob/main/agents/agent_ChatAgent_2): Queues remote commands behind simple state gates.
* [agents/agent_ChatAgent_3](https://github.com/Summoner-Network/summoner-agents/blob/main/agents/agent_ChatAgent_3): Tightens state transitions to control when queued work may run.

### Backpressure and rate limiting

Assume the network can stall. Your job is to stay responsive: return quickly on receive, let the writer's drain and the send queue enforce backpressure, and keep optional rate limits in config so you can tune without redeploying.

Test under synthetic load. Verify that:

* the writer is awaited (no busy loops),
* the send queue warning triggers at \~80% capacity,
* drops/backoffs are visible in logs with counts for sent, retried, and dropped frames.

## Best Practices

<p align="center">
  <img width="280px" src="../../assets/img/fundamentals_best_practices_rounded.png" />
</p>

A reliable agent is easy to **observe**, designed to **withstand failures**, avoids **known foot-guns**, and **scales** without changing its core rhythm. This section ties those threads together.

### Observability and logs

Log one event per line with structured fields so `tail -f` stays actionable. Include timestamp, route, peer, state gate, decision, and a short reason. Avoid multiline payload dumps. Prefer `debug` for payloads, `info` for decisions, `warning` for drops, and `error` for crashes. Make sampling and rotation adjustable via config so noisy environments do not drown your signal.

### Robustness checklist

* [ ] Handlers are idempotent and safe to retry. Design for dropped/late messages and restarts.
* [ ] Input is validated and normalized before use. Bad frames drop with a clear reason.
* [ ] Output is throttled. No busy loops. Backpressure is respected.
* [ ] Automaton gates sensitive commands. Upload/download keep state consistent.
* [ ] Handshake completes before domain flows. Cryptography is centralized.
* [ ] Queues are bounded. Producers drop or back off when full.
* [ ] Shutdown drains queues, cancels tasks, and persists last known state.
* [ ] Durable state is committed in one place per key. Send/receive do not race it.
* [ ] Reconnection paths are explicit. Retry windows tuned. Failovers verified in logs.

### What to avoid

* Giant handlers that parse, validate, decide, and emit in one place.
* Hidden async work in property getters or `__init__`.
* Global mutable state shared across handlers. Make state explicit on the client.
* Logs that omit the decision or the reason for a drop.
* Sprinkling cryptography across the code. Keep it centralized.

### Extending the design

As agents grow, keep the same discipline. Promote pure helpers and dataclasses into small modules. Keep the runtime surface thin: decorators for routes and hooks, plus a client that knows how to run, travel, and upload states. Everything else remains ordinary Python you can test in isolation.

## Appendix: Startup blueprint

```python
import argparse
from summoner.client import SummonerClient

client = SummonerClient(name="Agent")

# Optional: activate flows BEFORE registering any arrow routes
flow = client.flow().activate()
flow.add_arrow_style(stem="-", brackets=("[", "]"), separator=",", tip=">")
flow.ready()
Trigger = flow.triggers()

# --- register hooks/receive/send/upload/download here ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config_path", required=False)
    args = parser.parse_args()
    # pre-run setup, if any:
    # client.loop.run_until_complete(setup())
    client.run(host="127.0.0.1", port=8888,
               config_path=args.config_path or "configs/client_config.json")
```

This blueprint makes startup explicit. It sets the initial state and defers all long-running work to tasks that you cancel at shutdown.

> [!NOTE]
> The SDK creates/configures the logger internally from `client_config.json`. Do not pass a logger to the constructor.

<p align="center">
  <a href="client_agent.md">&laquo; Previous: Clients and Agents </a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="../howtos/index.md">Next: "How-to" tutorials &raquo;</a>
</p>
