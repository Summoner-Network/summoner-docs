# <code style="background: transparent;">Summoner<b>.server.server</b></code>

A lightweight TCP broadcast server with two interchangeable backends:

* **Python (asyncio)** – simple, portable baseline for local dev and demos.
* **Rust (Tokio via PyO3)** – production-grade event loop with backpressure, rate-limiting, quarantine, and graceful shutdown.

Pick the backend in your **server config** with `version: "python" | "rust"`. On Windows, the Rust backend is unavailable and the server runs in Python regardless of `version`.

> 📎 The full configuration guide (every parameter with examples) lives in **[server_config.md](./server_config.md)**.

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

**Manual test with `nc`**

```bash
# terminal A
nc 127.0.0.1 8888

# terminal B
nc 127.0.0.1 8888

# type in A; B receives:
# {"remote_addr":"127.0.0.1:54321","content":"<your line>"}
```

---

## Operational model

### Python backend (asyncio)

* Accepts clients, reads a **line** from each, and **broadcasts** it to all *other* clients.
* Broadcast payload is a JSON envelope:

  ```json
  {"remote_addr":"<ip:port>","content":"<original line without trailing \\n>"}
  ```
* Designed for clarity & portability; no built-in backpressure/limits.

### Rust backend (Tokio)

* Accept loop + per-client tasks.
* **Backpressure monitor** issues:

  * **Throttle** (small delay),
  * **FlowControl** (pause reads),
  * **Disconnect** (drop + quarantine).
* **Rate limiter**: per-client messages/minute.
* **Idle timeout**: disconnect if no activity for N seconds.
* **Graceful shutdown**: Ctrl+C notifies clients, then closes.

---

## API reference (Python front)

### `class SummonerServer`

#### `__init__(name: Optional[str] = None)`

* **name**: logical name used by the logger.
* Creates an event loop; sets up client and task bookkeeping.

#### `run(host: str = "127.0.0.1", port: int = 8888, *, config_path: Optional[str] = None, config_dict: Optional[dict] = None) -> None`

Start the server with the provided config.

* Loads config from `config_dict` (if provided) otherwise `config_path`.
* **Backend choice**

  * On non-Windows with `version: "rust"` → dispatches to the Rust server (`rust_server_v1_0_0.start_tokio_server`).
  * Otherwise runs the **Python** asyncio server.
* **Host/port precedence**

  * **Rust backend**: uses `server_config["host"]`/`["port"]` if present; otherwise falls back to `run(host, port)`.
  * **Python backend**: uses the **`host`/`port` passed to `run()`** (the config's `host`/`port` are not applied in the Python path).
* Cleanly handles cancellation and shutdown.

#### `async def run_server(host: str = '127.0.0.1', port: int = 8888)`

Async entry for **Python** backend. Binds and `serve_forever()`.

#### `async def handle_client(reader, writer)`

* Reads lines from a client.
* Broadcasts a JSON envelope to all other clients:

  ```python
  {"remote_addr": "<ip:port>", "content": "<line-without-trailing-\\n>"}
  ```
* On disconnect, cleans up and (best effort) warns the client.

#### `def set_termination_signals() -> None`

Installs SIGINT/SIGTERM handlers (non-Windows).

#### `def shutdown() -> None`

Cancels all loop tasks to drive a clean exit.

---

## Rust backend notes

* Imported as `rust_server_v1_0_0` (PyO3 module). Build and ship it alongside the Python package.
* Implements: backpressure monitor, per-client rate limiting, idle timeout, quarantine list, and graceful shutdown.
* Emits structured logs when `logger.enable_json_log` is true (with optional field pruning via `logger.log_keys`).

---

## Compatibility & gotchas

* **Windows**: Rust backend not available; Python backend runs even if `version: "rust"`.
* **Idle listeners** (Rust): If a client only receives and never sends, it will hit `client_timeout_secs` unless you:

  * send a periodic heartbeat; or
  * set `client_timeout_secs: null`.
* **Disconnect ⇒ Quarantine** (Rust): Force-disconnected clients are temporarily banned; reconnect attempts are ignored during cooldown.
* **Backpressure signal** (Rust): Thresholds are compared to *fan-out size* (how many peers would receive the message). Tune thresholds relative to expected room size.

---

<p align="center">
  <a href="../server.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.server</b></code></a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="./configs.md">Next: <code style="background: transparent;">Summoner<b>.server</b></code> configuration guide &raquo;</a>
</p>
