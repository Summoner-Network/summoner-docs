# Basics on the TCP-based Summoner clients

Agents should be seen as extended client classes from the core.

------

# Agent Basics

> Agents are specialized client subclasses that encapsulate your business logic over the Summoner network.

**Purpose & audience**  
- **Who:** Developers implementing custom agent behaviors  
- **What:** how to extend the core `Agent` class, override lifecycle hooks, and exchange messages  
- **Outcome:** a clear scaffold for writing agents that connect, handle events, and clean up gracefully

---

## 1. Extending the Core Agent

### 1.1 Subclassing `Agent`  
- Your agent class must inherit from `summoner.Agent`  
- All networking, reconnection, and protocol plumbing is handled by the base class  

> **Sample copy:**  
> “Create a new file `my_agent.py` and define your agent class by subclassing `Agent`. You’ll only need to override the methods that matter for your logic.”

```python
from summoner import Agent, run_client

class MyAgent(Agent):
    pass  # we’ll add hooks in the next section

if __name__ == "__main__":
    run_client(MyAgent)
````

---

## 2. Lifecycle Hooks

Override these methods to plug into key events:

| Hook                    | When it runs                                | Use for…                              |
| ----------------------- | ------------------------------------------- | ------------------------------------- |
| `setup(self)`           | Once, before connecting                     | initialize state, start tasks         |
| `on_connect(self)`      | After a successful connection to the server | send registration or hello message    |
| `on_message(self, msg)` | On each inbound message                     | parse payload, trigger business logic |
| `on_disconnect(self)`   | When the connection is lost                 | cleanup, schedule reconnect attempts  |
| `teardown(self)`        | Once, when shutting down                    | close resources, flush buffers        |

> **Sample copy:**
> “Use `setup()` to prepare any queues or background tasks. Then, your main logic lives in `on_message()`. Finally, handle cleanup in `teardown()`.”

```python
class MyAgent(Agent):
    def setup(self):
        self.counter = 0

    async def on_connect(self):
        await self.send("hello, server")

    async def on_message(self, msg):
        self.counter += 1
        print(f"Msg #{self.counter}: {msg}")
        if self.counter > 5:
            await self.stop()

    async def teardown(self):
        print("Agent shutting down")
```

---

## 3. Sending and Receiving

* **Sending:**

  * `await self.send(payload, target=None)`
  * By default, messages go to the connected server; specify `target` for peer-to-peer

* **Receiving:**

  * Messages arrive in `on_message(self, msg)` as raw payloads or envelope objects
  * Inspect metadata (sender ID, timestamp) if available

> **Sample copy:**
> “Call `self.send()` from any hook to dispatch messages. In `on_message()`, you’ll receive the payload exactly as the sender provided it.”

---

## 4. Managing State

* **Instance attributes** hold transient data (`self.foo = …`)
* **Queues** (`asyncio.Queue`) buffer incoming or outgoing messages
* **Persistence**: for durable state, see [Persist agent states](../../howtos/client/state_persist.md)

> **Sample copy:**
> “Keep counters, caches, or flags on `self`. For cross-restart state, integrate an external store via the persistence how-to.”

---

## 5. Example: Echo Agent

```python
from summoner import Agent, run_client

class EchoAgent(Agent):
    async def on_message(self, msg):
        # simply echo back whatever we get
        await self.send(msg)

if __name__ == "__main__":
    run_client(EchoAgent, host="localhost", port=9000)
```

> **Sample copy:**
> “This EchoAgent replies with the same message it receives. It’s a minimal test to verify connectivity and message flow.”

---

<p align="center">
  <a href="basics_client.md">&laquo; Previous: Client (Basics)</a>
  &nbsp;|&nbsp;
  <a href="basics_server.md">Next: Server (Basics) &raquo;</a>
</p>
```

**How to adapt this template**

* Replace `summoner.Agent`, `run_client`, and method names with your actual API.
* Add or remove lifecycle hooks based on the SDK’s design.
* Link to deeper how-tos (state persistence, error handling) as needed.



<p align="center">
  <a href="basics_client.md">&laquo; Previous: Client (Basics)</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="basics_server.md">Next: Server (Basics) &raquo;</a>
</p>