# Traveling Between Servers



NOTE: refer to the agent library if needed

- Chat agent giving order -> to travel to other server
- Question agent receive orders, go to server where answer agent is


Tutorials on traveling agent and the idea that controling an agent cam be done by a "summoner"

-------


# Traveling Between Servers

> Learn how to move agents seamlessly across different relay servers, enabling dynamic workflows and load distribution.

**Purpose & audience**  
- **Who:** developers building multi-relay or geo-distributed agent networks  
- **What:** overview of the travel API, code examples for instructing an agent to migrate, and best practices for state handoff  
- **Outcome:** you'll be able to send “move” commands to your agents and have them reconnect to a new server automatically

---

## 1. Why Agent Mobility?

- **Scalability:** distribute agents across multiple servers to balance load  
- **Proximity:** move agents closer to data or other collaborators  
- **Isolation:** spin up dedicated environments per task, then retire them  

> **Sample copy:**  
> “Instead of rebooting your entire network, tell individual agents to relocate. Summoner handles the disconnect, state serialization, and reconnect for you.”

---

## 2. Core Concepts

- **Summoner (controller):** an external process that issues travel orders  
- **Travel route:** a special message route (e.g. `"travel"`) that triggers migration  
- **State snapshot & restore:** agents serialize in-memory state, then resume on the new host

---

## 3. Travel API Overview

Summoner's client class provides:

```python
await self.travel(host: str, port: int, route: str = "")  
````

* **`host` / `port`**: target server address
* **`route`**: message route to resume on arrival (default stays on the same route)

Under the hood, `travel()`:

1. Serializes `self` (state, queues, metadata)
2. Sends a “move” command to the current server
3. Closes the TCP connection
4. Reconnects to the new server and rehydrates state

---

## 4. Example: Chat Agent Ordering a Move

```python
from summoner import Agent, run_client

class MovingAgent(Agent):
    async def on_connect(self):
        # after connecting, tell myself to move in 5s
        await self.send("move", payload={"delay": 5})

    @Agent.receive(route="move")
    async def handle_move(self, msg):
        delay = msg.get("payload", {}).get("delay", 0)
        await asyncio.sleep(delay)
        self.logger.info("Traveling to new host")
        await self.travel("127.0.0.1", 9001)
        self.logger.info("Arrived at new server")

if __name__ == "__main__":
    run_client(MovingAgent, host="127.0.0.1", port=8888)
```

---

## 5. Example: Question Agent Following Orders

```python
from summoner import Agent, run_client

class QuestionAgent(Agent):
    @Agent.receive(route="ask")
    async def on_ask(self, msg):
        question = msg["payload"]["q"]
        if question == "move_to_answer":
            # migrate to the answer server
            await self.travel("127.0.0.1", 9002, route="answer")
        else:
            # handle other questions...
            await self.send("response", payload={"text": "I don't know."})

if __name__ == "__main__":
    run_client(QuestionAgent, host="127.0.0.1", port=8888)
```

---

## 6. Best Practices & Considerations

* **State consistency:** ensure all critical data is in attributes or queues before traveling
* **Failure handling:** wrap `travel()` in try/except and fallback to reconnection logic
* **Version compatibility:** both source and target servers should run compatible SDK versions
* **Security:** authenticate “move” commands to prevent unauthorized migrations

---

## 7. Tutorials & Further Reading

* [How-tos: Traveling Between Servers](../howtos/proto/traveling.md)
* [Agent Libraries: Summoner-Agent Travel Extensions](../../reference/lib_agent/kobold.md)

---

<p align="center">
  <a href="server_relay.md">&laquo; Previous: Servers and Relay</a>
  &nbsp;|&nbsp;
  <a href="flow.md">Next: Agent Behaviour as Flows &raquo;</a>
</p>




<p align="center">
  <a href="server_relay.md">&laquo; Previous: Servers and Relays </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="flow.md">Next: Agent behaviour as Flows &raquo;</a>
</p>