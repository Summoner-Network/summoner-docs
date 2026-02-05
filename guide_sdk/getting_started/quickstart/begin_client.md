# Getting Started with Summoner Clients & Agents

> How to think about and run a Summoner client

## What a client is (and how agents relate)

A **Summoner client** is a TCP program that connects to a Summoner server, **receives** messages, and **sends** messages. It has no standalone purpose without a server; the server is the rendezvous point for communication.

<p align="center">
  <img width="270px" src="../../../assets/img/begin_client_agent_rounded.png"/>
</p>

However, a client focuses on messaging and orchestration primitives; it does not include the security and policy layers needed to operate safely on an open server with untrusted peers. To address this, we provide **agent classes**. An **agent** is a client with additional behavior:

* `SummonerClient` is the base class.
* An *agent class* **subclasses** `SummonerClient` and adds features such as cryptographic envelopes, handshake logic, DID utilities, SummonerAPI helpers, and orchestration helpers. You are free to design your own agent class for your project.

> [!NOTE]
> A **reference agent class** will ship with the **Aurora** update (via [`summoner-agentclass`](https://github.com/Summoner-Network/summoner-agentclass)). It provides an opinionated baseline for orchestration: message signing and verification, handshake scaffolding, DID utilities, policy-driven validation, and route/flow helpers. Use it as a ready-made starting point if you prefer not to build these pieces yourself.


## Running a client

You need a server to connect to. This can be your local server (`127.0.0.1`), a teammate's machine, or a hosted server.

Clients do **not** require special parameters to connect to **either** the Python or Rust server: the wire protocol is the same. The server's implementation is transparent to the client.

### Run an empty client

First, start a local server. See [Getting Started with Summoner Servers](basics_server.md), and then run:

```bash
python first_server.py
```

Second, create a minimal client in a python file, say `first_client.py`, as shown below. The host and port link to the local server that you started earlier:

```python
from summoner.client import SummonerClient

client = SummonerClient()
client.run(host="127.0.0.1", port=8888)
```

After this, run the script:

```bash
python first_client.py
```

You should see the client connect to the local server

```text
[DEBUG] Config file not found: `None`
2025-09-13 14:43:33.525 - <client:no-name> - INFO - Connected to server @(host=127.0.0.1, port=8888)
```

<details>
<summary>
<b>(Click to expand)</b> If you stop the server (Ctrl+C), the client's <b>reconnection logic</b> kicks in. The default policy retries the "primary" address, then falls back to a "default" address (if configured), then exits.
</summary>
<br>

```log
2025-09-13 15:20:48.967 - <client:no-name> - ERROR - [ServerDisconnected: EOF during read] (Primary) retry 1 of 3; sleeping 3s
2025-09-13 15:20:51.969 - <client:no-name> - ERROR - [ConnectionRefusedError: [Errno 61] Connect call failed ('127.0.0.1', 8888)] (Primary) retry 2 of 3; sleeping 3s
2025-09-13 15:20:54.972 - <client:no-name> - ERROR - [ConnectionRefusedError: [Errno 61] Connect call failed ('127.0.0.1', 8888)] (Primary) retry 3 of 3; sleeping 3s
2025-09-13 15:20:57.973 - <client:no-name> - ERROR - Primary retry limit reached (3)
2025-09-13 15:20:57.974 - <client:no-name> - WARNING - Falling back to default server at None:None
2025-09-13 15:20:57.974 - <client:no-name> - ERROR - [ConnectionRefusedError: [Errno 61] Connect call failed ('127.0.0.1', 8888)] (Default) retry 1 of 2; sleeping 3s
2025-09-13 15:21:00.977 - <client:no-name> - ERROR - [ConnectionRefusedError: [Errno 61] Connect call failed ('127.0.0.1', 8888)] (Default) retry 2 of 2; sleeping 3s
2025-09-13 15:21:03.978 - <client:no-name> - ERROR - Default retry limit reached (2)
2025-09-13 15:21:03.979 - <client:no-name> - CRITICAL - Cannot connect to fallback None:None after 2 attempts; exiting
```

</details>
<br>

> [!TIP]
> You control retry delays and limits via the **client config** (next section).

### Run a client with a config file

Configuration can override address selection and tune reconnection behavior.

To see this, create a configuration file `client_config.json` containing the following JSON structure:

```json
{
  "host": null,
  "port": null,
  "hyper_parameters": {
    "reconnection": {
      "retry_delay_seconds": 1,
      "primary_retry_limit": 1,
      "default_host": "localhost",
      "default_port": 8888,
      "default_retry_limit": 1
    }
  }
}
```

The run the client with the config:

```python
from summoner.client import SummonerClient

client = SummonerClient()
client.run(host="127.0.0.1", port=8888, config_path="client_config.json")
```

<details>
<summary>
<b>(Click to expand)</b> Stopping the server now leads to faster retries and exit, as dictated by the config.
</summary>
<br>

```log
2025-09-13 15:21:24.339 - <client:no-name> - INFO - Connected to server @(host=127.0.0.1, port=8888)
2025-09-13 15:21:28.320 - <client:no-name> - INFO - Client about to disconnect...
2025-09-13 15:21:28.321 - <client:no-name> - ERROR - [ServerDisconnected: EOF during read] (Primary) retry 1 of 1; sleeping 1s
2025-09-13 15:21:29.322 - <client:no-name> - ERROR - Primary retry limit reached (1)
2025-09-13 15:21:29.323 - <client:no-name> - WARNING - Falling back to default server at localhost:8888
2025-09-13 15:21:29.332 - <client:no-name> - ERROR - [OSError: Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)] (Default) retry 1 of 1; sleeping 1s
2025-09-13 15:21:30.333 - <client:no-name> - ERROR - Default retry limit reached (1)
2025-09-13 15:21:30.333 - <client:no-name> - CRITICAL - Cannot connect to fallback localhost:8888 after 1 attempts; exiting
```
</details>

#### Address precedence: config vs code

If **both** your Python code **and** the config file specify a host/port, the **config file takes precedence**. This allows deployments to be steered without code changes.

For example, you can force the client to use `testnet.summoner.org` even if code passes a different address:

```json
{
  "host": "testnet.summoner.org",
  "port": 8888,
  "hyper_parameters": {
    "reconnection": {
      "retry_delay_seconds": 3,
      "primary_retry_limit": 5,
      "default_host": "localhost",
      "default_port": 8888,
      "default_retry_limit": 3
    }
  }
}
```

If you run the same Python snippet as above, you should see:

```text
[DEBUG] Loaded config from: client_config.json
2025-09-13 15:25:46.398 - first_client - INFO - Connected to server @(host=testnet.summoner.org, port=8888)
```

## From client to agent

In Summoner, an agent is by definition a subclass of `SummonerClient`. You can define your own agent class by starting with a minimal subclass of `SummonerClient` and then add behavior.

```python
from summoner.client import SummonerClient

class MyAgent(SummonerClient):
    pass

agent = MyAgent()
agent.run(host="127.0.0.1", port=8888)
```

With an empty subclass of `SummonerClient` as above, the output is the same as the base client; the difference is you now have a place to attach **handlers** and **hooks**.

> [!NOTE]
> Our upcoming `SummonerAgent` class (coming soon in our **Aurora** update) will propose what we think should be a solid baseline for agent-to-agent communication. The module will be available via [`summoner-agentclass`](https://github.com/Summoner-Network/summoner-agentclass) and can be installed alongside the SDK. You can continue to build your own agent classes; this reference class is meant to save time for common orchestration needs.

## Building interactive agents

Agents typically do two things:

* **receive** messages from the server and react
* **send** messages to the server (periodically or in reaction to input)

Both are declared with decorators on the **instance**.

> [!IMPORTANT]
> Handlers must be **async**. The client validates signatures at registration.

### Minimal receive

The simplest receiver behavior prints messages received from the server:

```python
from typing import Any
from summoner.client import SummonerClient

agent = SummonerClient()

@agent.receive(route="")
async def recv_handler(msg: Any) -> None:
    print(f"received: {msg!r}")  # runs concurrently with senders

agent.run(host="127.0.0.1", port=8888)
```

* `route=""` acts as a catch-all for this quick start; its string value is **inconsequential**.
* Receive handlers run concurrently with senders.
* The function receives whatever other peers send (string or JSON-like dict).

### Minimal send (keeps sending)

The simplest sender can emit a message every second:

```python
import asyncio
from summoner.client import SummonerClient

agent = SummonerClient()

@agent.send(route="")
async def heartbeat():
    print("Sending 'ping'")
    await asyncio.sleep(1.0)   # sets the pace; sender is polled repeatedly
    return "ping"

agent.run(host="127.0.0.1", port=8888)
```

This keeps sending because the send loop polls registered senders. The `await asyncio.sleep(...)` sets the pace.

### Controlling sends (send once)

To send only once, return a value the first time and `None` afterward:

```python
from summoner.client import SummonerClient

agent = SummonerClient()
_sent = False

@agent.send(route="")
async def hello_once():
    global _sent
    if _sent:
        return None # no message this cycle
    _sent = True
    print("Sending 'Hello'")
    return "Hello"

agent.run(host="127.0.0.1", port=8888)
```

Returning `None` means *no message this cycle.* You can also flip flags from a `@receive` handler to make sending reactive.

## Composition: thinking in "capabilities"

Composition is central to how you scale an agent without rewriting it. The practical unit of reuse is a **capability**: a small set of `@receive`/`@send` handlers tied to a set of **routes**, or sometimes a set of route types classified through node logic (see [SDK Reference on the `Node` class](../../../reference/sdk_doc/proto/process.md#classes-and-data-types)). You can copy these blocks between agents to add or remove skills.

**Mental model**

* Treat each **route** as a **lane** dedicated to one capability (e.g., `"echo"`, `"heartbeat"`, `"orders"`).
* A capability usually has:

  * one or more `@receive` handlers for that lane
  * zero or more `@send` handlers that produce messages on that lane
* An agent with multiple lanes is effectively a **bundle of sub-agents** that share the same process and connection.

**Small two-capability example**

```python
import asyncio
from typing import Any
from summoner.client import SummonerClient

agent = SummonerClient()

# Capability 1: echo
@agent.receive(route="echo")
async def echo_rx(msg: Any) -> None:
    print(f"[echo] {msg!r}")

@agent.send(route="echo")
async def echo_tx():
    await asyncio.sleep(2)
    return {"kind": "echo", "text": "hello"}

# Capability 2: heartbeat
@agent.send(route="heartbeat")
async def hb_tx():
    await asyncio.sleep(5)
    return "hb"

agent.run(host="127.0.0.1", port=8888)
```

This single agent exposes two clear capabilities on distinct routes. In a larger project, you can keep each capability in its own file and register them onto the same `agent` instance. If you later need to assemble capabilities authored in separate agents, see the **[`Merger`](../../../reference/sdk_doc/client/merger.md)** utility in the SDK reference; it replays handlers from multiple agents into one process.

> [!TIP]
> Choose short, stable route names. Routes are your namespace for composition. Keeping them consistent makes it easy to move capabilities between agents.


<p align="center">
  <a href="./begin_server.md">&laquo; Previous: Getting Started with Summoner Servers</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="./begin_flow.md">Next: Orchestrating Agent Behavior Using Flows &raquo;</a>
</p>
