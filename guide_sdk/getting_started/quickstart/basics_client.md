# Basics on the TCP-based Summoner clients


- config
- logs (config or self.logger.info ...)
- memory (variables, queue...)
- `setup()` (event loops)

-----


# Client Basics

> Learn how to configure, log, manage state, and bootstrap your Summoner client over a TCP connection.

**Purpose & audience**  
- **Who:** developers writing custom Summoner clients  
- **What:** how to set up connection options, capture logs, hold in-memory state, and start the asyncio event loop  
- **Outcome:** a working client scaffold you can extend for your own agent logic

---

## 1. Configuration

### 1.1 Default settings  
- Where Summoner looks for `config.yaml` or `config.json`  
- Typical fields: `host`, `port`, `reconnect_delay`, `log_level`

> **Sample copy:**  
> “By default, the client reads connection parameters from `config.yaml` in your working directory. You can override any value at runtime via keyword arguments to `run_client(...)`.”

### 1.2 Overriding via code  
- Pass `host` and `port` directly  
- Use environment variables (`SUMMONER_HOST`, `SUMMONER_PORT`)  
- Merging CLI flags with file config

```python
from summoner import run_client

# override config file
run_client(MyAgent, host="127.0.0.1", port=9000)
````

---

## 2. Logging

### 2.1 Built-in logger

* Every `Agent` instance has `self.logger`
* Default level: INFO
* Logs to console; configurable to file

> **Sample copy:**
> “Use `self.logger.info("…")` inside your agent to record events. Change verbosity with `config.log_level = "DEBUG"`.”

### 2.2 Custom handlers

* Adding file or rotating handlers
* Example: write logs to `logs/client.log`

```python
import logging
from summoner import Agent, run_client

class MyAgent(Agent):
    def setup(self):
        fh = logging.FileHandler("logs/client.log")
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.DEBUG)
```

---

## 3. State & Memory

### 3.1 In-memory variables

* Store simple counters or flags on `self`
* Example: `self.message_count = 0`

### 3.2 Queues and buffers

* Use `asyncio.Queue` for outgoing/incoming message buffering
* Example: `self.outbox = asyncio.Queue()`

> **Sample copy:**
> “Hold transient state in your agent instance. For more complex persistence, see the `state_persist` how-to.”

```python
import asyncio
class MyAgent(Agent):
    def setup(self):
        self.message_count = 0
        self.outbox = asyncio.Queue()

    async def on_message(self, msg):
        self.message_count += 1
        await self.outbox.put(msg)
```

---

## 4. Bootstrapping & Event Loop

### 4.1 `setup()` hook

* Called once before connection
* Ideal for creating tasks, queues, or custom loop policies

### 4.2 Starting the loop

* `run_client(...)` handles loop creation and shutdown
* Pass additional loop arguments if needed

> **Sample copy:**
> “Override `setup()` to spin up background tasks before your agent connects. The SDK will then call `run_client`, which starts and manages the asyncio event loop for you.”

```python
class MyAgent(Agent):
    def setup(self):
        self.logger.info("Initializing agent")
        self.loop.create_task(self.background_task())

    async def background_task(self):
        while True:
            await asyncio.sleep(10)
            self.logger.info("Heartbeat")
```

---

<p align="center">
  <a href="basics.md">&laquo; Previous: Basics (Intro)</a>
  &nbsp;|&nbsp;
  <a href="basics_agent.md">Next: Agent (Basics) &raquo;</a>
</p>
```

**How to adapt this template**

* Swap in your actual config file names/formats.
* Extend the logging section with your preferred handlers.
* Link to deeper how-tos (e.g. state persistence) as appropriate.
* Replace sample copy with tone and terminology matching your docs.



<p align="center">
  <a href="basics.md">&laquo; Previous: Basics (Intro)</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="basics_server.md">Next: Server (Basics) &raquo;</a>
</p>