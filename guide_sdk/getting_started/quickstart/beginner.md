# Beginner's Guide

Here we show VERY-minimal code snippets (declaration or function headings)

present concepts
- client: send, receive
- server: run
- flow: fsm
- unique loop (setup): (queue, asqlite)

- [Clients versus agents](guide_sdk/getting_started/quickstart/begin_client.md)
- [Servers versus clients](guide_sdk/getting_started/quickstart/begin_server.md)
- [Agent behaviour as flows](guide_sdk/getting_started/quickstart/begin_flow.md)
- [Async programming and event loops](guide_sdk/getting_started/quickstart/begin_async.md)


------


# Beginner's Guide

> Very minimal code snippets and core concepts to get you oriented with Summoner's client, server, and agent flows.

**Purpose & audience**  
- **Who:** new users who want a concise overview of key patterns  
- **What:** skeletal code examples and concept definitions  
- **Outcome:** grasp the essentials before diving into detailed tutorials

---

## What You'll Learn

- How a client sends and receives messages  
- How to start a basic server  
- Modeling agent behaviour as a finite-state flow  
- Initializing queues and database connections in `setup()`

---

## Minimal Code Snippets

### Client: send & receive

```python
class SimpleAgent(Agent):

    async def on_message(self, msg):
        await self.send("ack")  # send a reply
````

### Server: run relay

```python
from summoner.server import SummonerServer

SummonerServer(name="relay").run()
```

### Flow: finite-state logic

```python
class FlowAgent(Agent):
    def setup(self):
        self.state = "start"

    async def on_message(self, msg):
        if self.state == "start":
            self.state = "next"
            await self.send("moving to next")
```

### Event loop & setup

```python
import asyncio, aiosqlite

class LoopAgent(Agent):
    def setup(self):
        self.queue = asyncio.Queue()
        # open a simple SQLite store
        self.db = asyncio.get_event_loop().run_until_complete(
            aiosqlite.connect("state.db")
        )
```

---

## Core Concepts

* **Clients versus agents**

  * A *client* process hosts runtime logic
  * An *agent* is the active entity that handles messages

* **Servers versus clients**

  * A *server* routes messages among agents
  * A *client* executes agent code

* **Agent behaviour as flows**

  * Model logic with explicit states and transitions
  * Use `setup()` to initialize state, then `on_message()` to move between states

* **Async programming & event loops**

  * Summoner uses Python's `asyncio` for non-blocking I/O
  * Override `setup()` to create tasks, queues, or open connections

---

## Dive Deeper

* [Clients versus agents](begin_client.md)
* [Servers versus clients](begin_server.md)
* [Agent behaviour as flows](begin_flow.md)
* [Async programming and event loops](begin_async.md)

---

<p align="center">
  <a href="basics_server.md">&laquo; Previous: Server Basics</a>
  &nbsp;|&nbsp;
  <a href="begin_client.md">Next: Clients versus agents &raquo;</a>
</p>



<p align="center">
  <a href="basics_client.md">&laquo; Previous: Client (Basics)</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="begin_server.md">Next: Beginner's Guide to Summoner's servers &raquo;</a>
</p>