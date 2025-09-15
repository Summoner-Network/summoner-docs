# Agent behaviour as Flows


NOTE: refer to the agent library if needed

This section needs to use code to illustrate the following statements:

Contrary to agent without flows, here we need ot talk about the semantic hidden in the route and how they communicate with triggers or actions.

- Finite state machines 
- Category theory
- Higher structures

----------

# Agent behaviour as Flows

> Learn how Summoner expresses agent logic as explicit flows, where routes encode state transitions, triggers, and actions.

**Purpose & audience**  
- **Who:** developers who want to structure complex agent protocols clearly  
- **What:**  
  1. How routes capture finite-state machines (FSM)  
  2. How flow composition reflects category-inspired patterns  
  3. How higher-order abstractions enable parallel, reusable behaviors  
- **Outcome:** a set of code examples you can adapt to model reliable, maintainable agent logic

---

## 1. Flows vs Stateless Agents

A stateless agent reacts to messages with ad-hoc logic. Flows instead declare **states** and **transitions**:

```python
# Stateless echo agent
class EchoAgent(Agent):
    async def on_message(self, msg):
        await self.send(msg)
````

In a flow-based agent, each route represents an edge in a state graph:

```python
@agent.receive(route="idle → echoing")
async def handle_echo(self, msg):
    await self.send(msg)
```

Here, the route `"idle → echoing"` labels the transition from `idle` to `echoing`. Summoner ensures that only messages matching this transition invoke the handler.

---

## 2. Finite State Machines

Define an FSM by naming states and decorating handlers for each transition:

```python
from summoner import Agent, run_client

class OrderAgent(Agent):
    @Agent.receive(route="idle → ordering")
    async def start_order(self, msg):
        self.logger.info("Received order request")
        await self.send("confirming")

    @Agent.send(route="ordering → waiting")
    async def confirm_order(self):
        return {"status": "order confirmed"}

    @Agent.receive(route="waiting → completed")
    async def complete_order(self, msg):
        self.logger.info("Order completed, payload=%s", msg)
        await self.stop()

if __name__ == "__main__":
    run_client(OrderAgent)
```

* **States:** `idle`, `ordering`, `waiting`, `completed`
* **Transitions:** each decorated method handles one directed edge
* Summoner manages the underlying TCP loop and dispatch

---

## 3. Category-Inspired Composition

Routes act as **morphisms** connecting state objects. You can compose them by chaining transitions:

```python
class ComposeAgent(Agent):
    @Agent.receive(route="a → b")
    async def a_to_b(self, msg):
        await self.send(msg, route="b → c")

    @Agent.receive(route="b → c")
    async def b_to_c(self, msg):
        await self.send({"done": True})
```

* The first handler processes `"a → b"`, then sends on `"b → c"`.
* The second handler completes the flow.
* Composition reflects the law that `(a→b) ∘ (b→c) = (a→c)` in semantic effect.

---

## 4. Higher-Order Structures

### 4.1 Parallel Flows

Run multiple independent flows via background tasks:

```python
class ParallelAgent(Agent):
    def setup(self):
        self.loop.create_task(self._flow_one())
        self.loop.create_task(self._flow_two())

    async def _flow_one(self):
        await self.send("start", route="one → done")

    async def _flow_two(self):
        await self.send("ping", route="two → pong")
```

### 4.2 Functor-Style Mapping

Dynamically register similar transitions with a loop:

```python
for src, dst in [("x→y"), ("y→z"), ("z→w")]:
    @Agent.receive(route=src)
    async def handler(self, msg, src=src, dst=dst):
        self.logger.info(f"Transition {src} received, forwarding to {dst}")
        await self.send(msg, route=dst)
```

* Treats each `(src→dst)` as an element in a collection
* Maps a common handler pattern over them

---

## 5. Putting Flows into Practice

1. **Sketch your FSM** on paper or whiteboard.
2. **Annotate each edge** with a route string.
3. **Write handlers** decorated for each transition.
4. **Leverage composition** by chaining routes in `send()` calls.
5. **Scale with higher abstractions** (background tasks, loops, dynamic registration).

> **Next steps:** integrate flow definitions with the [Summoner-Agent library](../../reference/lib_agent/index.md) for persistence, visualization, and testing.

---

<p align="center">
  <a href="traveling.md">&laquo; Previous: Traveling Between Servers</a>
  &nbsp;|&nbsp;
  <a href="async.md">Next: Async Programming and Event Loops &raquo;</a>
</p>





<p align="center">
  <a href="traveling.md">&laquo; Previous: Traveling Between Servers </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="async.md">Next: Async Programming and Event Loops &raquo;</a>
</p>