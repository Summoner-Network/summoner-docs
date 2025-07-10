# Beginner's Guide to Summoner's Servers


Very light code use, but overview is good (with many insights if possible)

How to launch and use servers

Servers are relay and should not be trusted


How to program a server

Server:
- broacast
- dedicated (relay)
- host client
- hybrid (event several hsot +  possible independent relay)


---------



Here’s a structured rewrite for **`begin_server.md`** that mirrors the style of the client guide—light on code, rich in conceptual insight.

````markdown
---
sidebar_label: Servers vs Clients
---

# Beginner’s Guide to Summoner Servers

> Minimal examples and core concepts for launching a Summoner relay server. Understand the server’s role, trust boundaries, and available modes.

**Purpose & audience**  
- **Who:** developers deploying a relay server in dev or production  
- **What:**  
  1. How to start the server via CLI or code  
  2. The four server modes and when to use each  
  3. Why the relay is untrusted and how to secure messages  
- **Outcome:**  
  - Have a running server in minutes  
  - Pick the right deployment mode  
  - Grasp basic security considerations

---

## 1. Starting the Relay

### 1.1 CLI mode

```bash
# Python relay
summoner-server start --config path/to/config.yaml

# Rust relay (higher performance)
summoner-server-rust start --config path/to/config.yaml
````

* **Flags override** the config file (e.g. `--port 9000`).
* Default `config.yaml` fields:

  ```yaml
  host: 0.0.0.0
  port: 8000
  max_connections: 100
  ```

### 1.2 Programmatic mode

```python
from summoner.server import SummonerServer

if __name__ == "__main__":
    server = SummonerServer(name="my_relay")
    server.run(config_path="config.yaml")
```

> **Sample copy:**
> “Use the CLI for quick spin-ups. For embedding or advanced orchestration, start the server from Python code.”

---

## 2. Server Modes

Summoner supports different relay topologies:

| Mode                | Description                                                       | Use case                                 |
| ------------------- | ----------------------------------------------------------------- | ---------------------------------------- |
| **Broadcast**       | Sends every message to all connected agents (pub/sub style)       | Chat rooms, global notifications         |
| **Dedicated**       | Routes only between predefined pairs or groups (point-to-point)   | Private pipelines, 1-on-1 sessions       |
| **Embedded (Host)** | Runs the relay inside a client process for local testing          | Rapid prototyping, offline demos         |
| **Hybrid**          | Multiple relay instances forward messages among themselves (mesh) | Geo-distributed deployments, L2 networks |

> **Sample copy:**
> “Choose Broadcast for open networks. Use Dedicated when messages should go only to specific agents. Embedded mode lets you run a mini-relay in the same process, and Hybrid links multiple relays across hosts.”

---

## 3. Security & Trust

* **Untrusted Relay**

  * The server forwards messages blindly.
  * Do *not* rely on it for confidentiality or integrity.

* **End-to-end Encryption**

  * Encrypt payloads on the client side.
  * Use Summoner’s protocol hooks to negotiate keys before sending.

* **Handshake & Authentication**

  * Implement a handshake in `on_connect` to verify identities.
  * Reject unauthorized clients by closing the connection.

> **Sample copy:**
> “Treat the relay as a dumb pipe. For sensitive data, always encrypt before `send()`, and validate peer credentials in your agent’s `on_connect()`.”

---

## 4. Logging & Monitoring

* **Built-in logs** at INFO level show connections/disconnections.
* **Custom handlers**:

  ```python
  import logging
  from summoner.server import SummonerServer

  logger = logging.getLogger("summoner.server")
  fh = logging.FileHandler("logs/relay.log")
  logger.addHandler(fh)
  logger.setLevel(logging.DEBUG)

  SummonerServer(name="relay").run()
  ```
* **Metrics endpoint** (if enabled): scrape Prometheus metrics on `/metrics`.

> **Tip:** integrate with your orchestration platform (Kubernetes probes, systemd) using the metrics or health-check flags.

---

<p align="center">
  <a href="begin_client.md">&laquo; Previous: Clients vs Agents</a>
  &nbsp;|&nbsp;
  <a href="begin_flow.md">Next: Agent Flows &raquo;</a>
</p>


**Next up:** the **Flows** page, where we’ll map out how agents transition between states. Let me know if you’d like extra code snippets or deeper dives here!



<p align="center">
  <a href="begin_client.md">&laquo; Previous: Beginner's Guide to Summoner's Clients </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="begin_flow.md">Next: Beginner's Guide to Agent's Flows &raquo;</a>
</p>