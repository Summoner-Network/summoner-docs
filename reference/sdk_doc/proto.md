# <code style="background: transparent;">Summoner<b>.protocol</b></code>

The **protocol** layer defines the runtime primitives behind routing and state transitions: **signals**, **events**, **routes**, and the **state tape**. Most users touch it indirectly through `SummonerClient`, but it is useful when debugging flows or building tools around DNA/routes.

## Modules

* [<code style="background: transparent;">Summoner<b>.protocol.triggers</b></code>](./proto/triggers.md) → Load a trigger tree into a dynamic `Trigger` class, and work with `Signal`, `Event` (`Move/Stay/Test`), `Action`, and `extract_signal`.

* [<code style="background: transparent;">Summoner<b>.protocol.process</b></code>](./proto/process.md) → Runtime types used during routing: `Node`, `ArrowStyle`, `ParsedRoute`, `Receiver`, `Sender`, `StateTape`, and activation collection.

* [<code style="background: transparent;">Summoner<b>.protocol.flow</b></code>](./proto/flow.md) → Parse human route strings into `ParsedRoute` objects using configured `ArrowStyle`s.

## Pick the right module

| You want to…                                                         | Go to                   |
| -------------------------------------------------------------------- | ----------------------- |
| Define and compare signals by ancestry (parent > child)              | `triggers`              |
| Use gates like `/all`, `/not(x,y)`, `/oneof(a,b)` and check matching | `process` → `Node`      |
| Configure arrow syntax and parse routes into `ParsedRoute`           | `flow`                  |
| Collect receiver activations from a tape (by priority)               | `process` → `StateTape` |
| Filter senders by action type and/or signal                          | `process` → `Sender`    |

## Key types at a glance

| Type                               | Purpose                                                                             |
| ---------------------------------- | ----------------------------------------------------------------------------------- |
| `Signal`                           | Comparable signals ordered by ancestry (ancestor compares greater than descendant). |
| `Event` / `Move` / `Stay` / `Test` | Events wrapping a signal used to drive transitions.                                 |
| `Node`                             | Gate/state token. Supports `accepts(state: Node) -> bool`.                          |
| `ArrowStyle`                       | Defines the arrow syntax used by the flow parser.                                   |
| `ParsedRoute`                      | Parsed route with `is_arrow`, `has_label`, `activated_nodes(event)`.                |
| `Receiver` / `Sender`              | Async handlers; sender can filter on action types and/or signals.                   |
| `StateTape`                        | Normalizes state shapes and collects activations grouped by priority.               |

## Mental model

* **Signal** is a named point in a hierarchy (`Trigger.OK`, `Trigger.minor`).
* **Event** wraps a `Signal` (`Move(Trigger.minor)`, `Stay(Trigger.OK)`, `Test(Trigger.OK)`).
* **Route** is a string that parses into a `ParsedRoute(source, label, target, style)`.
* **Node** is the gate/token unit inside routes (`"A"`, `"/all"`, `"/not(x,y)"`, `"/oneof(a,b)"`).
* **StateTape** stores the active `Node` states and computes which receivers should fire.

## Quick start in one file

This shows the minimum useful subset: build triggers, parse a route, and collect receiver activations from a tape.

```python
from summoner.protocol.flow import Flow
from summoner.protocol.triggers import load_triggers, Move
from summoner.protocol.process import Receiver, StateTape

# 1) Configure a flow parser (arrow style is required for arrow routes)
flow = Flow().activate()
flow.add_arrow_style(stem="-", brackets=("[", "]"), separator=",", tip=">")
flow.compile_arrow_patterns()

# 2) Load triggers (Flow.triggers() does not accept `text=...`; use load_triggers for that)
Trigger = load_triggers(text="""
OK
  acceptable
  all_good
error
  minor
  major
""")

# 3) Parse a route
r = flow.parse_route("A, C --[ f, g ]--> B, K")
key = str(r)  # canonical, whitespace-free key
assert key == "A,C--[f,g]-->B,K"

# 4) Register a receiver and collect activations
async def rcvr(payload):  # -> Event | None
    return Move(Trigger.minor)

receiver_index = {key: Receiver(fn=rcvr, priority=(1,))}
parsed_routes  = {key: r}

tape = StateTape({"k0": ["A"]})
activations_by_prio = tape.collect_activations(receiver_index, parsed_routes)
```

> [!TIP]
> Use `str(route)` (where `route` is a `ParsedRoute`) as the normalized, whitespace-free key for route lookups and indices.

<p align="center">
  <a href="server.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.server</b></code></a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="../lib_agent/index.md">Next: Agent Libraries &raquo;</a>
</p>
