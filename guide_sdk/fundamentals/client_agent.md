# Clients and Agents

NOTE: refer to the agent library if needed

## Configuration
Explain very well the config (each parameter has a small paragraph or section)

## Code

routes



(explain an agent without flow)


Should I briefly refer to `summoner-agent` here (this will be done later but a small reference could be useful).


--------


# Clients and Agents

> Dive into how Summoner separates the runtime host (client) from the logical entity (agent), and configure each to suit your needs.

**Purpose & audience**  
- **Who:** developers building and deploying agents with the Summoner SDK  
- **What:**  
  1. Configure connection and behavior parameters  
  2. Write client-side bootstrap code  
  3. Define agents without needing full flow abstractions  
- **Outcome:** a clear split between “hosting” vs “logic,” with examples you can extend

---

## 1. Configuration

Summoner clients read settings from a config file, CLI flags, or environment variables. Here are the common parameters:

### 1.1 Connection parameters

- **`host`**  
  The server address to connect to (default: `localhost`).  
- **`port`**  
  The TCP port on which the relay listens (default: `8000`).  
- **`reconnect_delay`**  
  Seconds to wait before retrying a failed connection (default: `5`).

### 1.2 Runtime options

- **`log_level`**  
  One of `DEBUG`, `INFO`, `WARN`, or `ERROR`. Controls verbosity of `self.logger`.  
- **`client_name`**  
  A unique identifier for this client instance. Used in logs and server metrics.  
- **`heartbeat_interval`**  
  How often (in seconds) the client sends a ping to keep the connection alive.

> **Sample copy:**  
> “You can place a `client_config.yaml` next to your script, or pass flags like `--host 127.0.0.1 --port 9000 --log-level DEBUG`. Environment variables `SUMMONER_HOST` and `SUMMONER_PORT` are also supported.”

---

## 2. Client Bootstrap Code

### 2.1 Using `run_client`

The simplest way to start a client-hosted agent:

```python
from summoner import Agent, run_client

class MyAgent(Agent):
    async def on_message(self, msg):
        print("Got:", msg)

if __name__ == "__main__":
    run_client(MyAgent,
               host="127.0.0.1",
               port=8000,
               log_level="INFO",
               client_name="example_client")
````

* **`run_client`**

  * Reads config, sets up logging, and connects to the server.
  * Manages the asyncio loop and reconnection logic.
* **Keyword overrides**
  Any argument passed to `run_client` supersedes the config file.

---

## 3. Agent Logic Without Flows

You don’t need to model a full FSM to write an agent. For simple behaviors, override the basic lifecycle hooks:

```python
class EchoAgent(Agent):
    async def on_connect(self):
        await self.send("hello!")

    async def on_message(self, msg):
        await self.send(msg)  # echo back

    async def teardown(self):
        print("Goodbye!")
```

* **`on_connect`**
  Called once after the TCP handshake.
* **`on_message`**
  Invoked on each inbound payload.
* **`teardown`**
  Clean-up before the client shuts down.

---

## 4. Routes and Message Handling

By default, all messages use the empty route (`""`). You can define multiple handlers using custom routes:

```python
@agent.receive(route="chat")
async def on_chat(msg):
    print("Chat:", msg)

@agent.send(route="chat")
async def send_chat():
    return "howdy!"
```

* **Routes** act as labels for different message types.
* **Multiple handlers** let you partition logic cleanly.

---

## 5. Linking to the Agent Library

For advanced behaviors—persistent state, complex flows, or plugins—see the [Summoner-Agent library reference](../../reference/lib_agent/index.md). You can integrate it later once your basic client and agent are up and running.

---

<p align="center">
  <a href="index.md">&laquo; Previous: Fundamentals</a>
  &nbsp;|&nbsp;
  <a href="server_relay.md">Next: Servers and Relay &raquo;</a>
</p>






<p align="center">
  <a href="index.md">&laquo; Previous: Fundamentals </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="server_relay.md">Next: Servers and Relay &raquo;</a>
</p>


