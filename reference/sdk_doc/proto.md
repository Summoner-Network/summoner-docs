# <code style="background: transparent;">Summoner<b>.protocol</b></code>

The **protocol** layer defines how messages, routes, and state transitions are expressed and processed. It's the glue between user code (client/server) and the routing model (signals, events, nodes, and arrows).

## Modules

- [<code style="background: transparent;">Summoner<b>.protocol.triggers</b></code>](./proto/triggers.md) — Build the `Trigger` class from a `TRIGGERS` spec; define `Signal`, `Event`, `Move/Stay/Test`, `Action`, and `extract_signal`.
- [<code style="background: transparent;">Summoner<b>.protocol.process</b></code>](./proto/process.md) — Core types used at runtime: `Node`, `ArrowStyle`, `ParsedRoute`, `Receiver`, `Sender`, `StateTape`, priorities, and activations.
- [<code style="background: transparent;">Summoner<b>.protocol.flow</b></code>](./proto/flow.md) — Parser + normalizer that turns human-readable routes into `ParsedRoute` objects; loads triggers; configures arrow styles.

## Pick the right module

| You want to… | Go to |
|---|---|
| Define a signal hierarchy and compare signals (`OK > acceptable`) | `triggers` |
| Express gates like `/all`, `/not(A,B)`, `/oneof(X,Y)` and test acceptance | `process#Node` |
| Configure arrow syntax (e.g., `--[ ]-->`, `=={ }==)`) and parse routes | `flow` |
| Batch receivers by priority and collect activations into a tape | `process#StateTape` |
| Filter senders by action type or signal | `process#Sender` |

## Quick start

```python
from summoner.protocol.flow import Flow
from summoner.protocol.triggers import Move, Action, extract_signal
from summoner.protocol.process import Receiver, StateTape

# 1) Configure the parser and triggers
flow = Flow().activate()
flow.add_arrow_style(stem='-', brackets=('[', ']'), separator=',', tip='>')
flow.add_arrow_style(stem='=', brackets=('{', '}'), separator=';', tip=')')
Trigger = flow.triggers(text="""
OK
  acceptable
  all_good
error
  minor
  major
""")
flow.ready()

# 2) Parse a route (normalized string form works as a stable key)
r = flow.parse_route("A, C --[ f, g ]--> B, K")
assert str(r) == "A,C--[f,g]-->B,K"

# 3) Register a receiver and collect activations from a tape of states
async def rcvr(payload):  # returns an Event or None
    return Move(Trigger.minor)

receiver_index = {str(r): Receiver(fn=rcvr, priority=(1,))}
parsed_routes  = {str(r): r}
tape = StateTape({"k0": ["A"]})
activations_by_prio = tape.collect_activations(receiver_index, parsed_routes)
````

> **Tip:** `str(ParsedRoute)` is a canonical, whitespace-free form — use it as the map key across your indices.

## Route grammar (cheat sheet)

* **Object(s):** `X`, `A, C, D`, `/all`
* **Unlabeled arrow:** `A -->> B` (with `-` stem and `>` tip → rendered as `A--[]-->B`)
* **Labeled arrow:** `A --[ f, g ]--> B, K`
* **Dangling left (no source):** `=={ f }==) Y`
* **Dangling right (no target):** `E =={ t }==)`
* **Tokens:** plain `A`, or with leading `/`: `/all`, `/not(E,F)`, `/oneof(R,S)`

Invalid tokens raise: `ValueError: Invalid token 'inv&alid' in route 'A --> inv&alid'`.

## Key types at a glance

| Type                               | Purpose                                                                 |
| ---------------------------------- | ----------------------------------------------------------------------- |
| `Signal`                           | Comparable, ordered by ancestry in the trigger tree.                    |
| `Event` / `Move` / `Stay` / `Test` | Event wrappers around a `Signal`.                                       |
| `Node`                             | Gate/state token (`all`, `plain`, `not`, `oneof`); supports `accepts`.  |
| `ArrowStyle`                       | Defines arrow parts (stem/brackets/separator/tip).                      |
| `ParsedRoute`                      | Canonical parsed route with `has_label`, `is_arrow`, `activated_nodes`. |
| `Receiver` / `Sender`              | Async handlers; sender filters by action class and/or signal.           |
| `StateTape`                        | Normalizes state shapes, batches activations by priority.               |

## Common errors

* **Triggers:** invalid/duplicate names, inconsistent indentation, or reserved names → `ValueError`.
* **Flow:** invalid token per `_TOKEN_RE` → `ValueError` with offending token and full route.
* **Node:** malformed token → `ValueError`.

<p align="center">
  <a href="server.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.server</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../lib_agent/index.md">Next: Agent Libraries &raquo;</a>
</p>
