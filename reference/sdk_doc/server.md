# <code style="background: transparent;">Summoner<b>.server</b></code>

A lightweight TCP broadcast server with two interchangeable backends:

* **Python (asyncio)**: simple, portable baseline useful for local dev and quick demos.
* **Rust (Tokio)**: production-grade event loop with backpressure, rate limiting, quarantine, and graceful shutdown.

You select the backend in the **server config** (`version: "python" | "rust"`). On Windows, the Rust backend is unavailable; the Python backend is used regardless of `version`.

---

## Quick start

**server.py**

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")
server.run(
    host="127.0.0.1",
    port=8888,
    config_path="server.json",   # or pass config_dict=...
)
```

**server.json (minimal)**

```json
{
  "version": "rust",
  "host": "127.0.0.1",
  "port": 8888,
  "logger": { "log_level": "INFO", "enable_console_log": true },
  "hyper_parameters": { "rate_limit_msgs_per_minute": 300 }
}
```

---

## Operational model

### Python backend (asyncio)

* Accepts clients, reads a line from each, and **broadcasts** it to all *other* clients.
* No built-in backpressure/rate-limit; designed for clarity and portability.

### Rust backend (Tokio)

* Accept loop + per-client tasks.
* **Backpressure monitor** collects "fan-out size" reports and issues:

  * **Throttle**: add small delay before handling next message.
  * **FlowControl**: pause reads for a longer delay.
  * **Disconnect**: forcefully drop misbehaving clients and **quarantine** them.
* **Rate limiter**: cap messages per client per minute.
* **Idle timeout**: drop clients that don't send anything for N seconds.
* **Graceful shutdown**: Ctrl+C notifies all clients before closing.

---

## Python API reference

### `class SummonerServer`

#### `__init__(name: Optional[str] = None)`

* **name**: logical name used by the logger.
* Creates an event loop, sets up client tracking and task bookkeeping.

#### `run(host: str = "127.0.0.1", port: int = 8888, *, config_path: Optional[str] = None, config_dict: Optional[dict] = None) -> None`

Start the server with the provided config.

* Loads config from `config_dict` (if provided) otherwise from `config_path`.
* On non-Windows with `version: "rust"`, dispatches to the Rust server via `rust_server_v1_0_0.start_tokio_server(...)`.
* Otherwise starts the **Python** asyncio server.

**Errors & shutdown**

* Handles `KeyboardInterrupt` / cancellation cleanly.
* Always waits for client tasks to finish; logs "Server exited cleanly."

**Example**

```python
server = SummonerServer("my:server")
server.run(config_dict={
  "version": "python",
  "host": "0.0.0.0",
  "port": 9000,
  "logger": {"log_level": "DEBUG", "enable_console_log": True}
})
```

#### `async def run_server(host: str = '127.0.0.1', port: int = 8888)`

Async entry for the **Python** backend. Binds and `serve_forever()`.

#### `async def handle_client(reader, writer)`

Core loop for **Python** backend:

* Reads lines from a client.
* Broadcasts JSON envelope `{"remote_addr": "...", "content": "<original without trailing \\n>"}` to others.
* On disconnect, cleans up and warns the client if possible.

#### `def set_termination_signals() -> None`

Install SIGINT/SIGTERM handlers (non-Windows).

#### `def shutdown() -> None`

Cancels all loop tasks to drive a clean exit.

---

## Choosing your backend

* Use **Rust** for production loads, fairness under fan-out spikes, and stronger safety (backpressure, rate limiting, quarantine).
* Use **Python** for quick prototypes or on Windows where Rust module isn't available.

---

## Configuration reference (with examples & client interplay)

Below each parameter lists: **Type**, **Default**, **Applies** (Python/Rust), **What it does**, **Interactions**, and **Example**.

### Core

#### `host`

* **Type**: `string`
* **Default**: required
* **Applies**: Python & Rust
* **What**: Bind address (e.g. `"127.0.0.1"`, `"0.0.0.0"`).
* **Interactions**: Must match what clients connect to.
* **Example**:

  ```json
  { "host": "0.0.0.0", "port": 8888 }
  ```

#### `port`

* **Type**: `integer`
* **Default**: required
* **Applies**: Python & Rust
* **What**: TCP port to listen on.

#### `version`

* **Type**: `"python"` | `"rust"`
* **Default**: `"python"` if omitted (effective)
* **Applies**: Python loader; Rust requires non-Windows
* **What**: Select backend implementation.
* **Interactions**: On Windows, always falls back to Python.

---

### Logging (`logger`)

#### `log_level`

* **Type**: `"DEBUG"|"INFO"|"WARNING"|"ERROR"|"CRITICAL"`
* **Default**: `"INFO"`
* **Applies**: Python & Rust
* **What**: Minimum severity to record.

#### `enable_console_log`

* **Type**: `boolean`
* **Default**: `true`
* **Applies**: Python & Rust
* **What**: Show logs on stdout.

#### `console_log_format`

* **Type**: `string`
* **Default**: built-in pretty format
* **Applies**: Python (console handler)
* **What**: printf-style format; allows ANSI coloring.

#### `enable_file_log`

* **Type**: `boolean`
* **Default**: `false`
* **Applies**: Python & Rust
* **What**: Write rotating logs to disk.

#### `enable_json_log`

* **Type**: `boolean`
* **Default**: `false`
* **Applies**: Python & Rust
* **What**: Emit JSON log lines (structured).
* **Interactions**: When `true`, **Rust** will prune payloads using `log_keys`.

#### `log_file_path`

* **Type**: `string (dir)`
* **Default**: `./logs` (typical)
* **Applies**: Python & Rust
* **What**: Directory for rotated logs.

#### `log_format`

* **Type**: `string`
* **Default**: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
* **Applies**: Python (file handler)
* **What**: Classic file format (ignored with JSON logging).

#### `max_file_size`, `backup_count`, `date_format`

* **Type**: `int`, `int`, `string`
* **Applies**: Python & Rust
* **What**: Rotation size, retention, timestamp formatting.

#### `log_keys`

* **Type**: `null | [] | [string, ...]`
* **Default**: `null` (log full payload)
* **Applies**: **Rust** (payload pruning), Python (file JSON logs if you add a similar filter)
* **What**: When JSON-logging inbound payloads, choose which **fields** to keep.
* **Example**:

  ```json
  "logger": {
    "enable_json_log": true,
    "log_keys": ["msg_id", "type"]    // keep only these keys from the client's JSON content
  }
  ```

---

### Hyper parameters (`hyper_parameters`)

> ⚠️ **Name mapping (Python → Rust)**
>
> * `client_timeout_secs` → Rust `client_timeout` (seconds)
> * `rate_limit_msgs_per_minute` → Rust `rate_limit` (msgs/min)

#### `connection_buffer_size`

* **Type**: `int`
* **Default**: `128`
* **Applies**: **Rust**
* **What**: Capacity of the channel that buffers "queue size" reports from clients into the backpressure monitor.
* **Interactions**: If you expect large fan-out (thousands of clients), increase this to avoid dropped reports.
* **Example**: Massive broadcast hub:

  ```json
  "connection_buffer_size": 2048
  ```

#### `command_buffer_size`

* **Type**: `int`
* **Default**: `32`
* **Applies**: **Rust**
* **What**: Channel capacity for **backpressure commands** (`Throttle`, `FlowControl`, `Disconnect`).
* **Insights**: If commands are dropped (rare), misbehaving clients might be corrected a bit later.

#### `control_channel_capacity`

* **Type**: `int`
* **Default**: `8`
* **Applies**: **Rust**
* **What**: Buffer depth of the **per-client** control channel that carries throttle/flow-control commands.
* **Interactions with client**: Higher values resist bursts of commands; doesn't require any client-side change.

#### `queue_monitor_capacity`

* **Type**: `int`
* **Default**: `100`
* **Applies**: **Rust**
* **What**: Local queue where each client task stages the **fan-out size** it's about to broadcast.
* **Insight**: If your broadcast size changes rapidly (clients joining/leaving), larger capacity improves accuracy.

#### `client_timeout_secs`

* **Type**: `int | null`
* **Default**: `300` (5 minutes)
* **Applies**: **Rust**
* **What**: Disconnect clients that **don't send any line** for this duration.
* **Important**: The timer resets **only when the client sends something**. A pure "listener" client will be considered idle.
* **Client interplay**:

  * If your client is primarily a receiver, either:

    * Send a lightweight **heartbeat** periodically (e.g., every 60s), **or**
    * Set `client_timeout_secs: null` to allow idle listeners indefinitely.
* **Examples**:

  * Strict ops: `"client_timeout_secs": 120`
  * Passive listeners welcomed: `"client_timeout_secs": null`

#### `rate_limit_msgs_per_minute`

* **Type**: `int`
* **Default**: `300`
* **Applies**: **Rust**
* **What**: Per-client rate limit. Exceeding it prompts a warning back to the client; the message is **not** broadcast.
* **Client interplay**:

  * Client's `concurrency_limit` + batching can burst; if you routinely send >300/min, raise this or reduce client concurrency.
* **Examples**:

  * Chatty agents: `"rate_limit_msgs_per_minute": 1200`
  * Public endpoint: `"rate_limit_msgs_per_minute": 120`

#### `timeout_check_interval_secs`

* **Type**: `int`
* **Default**: `30`
* **Applies**: **Rust**
* **What**: How often the server checks for idle clients.

#### `accept_error_backoff_ms`

* **Type**: `int`
* **Default**: `100`
* **Applies**: **Rust**
* **What**: Sleep after a failed `accept()` to avoid hot loops.

#### `quarantine_cooldown_secs`

* **Type**: `int`
* **Default**: `300`
* **Applies**: **Rust**
* **What**: Ban duration after a **forced** disconnect (from backpressure policy).
* **Client interplay**: A quarantined client's reconnect attempt is ignored until cooldown expires.

#### `quarantine_cleanup_interval_secs`

* **Type**: `int`
* **Default**: `60`
* **Applies**: **Rust**
* **What**: How often stale quarantine entries are purged.

#### `throttle_delay_ms`

* **Type**: `int`
* **Default**: `200`
* **Applies**: **Rust**
* **What**: Delay injected on **Throttle**. Keeps system responsive without harsh drops.

#### `flow_control_delay_ms`

* **Type**: `int`
* **Default**: `1000`
* **Applies**: **Rust**
* **What**: Longer pause on **FlowControl**. Gives downstream consumers time to drain.

#### `worker_threads`

* **Type**: `int`
* **Default**: `num_cores - 1`
* **Applies**: **Rust**
* **What**: Tokio worker count. Tune only if you know your CPU & workload profile.

---

### Backpressure policy (`hyper_parameters.backpressure_policy`)

These thresholds react to the **fan-out size** (how many peers a message would be sent to right now). That's a pragmatic proxy for "how much work is queued."

> In the Rust code, each message reports `queue_size = number_of_other_clients` prior to broadcast. The monitor applies the policy against this number.

#### `enable_throttle`

* **Type**: `boolean`
* **Default**: `true` (recommended)
* **What**: Enable small delays to smooth spikes.

#### `throttle_threshold`

* **Type**: `int`
* **Default**: `100`
* **What**: Fan-out size beyond which **Throttle** triggers.

#### `enable_flow_control`

* **Type**: `boolean`
* **Default**: `true`
* **What**: Pause reads when fan-out size is high for longer.

#### `flow_control_threshold`

* **Type**: `int`
* **Default**: `300`
* **What**: Fan-out size beyond which **FlowControl** triggers.

#### `enable_disconnect`

* **Type**: `boolean`
* **Default**: `true`
* **What**: Forcefully disconnect if pressure is extreme.

#### `disconnect_threshold`

* **Type**: `int`
* **Default**: `500`
* **What**: Fan-out size beyond which **Disconnect** triggers (and the client is **quarantined**).

**Example – large room with gentle shaping**

```json
"backpressure_policy": {
  "enable_throttle": true,
  "throttle_threshold": 1000,
  "enable_flow_control": true,
  "flow_control_threshold": 3000,
  "enable_disconnect": false,
  "disconnect_threshold": 10000
}
```

---

## Client ↔ Server tuning recipes

### 1) Low-latency chat (fast typing; many small messages)

* **Server**

  * `rate_limit_msgs_per_minute`: 900–1200
  * `throttle_delay_ms`: 50–100
  * `flow_control_delay_ms`: 250–500
  * Backpressure thresholds high enough to avoid unnecessary pauses.
* **Client**

  * `concurrency_limit`: 20–50
  * `batch_drain`: `true` (drain after each batch)
* **Why**: Short delays preserve interactivity; moderate concurrency prevents bursts.

### 2) High-throughput broadcast (many recipients)

* **Server**

  * Increase `connection_buffer_size`, `queue_monitor_capacity`
  * Backpressure: `throttle_threshold` near expected room size; `flow_control_threshold` \~2–3×
  * Enable JSON logs + `log_keys` to keep logs compact
* **Client**

  * Reduce `concurrency_limit` if disconnects/quarantine appear.
* **Why**: Accurate reporting → timely shaping; compact logs reduce I/O pressure.

### 3) Strict security / abuse resistance

* **Server**

  * `rate_limit_msgs_per_minute`: 60–120
  * `client_timeout_secs`: 120–180
  * Backpressure: lower thresholds, `enable_disconnect: true`, `quarantine_cooldown_secs`: 900
* **Client**

  * Ensure heartbeats if you're mostly a listener (or set timeout to `null`).

---

## Complete example config (Rust backend)

```json
{
  "version": "rust",
  "host": "0.0.0.0",
  "port": 8888,

  "logger": {
    "log_level": "INFO",
    "enable_console_log": true,
    "enable_file_log": true,
    "enable_json_log": true,
    "log_file_path": "./logs",
    "max_file_size": 10485760,
    "backup_count": 5,
    "date_format": "%Y-%m-%d %H:%M:%S.%f",
    "log_keys": ["msg_id", "type", "user_id"]
  },

  "hyper_parameters": {
    "connection_buffer_size": 512,
    "command_buffer_size": 64,
    "control_channel_capacity": 16,
    "queue_monitor_capacity": 200,

    "client_timeout_secs": 300,
    "rate_limit_msgs_per_minute": 600,
    "timeout_check_interval_secs": 30,
    "accept_error_backoff_ms": 100,

    "quarantine_cooldown_secs": 300,
    "quarantine_cleanup_interval_secs": 60,

    "throttle_delay_ms": 150,
    "flow_control_delay_ms": 750,

    "worker_threads": 0,

    "backpressure_policy": {
      "enable_throttle": true,
      "throttle_threshold": 250,
      "enable_flow_control": true,
      "flow_control_threshold": 750,
      "enable_disconnect": true,
      "disconnect_threshold": 1500
    }
  }
}
```

---

## Minimal client to test

```python
from summoner.client import SummonerClient, Direction

client = SummonerClient("summoner:client")

@client.hook(Direction.SEND)
async def print_send(payload):
    # enforce a small message shape
    return {"msg_id": "1", "type": "chat", "text": str(payload)}

@client.receive("/all")
async def on_any(payload):
    print("recv:", payload)
    # echo back (will be rate-limited / throttled as needed)
    from summoner.protocol.triggers import Move, load_triggers
    Trigger = load_triggers()
    return Move(Trigger.OK)

@client.send("/all")
async def say_hello():
    return {"msg_id": "1", "type": "chat", "text": "hello"}

client.run(port=8888, config_dict={"logger": {"log_level": "INFO"}})
```

---

## Notes & gotchas

* **Windows**: Rust backend is not available; Python backend runs even if `version: "rust"`.
* **Idle listeners** (Rust): if your client mostly **receives** and doesn't send, it will hit `client_timeout_secs` unless you:

  * send a periodic heartbeat; or
  * set `client_timeout_secs: null`.
* **Disconnect ⇒ Quarantine**: When the policy disconnects a client, it **adds the address to a cooldown list**; reconnect attempts are ignored until the period expires.
* **Fan-out based thresholds**: The backpressure thresholds are compared to **current recipient count** (how many peers would receive your message). This is a practical signal for work queued; tune thresholds relative to expected room size.

---

<p align="center">
  <a href="client.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.client</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="proto.md">Next: <code style="background: transparent;">Summoner<b>.protocol</b></code> &raquo;</a>
</p>