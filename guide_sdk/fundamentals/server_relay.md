# Summoner Server Configuration (Local Deployment)

> This page focuses on configuration and parameterization needed to run a Summoner server locally. Routing and higher-level orchestration are covered elsewhere.

<p align="center">
  <img width="240px" src="../../assets/img/summoner_fund_server_rounded.png" />
</p>

## Philosophy: Servers Are Relays

Summoner servers act as untrusted relays. They accept TCP connections, read input one line at a time, and rebroadcast each line to all other connected clients. Validation, authentication, and message integrity live at the edges in your agents and their handshakes. The server keeps the pipe open, applies fair-use controls, and emits logs so you can see what is happening.

The wire format is intentionally simple: the protocol is line based, so each payload should end with `\n`. If a client forgets the trailing newline, the server adds it when broadcasting. Broadcasts exclude the original sender, which means every client receives the message set it did not originate and must decide what to process or ignore.

Each outbound frame is a single JSON line with a trailing `\n`, carrying the sender’s `remote_addr` and the original `content`. E.g.: 
```python
'{"remote_addr":"<ip:port>","content":"<line minus trailing \\n>"}\n'
```


> [!NOTE]
> **Aurora preview.** In the Aurora update, **Rust** servers will be programmable to support dedicated discussions without broadcast. You will be able to route conversations per session or per pair, replacing the default broadcast relay when needed.

A few implementation details help with interactive workloads. The Rust server sets TCP_NODELAY to avoid Nagle aggregation, which reduces latency for small frames. The **Rust server** also rejects a second connection from the same socket address to prevent duplicate sessions during testing.

This configuration layer stays modest on purpose. It gives you control over fairness, resource use, and observability without hiding how the network behaves.



## Two Implementations: Python and Rust

There are two interchangeable implementations exposed through the same Python API:

* **Python server** built on `asyncio`. It is the default everywhere and the only option on Windows.
* **Rust server** built on Tokio via PyO3. It runs on Unix-like systems and is selected through configuration.

Both listen on a host and port, use line-delimited frames, and broadcast to all peers except the sender.

On Windows, the Rust implementation is unavailable; any config with `"version": "rust"` will fall back to the Python server.

## Running a Server

The minimal entrypoint is identical for both implementations:

```python
from summoner.server import SummonerServer

if __name__ == "__main__":
    myserver = SummonerServer(name="my_server")
    myserver.run()
```

This starts the Python server on `127.0.0.1:8888`.

To switch to the Rust implementation on Unix-like systems, pass a tiny inline config:

```python
myserver.run(config_dict={"version": "rust"})
```

Because a config can coexist with `.run(...)` arguments, it is important to know which values take effect. The next section explains all configuration sources and their precedence.


## Configuration Sources and Precedence

### Overview

Summoner accepts configuration from three places. Think of them as layers that resolve to one effective set of values at startup.

1. **Keyword arguments to `.run(...)`**
   Use these for quick experiments or when embedding the server inside a script. You can pass `host`, `port`, and optionally `config_path` or `config_dict`. Arguments are explicit and visible at call sites, which is helpful for small utilities and tests.

2. **`config_path`**
   A path to a JSON file. This is better for reproducible runs, sharing presets with teammates, and keeping settings under version control. The loader prints where it loaded from or that no file was found, which makes provenance clear in your logs.

3. **`config_dict`**
   A Python `dict` with the same keys you would put in JSON. This is the most direct way to inject settings programmatically. It is ideal for notebooks, launchers, or apps that synthesize config from a GUI. Because it is already an in-memory object, it bypasses file I/O and wins over `config_path`.


<details>
<summary><b>Deployment Tips</b> </summary>

  #### Precedence in practice

  * If you pass a **`config_dict`**, it is used and any `config_path` is ignored.
  * Else, if you pass a **`config_path`**, the file is loaded.
  * Else, built-in defaults apply.

  This resolution is intentional. A dict is the most explicit representation since your code constructs it. A file is next, because you named it. Defaults come last.
  
   #### Host and port resolution depend on the implementation

  * The **Python server** takes `host` and `port` only from `.run(host=..., port=...)`. If you also provide a config file or dict, the Python path still uses the arguments for binding. The `logger` section is applied from config.
  * The **Rust server** reads `host` and `port` from config when present. If they are missing, it falls back to the `.run(...)` arguments. The `logger` section and all `hyper_parameters` apply to Rust.

  There is no hot reload. Restart the process to apply changes. If you want to make changes safely during development, prefer small, isolated edits and restart quickly to confirm behavior.
  
   #### Platform note

  On Windows, the Rust implementation is unavailable. If you set `"version": "rust"`, the Python server runs instead. Keep this in mind when sharing configs across platforms.
  
   #### Data types and validation

  * `host` is a string. Examples: `"127.0.0.1"`, `"0.0.0.0"`.
  * `port` is an integer and must fit in an unsigned 16-bit range. Typical user ports are above 1024.
  * JSON does not allow comments, so keep files clean and minimal. If you want inline notes, generate the dict in Python where comments are allowed in code.
  
  ####  Operational guidance

  If you plan to switch between Python and Rust often, choose one of these patterns to avoid surprises:

  * Keep `host` and `port` only in `.run(...)` and omit them from the config file. Rust will use the arguments when the keys are absent, and Python already uses the arguments.
  * Or, keep `host` and `port` only in the config and call `.run()` without those arguments. This matches Rust cleanly. For Python, be explicit in your docs that it does not read these keys from config.

</details>


### How to Run With Each Source

#### Code-only, Python server

Use this when you just need a local relay and want zero external files.

```python
from summoner.server import SummonerServer
SummonerServer(name="local").run(host="127.0.0.1", port=8888)
```

This path ignores `host` and `port` in any config file or dict. It still honors the `logger` section if you also pass a config for logging.

#### File-based, Rust server

Use a file to capture a repeatable setup you can commit to your repo.

```python
from summoner.server import SummonerServer
SummonerServer(name="local").run(config_path="server_config.json")
```

Inside `server_config.json`, set `version` and optionally `host` and `port`:

```json
{
  "version": "rust",
  "host": "0.0.0.0",
  "port": 8888
}
```

If `host` or `port` are missing, Rust falls back to the `.run(...)` arguments if you provided any.

#### Dict-based, Rust server

Use a dict when a launcher or GUI assembles settings dynamically.

```python
from summoner.server import SummonerServer

cfg = {
    "version": "rust",
    "host": "127.0.0.1",
    "port": 9000,
    "logger": {"log_level": "INFO"},
    "hyper_parameters": {"rate_limit_msgs_per_minute": 600}
}
SummonerServer(name="local").run(config_dict=cfg)
```

A dict overrides a file if both are provided. For `host` and `port`, Rust reads them from the dict when present. Python still binds using the `.run(...)` arguments.

<details>
<summary><b>Deployment tips</b> </summary>

* Always log the source of truth. Keep the startup log line that shows whether a file was loaded or a dict was used. This avoids ambiguity when someone reproduces your run later.
* For LAN testing, widen `host` to `0.0.0.0` and pick a port above 1024. Pair this with a moderate `rate_limit_msgs_per_minute` in Rust so a single peer cannot saturate your session.
* When moving configs between machines, remember that file paths inside the `logger` section are relative to the working directory of the process. Prefer absolute paths for long-running services.
* If a setting appears not to take effect, check which implementation you are running and which layer won by precedence. Most confusion comes from expecting the Python path to read `host` and `port` from config.

</details>

## Config File Shape

Top-level keys you can set:

### `version`

Selects the implementation. Use `"python"` for the asyncio server or `"rust"` for the Tokio server. On Windows, `"rust"` is ignored and the Python server runs. Choose Rust when you need higher throughput or want rate limiting, backpressure, and quarantine controls from `hyper_parameters`.

### `host`, `port`

Bind address and TCP port. For Rust, these can come from the config; for Python they must be passed to `.run(host=..., port=...)`. Keep `127.0.0.1` for isolated tests. Use `0.0.0.0` to accept LAN connections. Prefer ports above `1024`. If these keys are omitted in Rust, the server falls back to the arguments you passed to `.run(...)`.

### `logger`

Configures logging for both implementations. Typical fields:

* `log_level` controls verbosity (`DEBUG`, `INFO`, etc.).
* `enable_console_log` and `enable_file_log` choose sinks; `log_file_path` sets a directory for files.
* `enable_json_log` emits structured logs useful for tooling.
* `date_format` sets timestamps.
* `log_keys` prunes logged message content to specific JSON keys for privacy.
  Keep console logs on while developing; add JSON file logs for longer runs you want to analyze.

**Compatibility:** Python honors rotation/styling fields like `console_log_format`, `log_format`, `max_file_size`, and `backup_count`; the current Rust server ignores these. The cross-implementation keys are `log_level`, `enable_console_log`, `enable_file_log`, `log_file_path`, `enable_json_log`, `date_format`, and `log_keys`.

### `hyper_parameters` (Rust only)

Advanced runtime controls for fairness and lifecycle. Common knobs:

* Throughput and fairness: `rate_limit_msgs_per_minute`, `backpressure_policy.*`, `throttle_delay_ms`, `flow_control_delay_ms`.
* Resource usage: `worker_threads`, internal channel capacities.
* Robustness: `client_timeout_secs`, `timeout_check_interval_secs`, `quarantine_*`, `accept_error_backoff_ms`.
  All fields are optional with safe defaults. For local work, the defaults are fine. For load tests, keep backpressure thresholds increasing (throttle < flow\_control < disconnect) and set `worker_threads` explicitly to match your CPU quota.


<details>
<summary><b>Examples (click me)</b> Minimal local dev configs:</summary>
<br>

1) Python server, no file needed: Runs with `.run()` defaults: host `127.0.0.1`, port `8888`.

2) Rust server, minimal file:
    ```json
    {
      "version": "rust"
    }
    ```

3) Rust server, explicit bind and quiet logs:
    ```json
    {
      "version": "rust",
      "host": "127.0.0.1",
      "port": 8888,
      "logger": {
        "log_level": "INFO",
        "enable_console_log": true
      }
    }
    ```

</details>

<br>

<details>
<summary><b>Example (click me)</b> Production-leaning local configs (Python & Rust):</summary>
<br>

**Python server (production-leaning)**

```json
{
  "version": "python",
  "logger": {
    "log_level": "INFO",
    "enable_console_log": true,
    "console_log_format": "\u001b[92m%(asctime)s\u001b[0m - \u001b[94m%(name)s\u001b[0m - %(levelname)s - %(message)s",
    "enable_file_log": true,
    "enable_json_log": true,
    "log_file_path": "./logs",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "max_file_size": 2000000,
    "backup_count": 5,
    "date_format": "%Y-%m-%dT%H:%M:%S.%6fZ",
    "log_keys": ["route", "type", "id"]
  }
}
```

*Use `.run(host=..., port=...)` for binding; Python ignores `host` and `port` keys in config.*

**Rust server (production-leaning)**

```json
{
  "version": "rust",
  "host": "0.0.0.0",
  "port": 8888,

  "logger": {
    "log_level": "INFO",
    "enable_console_log": true,
    "enable_file_log": true,
    "log_file_path": "./logs",
    "enable_json_log": true,
    "date_format": "%Y-%m-%dT%H:%M:%S.%6fZ",
    "log_keys": ["route", "type", "id"]
  },

  "hyper_parameters": {
    "worker_threads": 4,

    "rate_limit_msgs_per_minute": 600,
    "client_timeout_secs": 600,
    "timeout_check_interval_secs": 15,

    "accept_error_backoff_ms": 250,
    
    "connection_buffer_size": 512,
    "command_buffer_size": 128,
    "control_channel_capacity": 32,
    "queue_monitor_capacity": 256,

    "backpressure_policy": {
      "enable_throttle": true,
      "throttle_threshold": 200,
      "enable_flow_control": true,
      "flow_control_threshold": 600,
      "enable_disconnect": true,
      "disconnect_threshold": 1000
    },

    "throttle_delay_ms": 200,
    "flow_control_delay_ms": 800,

    "quarantine_cooldown_secs": 600,
    "quarantine_cleanup_interval_secs": 60
  }
}
```

</details>

<br>



# Parameter Reference by JSON Structure

The sections below follow the JSON structure. Each parameter has a clear purpose, suggested ranges, and relationships to others. When a parameter is Rust-only, it is noted explicitly.

## `version`

<details>
<summary>
<b>(Click to expand)</b>
</summary>
<br>

* **Type**: string
* **Allowed**: `"python"`, `"rust"`
* **Default**: `"python"` when omitted
* **Used by**: **Python/Rust** (on Windows, `"rust"` falls back to Python)

Selects the implementation. On Windows, `"rust"` is ignored and the Python server runs. Use `"rust"` on Unix-like systems when you want higher throughput or strict backpressure, rate limiting, and quarantine features.

**Reasonable values**

* Local development on one machine: `"python"` is fine.
* Load or fairness experiments: `"rust"` with `hyper_parameters` tuned.

</details>

## `host` and `port`

<details>
<summary>
<b>(Click to expand)</b>
</summary>

* **Type**: string, integer
* **Default**: `host="127.0.0.1"`, `port=8888`
* **Used by**: **Python** (from `.run(...)` args), **Rust** (from config when present, else `.run(...)`)

Bind address and port.

**Precedence**

* Python server uses `.run(host, port)`.
* Rust server reads from JSON if provided; otherwise `.run(host, port)`.

**Guidance**

* Keep `127.0.0.1` for isolated local testing.
* Use `0.0.0.0` to accept connections from other machines on your LAN.
* Choose ports above 1024 to avoid privileges.
* Avoid reusing ports that other services already occupy.

**Interactions**
Opening to `0.0.0.0` pairs naturally with a modest `rate_limit_msgs_per_minute` to avoid local floods from neighboring hosts.

</details>

## `logger` (applies to Python and Rust)

<details>
<summary>
<b>(Click to expand)</b>
</summary>

### `logger.log_level`

* **Type**: string
* **Default**: `"DEBUG"`
* **Used by**: **Python/Rust**

Controls verbosity. `"INFO"` is a calm baseline once things work. Use `"DEBUG"` temporarily during setup.

### `logger.enable_console_log`

* **Type**: bool
* **Default**: `true`
* **Used by**: **Python/Rust**

Prints logs to stdout. Keep enabled for interactive use.

### `logger.enable_file_log` and `logger.log_file_path`

* **Type**: bool, string
* **Defaults**: `false`, `""`
* **Used by**: **Python/Rust**

Enable file logging and choose a directory for rotating files. For local runs, a relative directory like `./logs` is sufficient.

**Interaction**
File logs pair well with `logger.enable_json_log=true` when you plan to parse logs with tools.

### `logger.enable_json_log`

* **Type**: bool
* **Default**: `false`
* **Used by**: **Python/Rust**

When enabled, log entries are JSON objects. Useful for ingestion and filtering.

### `logger.date_format`

* **Type**: string
* **Default**: `"%Y-%m-%d %H:%M:%S.%3f"`
* **Used by**: **Python/Rust**

A standard `strftime` pattern. Increase fractional precision if you want finer timing.

### `logger.log_keys`

* **Type**: array of strings or null
* **Default**: `null`
* **Used by**: **Python/Rust**

When set, the logger prunes the client’s JSON content to these keys before recording it. This reduces accidental leakage of large payloads or private data in logs. If the incoming line is not JSON, the original text is logged.

**Reasonable values**
Start with a small set such as `["route", "type", "id"]`. Expand only when you need more detail.

### `logger.console_log_format` *(Python only)*

* **Type**: string
* **Default**: ANSI-colored pattern (see Python defaults)
* **Used by**: **Python**

Controls the console text layout and coloring for the Python logger’s stdout handler.

### `logger.log_format` *(Python only)*

* **Type**: string
* **Default**: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
* **Used by**: **Python**

Controls the file text layout (and JSON preamble fields) for the Python logger’s file handler.

### `logger.max_file_size` *(Python only)*

* **Type**: integer (bytes)
* **Default**: `1_000_000`
* **Used by**: **Python**

Maximum size before the Python `RotatingFileHandler` rolls the log file.

### `logger.backup_count` *(Python only)*

* **Type**: integer
* **Default**: `3`
* **Used by**: **Python**

How many rotated log files to retain with the Python `RotatingFileHandler`.

</details>

## `hyper_parameters` (Rust server only)

<details>
<summary>
<b>(Click to expand)</b> This object drives backpressure, fair use, lifecycle timing, and concurrency. If you are using the Python server exclusively, you can skip this section.
</summary>

### `worker_threads`

* **Type**: integer
* **Default**: number of CPU cores minus one, at least one
* **Used by**: **Rust**

Tokio worker threads for scheduling tasks. For local work, the default is appropriate. If you constrain CPU in a container, set this explicitly to match the quota.

**Interaction**
Higher thread counts allow more simultaneous slow clients without stalling. It does not increase single-connection throughput.

**Reasonable values**
`1` on very small machines. `cores−1` on desktops. Fixed small integers in containers.

### `client_timeout_secs`

* **Type**: integer or null
* **Default**: `300`
* **Used by**: **Rust**

Disconnect a client after this period of inactivity. When `null`, idle clients are never disconnected.

**Beginner insight**
Idle timeouts keep the peer list healthy. A client that dies without closing the socket will otherwise linger until the OS notices.

**Reasonable values**
`300` to `900` for local development. Set to `null` if you are testing long silent periods.

### `timeout_check_interval_secs`

* **Type**: integer
* **Default**: `30`
* **Used by**: **Rust**

The cadence for checking idle clients. Shorter intervals discover dead connections sooner at the cost of a few more timer wakeups.

**Combination**
For `client_timeout_secs=600`, an interval of `15` or `30` is typical.

### `rate_limit_msgs_per_minute`

* **Type**: integer
* **Default**: `300`
* **Used by**: **Rust**

Per-client rate limit. Exceeding it produces a warning to that client and suppresses the broadcast of the offending message.

**Beginner insight**
Rate limits cap sender aggressiveness. Backpressure decisions handle receiver saturation. They solve different problems.

**Reasonable values**
`300` for text-like traffic. Increase for small telemetry frames. Decrease if a single client tends to flood your local tests.

### Channel capacities

<details>
<summary>
<b>(Click to expand)</b> These are internal queues. They prevent noisy components from blocking others.
</summary>

* `connection_buffer_size`

  * **Type**: integer,
  * **Default**: `128`
  * **Used by**: **Rust**

  Capacity for backpressure reports. Not the OS accept backlog.

* `command_buffer_size`

  * **Type**: integer,
  * **Default**: `32`
  * **Used by**: **Rust**

  Capacity for backpressure commands delivered to the accept loop.

* `control_channel_capacity`

  * **Type**: integer,
  * **Default**: `8`
  * **Used by**: **Rust**

  Per-client queue for control commands like Throttle and FlowControl.

* `queue_monitor_capacity`

  * **Type**: integer,
  * **Default**: `100`
  * **Used by**: **Rust**

  Per-client queue where broadcast tasks report their current fan-out.

**Reasonable values**
Keep these modest in local runs. Increase only if you observe warnings about full channels.

**Interaction**
Raising `queue_monitor_capacity` without adjusting `backpressure_policy.*_threshold` changes when throttling kicks in because the system sees more outstanding sends.

</details>

### Backpressure policy

<details>
<summary>
<b>(Click to expand)</b> <code>backpressure_policy</code> is a nested object that defines when the server slows or disconnects talkative peers. Three mechanisms exist, in order of severity.
</summary>

#### `backpressure_policy.enable_throttle` and `throttle_threshold`

* **Types**: bool, integer
* **Defaults**: `true`, `100`
* **Used by**: **Rust**

Throttling introduces a small processing delay for the sender whenever the broadcast fan-out grows beyond the threshold. It reduces sender pace without pausing reads.

#### `throttle_delay_ms`

* **Type**: integer
* **Default**: `200`
* **Used by**: **Rust**

Duration of the throttling pause when applied.

#### `backpressure_policy.enable_flow_control` and `flow_control_threshold`

* **Types**: bool, integer
* **Defaults**: `true`, `300`
* **Used by**: **Rust**

Flow control pauses the sender’s reads for a longer period. Use this when throttling alone cannot keep queues small.

#### `flow_control_delay_ms`

* **Type**: integer
* **Default**: `1000`
* **Used by**: **Rust**

Duration of the flow-control pause.

#### `backpressure_policy.enable_disconnect` and `disconnect_threshold`

* **Types**: bool, integer
* **Defaults**: `true`, `500`
* **Used by**: **Rust**

Forced disconnect removes the client and places its address in quarantine.

**Beginner insight**
Think of these as three gates. Throttle is gentle. Flow control is firmer. Disconnect is a circuit breaker that protects the rest of the room.

**Consistent combinations**
Choose thresholds in increasing order. A practical pattern:

* `throttle_threshold` < `flow_control_threshold` < `disconnect_threshold`
* Example: `100`, `300`, `500`

Shorten `throttle_delay_ms` before raising thresholds if interactions feel sluggish.

</details>

### Quarantine

<details>
<summary>
<b>(Click to expand)</b> A quarantined address is temporarily prevented from reconnecting, which avoids immediate reconnect storms after a forced disconnect.
</summary>

#### `quarantine_cooldown_secs`

* **Type**: integer
* **Default**: `300`
* **Used by**: **Rust**

How long the address remains banned after disconnect.

#### `quarantine_cleanup_interval_secs`

* **Type**: integer
* **Default**: `60`
* **Used by**: **Rust**

How often the server removes expired bans.

**Reasonable values**
Keep the cooldown short during local experiments so you can reconnect quickly. For stress tests, a longer cooldown simplifies observation.

</details>

### Accept loop backoff

<details>
<summary>
<b>(Click to expand)</b> 
</summary>

#### `accept_error_backoff_ms`

* **Type**: integer
* **Default**: `100`
* **Used by**: **Rust**

Sleep duration after a failed `accept`. It gives the OS room to recover when the process hits resource limits like file descriptors.

**Beginner insight**
A transient pause after errors prevents tight retry loops that produce noisy logs and little progress.

</details>

</details>

<br>


# Putting It Together Locally

A simple way to deploy locally is to start with defaults, verify that messages flow between two clients, then layer controls:

1. Keep `host="127.0.0.1"`, `port=8888`.
2. Switch to the Rust implementation by adding a minimal config with `version="rust"`.
3. Enable `logger.enable_json_log=true` if you want structured logs.
4. Set `rate_limit_msgs_per_minute` to a comfortable ceiling.
5. Choose consistent backpressure thresholds following the increasing-order rule.
6. Set `client_timeout_secs` high enough that interactive pauses do not cause disconnects.

If you widen `host` to `0.0.0.0`, keep rate limiting and backpressure enabled so a single peer cannot monopolize the server.



<p align="center">
  <a href="index.md">&laquo; Previous: The Zen of Summoner </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="client_agent.md">Next: Clients and Agents &raquo;</a>
</p>
