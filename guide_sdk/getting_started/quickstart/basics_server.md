# Basics on the TCP-based Summoner servers

- config
- logs
- python (base) versus rust (recommended): what to choose


----------


# Server Basics

> Learn how to configure, run, and monitor your Summoner relay server over TCP, choosing between Python and Rust implementations.

**Purpose & audience**  
- **Who:** Developers deploying a Summoner server in dev or production  
- **What:** configuration options, logging best practices, implementation choices, and startup procedures  
- **Outcome:** a ready-to-use server scaffold tuned to your environment

---

## 1. Configuration

### 1.1 Config file  
- Default path: `config.yaml` or `config.json` in working directory  
- Common fields:  
  - `host`: interface to bind (e.g. `0.0.0.0`)  
  - `port`: listening port (e.g. `8000`)  
  - `max_connections`: cap on simultaneous agents  
  - `reconnect_policy`: backoff strategy  

> **Sample copy:**  
> “Place a `config.yaml` next to your startup script. Example:  
> ```yaml
> host: 0.0.0.0
> port: 8000
> max_connections: 100
> reconnect_policy:
>   initial_delay: 1
>   max_delay: 30
> ```  
>

### 1.2 CLI flags  
- Override any config entry at runtime:  
```bash
  summoner-server start --host 127.0.0.1 --port 9000 --max-connections 50
```

* Flags take precedence over file settings

---

## 2. Logging

### 2.1 Built-in logging

* Default logger at INFO level
* Prints to stdout with timestamps and levels

### 2.2 Custom handlers

* File logging: write to `logs/server.log`
* Rotating logs: use `logging.handlers.RotatingFileHandler`
* Example setup in code:

  ```python
  import logging
  from summoner.server import SummonerServer

  logger = logging.getLogger("summoner.server")
  fh = logging.handlers.RotatingFileHandler("logs/server.log", maxBytes=1e6, backupCount=3)
  logger.addHandler(fh)
  logger.setLevel(logging.DEBUG)

  SummonerServer(name="main").run()
  ```

---

## 3. Python vs Rust Implementations

| Implementation | Pros                            | Cons                              |
| -------------- | ------------------------------- | --------------------------------- |
| **Python**     | Quick iteration, easy debugging | Lower throughput under high load  |
| **Rust**       | High performance, low latency   | Requires Rust toolchain and build |

> **Sample copy:**
> “For prototypes or debugging, the Python server is ideal. Switch to the Rust binary for production to handle hundreds of agents with minimal overhead.”

---

## 4. Running the Server

### 4.1 CLI mode

```bash
# Python server
summoner-server start --config config.yaml

# Rust server (if installed)
summoner-server-rust --config config.yaml
```

### 4.2 Programmatic mode

```python
from summoner.server import SummonerServer

if __name__ == "__main__":
    server = SummonerServer(name="my_relay")
    server.run(config_path="config.yaml")
```

---

## 5. Monitoring Connections

* **Console output:** watch for `Client connected: <agent_id>` messages
* **Metrics endpoint:** (if enabled) expose Prometheus metrics on `/metrics`
* **Health checks:** integrate with your orchestration tool (Kubernetes, systemd)

> **Sample copy:**
> “Enable the metrics module in your config to scrape live connection counts and message rates. Use `kubectl port-forward` or `curl` for quick checks.”

---

<p align="center">
  <a href="basics_agent.md">&laquo; Previous: Agent (Basics)</a>
  &nbsp;|&nbsp;
  <a href="beginner.md">Next: Beginner’s Guide &raquo;</a>
</p>



<p align="center">
  <a href="basics_client.md">&laquo; Previous: Client (Basics)</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="beginner.md">Next: Beginner’s Guide &raquo;</a>
</p>