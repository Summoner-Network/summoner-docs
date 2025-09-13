# <code style="background: transparent;">Summoner<b>.server</b></code> configuration guide

This page documents **every** server setting with practical advice, client interplay, and examples.

> **Loading & precedence**
>
> * Pass `config_dict` directly to `server.run(...)`, or point `config_path` at a JSON file.
> * **Backend selection**: `version: "python" | "rust"`. On Windows, Rust is unavailable.
> * **Host/Port precedence**:
>
>   * **Rust backend**: prefers `config.host` / `config.port`; falls back to the arguments of `run(host, port)`.
>   * **Python backend**: uses `run(host, port)` only; `config.host/port` are ignored in Python path.

---

## Table of contents

* [Core](#core)

  * [`host`](#host)
  * [`port`](#port)
  * [`version`](#version)
* [Logger](#logger)

  * `log_level`, `enable_console_log`, `console_log_format`,
    `enable_file_log`, `enable_json_log`, `log_file_path`, `log_format`,
    `max_file_size`, `backup_count`, `date_format`, `log_keys`
* [Hyper parameters](#hyper-parameters)

  * `connection_buffer_size`, `command_buffer_size`,
    `control_channel_capacity`, `queue_monitor_capacity`,
    `client_timeout_secs`, `rate_limit_msgs_per_minute`,
    `timeout_check_interval_secs`, `accept_error_backoff_ms`,
    `quarantine_cooldown_secs`, `quarantine_cleanup_interval_secs`,
    `throttle_delay_ms`, `flow_control_delay_ms`, `worker_threads`
* [Backpressure policy](#backpressure-policy)

  * `enable_throttle`, `throttle_threshold`,
    `enable_flow_control`, `flow_control_threshold`,
    `enable_disconnect`, `disconnect_threshold`
* [Tuning recipes](#tuning-recipes)
* [Complete example](#complete-example-config)

---

## Core

### `host`

* **Type**: `string` (e.g. `"127.0.0.1"` or `"0.0.0.0"`)
* **Applies**: Python & Rust (see precedence note above)
* **Meaning**: IP/hostname to bind the server to.
* **Client interplay**: Clients must connect to this address.
* **Example**

  ```json
  { "host": "0.0.0.0", "port": 8888 }
  ```

### `port`

* **Type**: `integer` (e.g. `8888`)
* **Applies**: Python & Rust
* **Meaning**: TCP port to listen on.

### `version`

* **Type**: `"python"` | `"rust"`
* **Meaning**: Select backend implementation.
* **Windows**: Always falls back to Python backend.

---

## Logger

### `log_level`

* **Type**: `"DEBUG"|"INFO"|"WARNING"|"ERROR"|"CRITICAL"`
* **Default**: `"INFO"`
* **Tip**: Use `"DEBUG"` only in short bursts; it can be chatty under load.

### `enable_console_log`

* **Type**: `boolean`
* **Default**: `true`
* **Meaning**: Print logs to stdout (pretty format).

### `console_log_format`

* **Type**: `string`
* **Meaning**: printf-style template; ANSI coloring allowed.
* **Example**

  ```json
  "console_log_format": "\u001b[92m%(asctime)s\u001b[0m - \u001b[94m%(name)s\u001b[0m - %(levelname)s - %(message)s"
  ```

### `enable_file_log`

* **Type**: `boolean`
* **Meaning**: Write rotating logs to disk.

### `enable_json_log`

* **Type**: `boolean`
* **Meaning**: Emit structured (JSON) log lines.
* **Rust extras**: When `true`, inbound payloads can be field-pruned via `log_keys`.

### `log_file_path`

* **Type**: `string (directory)`
* **Meaning**: Where to store rotated logs.

### `log_format`

* **Type**: `string`
* **Meaning**: File log format (ignored if `enable_json_log` is true).

### `max_file_size`, `backup_count`, `date_format`

* **Type**: `int`, `int`, `string`
* **Meaning**: Rotation size, retention count, timestamp formatting.

### `log_keys`

* **Type**: `null | [] | [string, ...]`
* **Default**: `null` (log full JSON content)
* **Rust backend behavior**: Server parses the **client’s JSON `content`** once, prunes to the listed keys for logging, but **broadcasts the original content unchanged**.
* **Examples**

  * Full payload:

    ```json
    "enable_json_log": true, "log_keys": null
    ```
  * No payload (metadata only):

    ```json
    "enable_json_log": true, "log_keys": []
    ```
  * Only a subset:

    ```json
    "enable_json_log": true, "log_keys": ["msg_id", "type", "user_id"]
    ```

---

## Hyper parameters

> ℹ️ Name mapping (Rust internals):
>
> * `client_timeout_secs` → rust `client_timeout` (seconds)
> * `rate_limit_msgs_per_minute` → rust `rate_limit` (msgs/min)

### `connection_buffer_size`

* **Type**: `int` · **Default**: `128` · **Applies**: Rust
* **Meaning**: Channel capacity for client → backpressure monitor reports (fan-out sizes).
* **When to raise**: Many concurrent broadcasters / large rooms.

### `command_buffer_size`

* **Type**: `int` · **Default**: `32` · **Applies**: Rust
* **Meaning**: Buffer for backpressure commands (Throttle/FlowControl/Disconnect).

### `control_channel_capacity`

* **Type**: `int` · **Default**: `8` · **Applies**: Rust
* **Meaning**: Per-client control channel depth.

### `queue_monitor_capacity`

* **Type**: `int` · **Default**: `100` · **Applies**: Rust
* **Meaning**: Local queue where a client stages its outgoing fan-out size before reporting.
* **Tip**: Raise if room size changes rapidly.

### `client_timeout_secs`

* **Type**: `int | null` · **Default**: `300` · **Applies**: Rust
* **Meaning**: Disconnect a client if it hasn’t sent anything for this many seconds.
* **Client tip**: For receive-only clients, either send a heartbeat or set to `null`.

### `rate_limit_msgs_per_minute`

* **Type**: `int` · **Default**: `300` · **Applies**: Rust
* **Meaning**: Per-client max messages/minute. Excess messages get a warning and are **not** broadcast.
* **Client interplay**: High `concurrency_limit` + bursts? Consider increasing this.

### `timeout_check_interval_secs`

* **Type**: `int` · **Default**: `30` · **Applies**: Rust
* **Meaning**: How often idle checks run.

### `accept_error_backoff_ms`

* **Type**: `int` · **Default**: `100` · **Applies**: Rust
* **Meaning**: Sleep after an `accept()` error to avoid hot loops.

### `quarantine_cooldown_secs`

* **Type**: `int` · **Default**: `300` · **Applies**: Rust
* **Meaning**: After policy-driven disconnect, the client’s address is **banned** for this long.

### `quarantine_cleanup_interval_secs`

* **Type**: `int` · **Default**: `60` · **Applies**: Rust
* **Meaning**: Periodic sweep to remove expired quarantines.

### `throttle_delay_ms`

* **Type**: `int` · **Default**: `200` · **Applies**: Rust
* **Meaning**: Delay per **Throttle** command. Smooths spikes.

### `flow_control_delay_ms`

* **Type**: `int` · **Default**: `1000` · **Applies**: Rust
* **Meaning**: Longer pause per **FlowControl** command.

### `worker_threads`

* **Type**: `int` · **Default**: `num_cores - 1` · **Applies**: Rust
* **Meaning**: Tokio worker threads. Tune only with profiling data.

---

## Backpressure policy

Thresholds compare against **current fan-out size** (how many peers would receive a message *now*). That’s a practical proxy for queued work.

### `enable_throttle`

* **Type**: `boolean` · **Default**: `true`
* **Meaning**: Inject small delays when over threshold.

### `throttle_threshold`

* **Type**: `int` · **Default**: `100`
* **Meaning**: Fan-out size that triggers **Throttle**.

### `enable_flow_control`

* **Type**: `boolean` · **Default**: `true`
* **Meaning**: Pause reads when over threshold.

### `flow_control_threshold`

* **Type**: `int` · **Default**: `300`
* **Meaning**: Fan-out size that triggers **FlowControl**.

### `enable_disconnect`

* **Type**: `boolean` · **Default**: `true`
* **Meaning**: Force disconnect (and quarantine) at extreme pressure.

### `disconnect_threshold`

* **Type**: `int` · **Default**: `500`
* **Meaning**: Fan-out size that triggers **Disconnect**.

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

## Tuning recipes

### Low-latency chat (fast typing; many small messages)

* **Server**

  * `rate_limit_msgs_per_minute`: 900–1200
  * `throttle_delay_ms`: 50–100
  * `flow_control_delay_ms`: 250–500
  * Backpressure thresholds: relatively high
* **Client**

  * `concurrency_limit`: 20–50
  * `batch_drain`: `true`

### High-throughput broadcast (many recipients)

* **Server**

  * Increase `connection_buffer_size`, `queue_monitor_capacity`
  * Backpressure thresholds scaled to expected room size
  * `enable_json_log: true` + `log_keys` for compact logs
* **Client**

  * Lower `concurrency_limit` if you see disconnects/quarantine

### Strict security / abuse resistance

* **Server**

  * `rate_limit_msgs_per_minute`: 60–120
  * `client_timeout_secs`: 120–180
  * Lower thresholds; `enable_disconnect: true`
  * `quarantine_cooldown_secs`: 900
* **Client**

  * Send heartbeats if mostly listening (or disable timeout)

---

## Complete example config

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

<p align="center">
  <a href="./server.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.server.server</b></code></a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="../server.md">Next: <code style="background: transparent;">Summoner<b>.server</b></code> &raquo;</a>
</p>
