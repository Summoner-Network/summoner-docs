# <code style="background: transparent;">Summoner<b>.server</b></code> configuration guide

This page explains how to configure `Summoner.server` in a way that is understandable to readers who do not want to study the implementation. Each setting is described by its purpose, behavior, default value, and the practical consequences of changing it.

A Summoner server is a TCP relay: clients connect to a host and port, send newline-delimited messages, and the server forwards messages to other connected clients. Most configuration exists to answer three operational questions:

1. Where does the server listen (`host`, `port`), and which backend runs it (`version`)?
2. What is recorded for observability (`logger`)?
3. How does the server stay stable under load (`hyper_parameters` and `hyper_parameters.backpressure_policy`)?

> [!NOTE]
> **Loading & precedence**
>
> * You can pass a configuration dictionary directly to `server.run(...)` as `config_dict`, or provide a JSON file path via `config_path`.
> * The server runs using either the Python backend (asyncio) or the Rust backend (Tokio wrapped by Python).
> * **Host/Port precedence**
>
>   * **Rust backend**: prefers the values in the config file (`host`, `port`) and falls back to the arguments of `run(host, port)` when not present.
>   * **Python backend**: binds to `run(host, port)`; top-level `host` and `port` in the config are not used for binding in the Python path.

## Table of contents

* [Core](#core)

  * [`host`](#host)
  * [`port`](#port)
  * [`version`](#version)

* [Logger](#logger)

  * [What the logger emits](#what-the-logger-emits)
  * [`logger.log_level`](#log_level)
  * [`logger.enable_console_log`](#enable_console_log)
  * [`logger.console_log_format`](#console_log_format)
  * [`logger.enable_file_log`](#enable_file_log)
  * [`logger.log_file_path`](#log_file_path)
  * [`logger.enable_json_log`](#enable_json_log)
  * [`logger.log_format`](#log_format)
  * [`logger.date_format`](#date_format)
  * [`logger.max_file_size`](#max_file_size)
  * [`logger.backup_count`](#backup_count)
  * [`logger.log_keys`](#log_keys)

* [Hyper parameters](#hyper-parameters)

  * [What hyper parameters control](#what-hyper-parameters-control)
  * [`hyper_parameters.connection_buffer_size`](#connection_buffer_size)
  * [`hyper_parameters.command_buffer_size`](#command_buffer_size)
  * [`hyper_parameters.control_channel_capacity`](#control_channel_capacity)
  * [`hyper_parameters.queue_monitor_capacity`](#queue_monitor_capacity)
  * [`hyper_parameters.rate_limit_msgs_per_minute`](#rate_limit_msgs_per_minute)
  * [`hyper_parameters.client_timeout_secs`](#client_timeout_secs)
  * [`hyper_parameters.timeout_check_interval_secs`](#timeout_check_interval_secs)
  * [`hyper_parameters.accept_error_backoff_ms`](#accept_error_backoff_ms)
  * [`hyper_parameters.quarantine_cooldown_secs`](#quarantine_cooldown_secs)
  * [`hyper_parameters.quarantine_cleanup_interval_secs`](#quarantine_cleanup_interval_secs)
  * [`hyper_parameters.throttle_delay_ms`](#throttle_delay_ms)
  * [`hyper_parameters.flow_control_delay_ms`](#flow_control_delay_ms)
  * [`hyper_parameters.worker_threads`](#worker_threads)

* [Backpressure policy](#backpressure-policy)

  * [How backpressure protects the server](#how-backpressure-protects-the-server)
  * [`hyper_parameters.backpressure_policy.enable_throttle`](#enable_throttle)
  * [`hyper_parameters.backpressure_policy.throttle_threshold`](#throttle_threshold)
  * [`hyper_parameters.backpressure_policy.enable_flow_control`](#enable_flow_control)
  * [`hyper_parameters.backpressure_policy.flow_control_threshold`](#flow_control_threshold)
  * [`hyper_parameters.backpressure_policy.enable_disconnect`](#enable_disconnect)
  * [`hyper_parameters.backpressure_policy.disconnect_threshold`](#disconnect_threshold)

* [Tuning recipes](#tuning-recipes)

* [Complete example](#complete-example-config)

## Core

### `host`

<details>
<summary><b>Purpose:</b> The parameter <code>host</code> is the network address the server listens on.</summary>

#### Typical values and meaning

* `"127.0.0.1"` means only local clients can connect (development on one machine).
* `"0.0.0.0"` means the server accepts connections from other machines that can reach it (LAN or cloud deployment).

#### Default if omitted

If `host` is not provided, the default is `"127.0.0.1"`.

#### Example

```json
{ "host": "0.0.0.0", "port": 8888 }
```

</details>

### `port`

<details>
<summary><b>Purpose:</b> The parameter <code>port</code> is the TCP port number the server listens on.</summary>

#### Default if omitted

If `port` is not provided, the default is `8888`.

</details>

### `version`

<details>
<summary><b>Purpose:</b> The parameter <code>version</code> selects which server backend runs.</summary>

#### Values

* `"python"` selects the Python asyncio server.
* `"rust"` selects the newest available Rust backend installed in the environment.
* `"rust_vX.Y.Z"` pins to a specific Rust backend version when that module is installed (for example `"rust_v1.1.0"`).

#### Platform behavior

On Windows, the server runs the Python backend.

</details>

## Logger

Logging is how the server answers basic production questions such as: "Who connected?", "What load did the server observe?", "Which clients are being throttled?", and "Why did a client disconnect?".

The configuration controls two destinations:

1. Console logs (visible in terminal output or container logs)
2. File logs (persisted on disk)

A key operational property is that the Rust backend initializes the logger once per process. Changing the config values requires restarting the server process to change logging behavior.

### What the logger emits

The Rust backend formats console logs as readable lines containing:

* a timestamp
* the server name
* the log level
* the message

For file logs, the Rust backend supports:

* plain text lines, or
* JSON Lines (one JSON object per line), where the `message` field is itself either JSON (if the logged string parses as JSON) or a string (if it does not).

This makes it possible to ingest logs into standard enterprise tooling while also keeping console output readable.

<a id="log_level"></a>

### `logger.log_level`

<details>
<summary><b>Purpose:</b> The parameter <code>log_level</code> sets the minimum severity that is recorded.</summary>

#### Idea

Config path: `logger.log_level`.

The parameter `log_level` determines how "chatty" the server is allowed to be in logs. Higher verbosity is helpful during debugging, while lower verbosity keeps production logs smaller.

We recommend choosing the lowest verbosity that still answers your operational questions.

* Use `"INFO"` for most deployments (connections, disconnections, warnings, backpressure actions).
* Use `"DEBUG"` for short investigations (it can generate a lot of volume under load).
* Use `"WARNING"` or `"ERROR"` only if you already have good observability elsewhere and want to minimize log volume.

#### Default if omitted

If not provided, the default is `"DEBUG"`.

#### Common values

`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`

</details>

<a id="enable_console_log"></a>

### `logger.enable_console_log`

<details>
<summary><b>Purpose:</b> The parameter <code>enable_console_log</code> turns console logging on or off.</summary>

#### Idea

Config path: `logger.enable_console_log`.

The parameter `enable_console_log` determines whether the server prints logs to the terminal (useful for local runs and container logs).

Keep this enabled in local development and in containerized environments where stdout/stderr are collected by the platform. In long-running services with dedicated file shipping, you may choose to disable console logs to reduce noise.

#### Default if omitted

If not provided, the default is `true`.

</details>

<a id="console_log_format"></a>

### `logger.console_log_format`

<details>
<summary><b>Purpose:</b> The parameter <code>console_log_format</code> controls the console log line format for the Python backend.</summary>

#### Idea

Config path: `logger.console_log_format`.

The parameter `console_log_format` determines how console logs are formatted on the Python backend (colors, timestamp layout, and so on).

If you are using the Python backend, this is where you tune readability (colors, fields, timestamp layout). If you are using the Rust backend, this setting is typically left in the config for consistency across environments, even though it does not affect Rust console output.

#### Default if omitted

If omitted, the Python backend uses its default formatting.

#### Rust backend behavior

The Rust backend prints a fixed console format (timestamp, name, level, message). The `console_log_format` string does not change Rust console formatting.

</details>

<a id="enable_file_log"></a>

### `logger.enable_file_log`

<details>
<summary><b>Purpose:</b> The parameter <code>enable_file_log</code> turns file logging on or off.</summary>

#### Idea

Config path: `logger.enable_file_log`.

The parameter `enable_file_log` determines whether the server also writes logs to disk (useful for long-running deployments where terminal logs are not retained).

Enable file logging when you want durable logs on disk (for example, for post-incident review, auditing, or environments where stdout is not retained). If you already rely on centralized logging from console output, you may keep this disabled.

#### Default if omitted

If not provided, the default is `false`.

</details>

<a id="log_file_path"></a>

### `logger.log_file_path`

<details>
<summary><b>Purpose:</b> The parameter <code>log_file_path</code> is the directory where log files are written when <code>enable_file_log</code> is <code>true</code>.</summary>

#### Idea

Config path: `logger.log_file_path`.

The parameter `log_file_path` determines where log files are written if file logging is enabled. If this is empty, the server writes the log file next to where it was started.

Use an explicit path in production so logs end up where your tooling expects them (for example, a mounted volume or a standard system log directory). If you run multiple servers on one machine, prefer separate directories per service or per environment.

#### Default if omitted

If omitted or set to an empty string, the Rust backend writes a log file in the current working directory.

#### File naming

The file name is derived from the server name, with dots replaced by underscores.

</details>

<a id="enable_json_log"></a>

### `logger.enable_json_log`

<details>
<summary><b>Purpose:</b> The parameter <code>enable_json_log</code> selects whether file logs are written as JSON Lines or as plain text.</summary>

#### Idea

Config path: `logger.enable_json_log`.

The parameter `enable_json_log` determines whether file logs are written as structured JSON lines instead of plain text. JSON logs are easier to search, parse, and ingest into centralized logging systems.

Enable JSON logs when logs are intended for ingestion (ELK, Datadog, Splunk, CloudWatch, etc.). Keep plain text logs when logs are primarily read by humans on the host.

#### Default if omitted

If not provided, the default is `false`.

#### Practical effect

JSON logs are the preferred format when logs are ingested into a centralized logging system, because fields like timestamp, level, and server name become structured data.

</details>

<a id="log_format"></a>

### `logger.log_format`

<details>
<summary><b>Purpose:</b> The parameter <code>log_format</code> controls the file log line format for the Python backend when JSON logging is not enabled.</summary>

#### Idea

Config path: `logger.log_format`.

The parameter `log_format` determines how file logs are formatted on the Python backend when JSON logging is not enabled.

Tune this only if you are using the Python backend and you want file logs to match an existing organization standard. For the Rust backend, keep this value for config consistency across backends.

#### Default if omitted

If omitted, the Python backend uses its default formatting.

#### Rust backend behavior

The Rust backend uses a fixed format for plain text file logs.

</details>

<a id="date_format"></a>

### `logger.date_format`

<details>
<summary><b>Purpose:</b> The parameter <code>date_format</code> controls timestamp formatting for console and file logs.</summary>

#### Idea

Config path: `logger.date_format`.

The parameter `date_format` determines how timestamps look in logs (for example, including milliseconds).

If you correlate server logs with other systems (load balancers, clients, infrastructure), consider using a timestamp format with millisecond precision and stable ordering. If you rely on log ingestion, choose a format that your pipeline parses reliably.

#### Default if omitted

If not provided, the default is `"%Y-%m-%d %H:%M:%S.%3f"` (date, time, and milliseconds).

</details>

<a id="max_file_size"></a>

### `logger.max_file_size`

<details>
<summary><b>Purpose:</b> The parameter <code>max_file_size</code> configures log rotation size for the Python backend.</summary>

#### Idea

Config path: `logger.max_file_size`.

The parameter `max_file_size` determines the maximum size of a log file before rotation on the Python backend.

Set this based on how quickly logs grow in your environment. For high-traffic services, a smaller rotation size avoids very large files but increases the number of rotated files created.

#### Default if omitted

If omitted, the Python backend uses its default rotation size.

#### Rust backend behavior

The Rust backend writes to a single file per server name using the configured path. Rotation by file size is not applied by the Rust backend.

</details>

<a id="backup_count"></a>

### `logger.backup_count`

<details>
<summary><b>Purpose:</b> The parameter <code>backup_count</code> configures how many rotated log files are kept by the Python backend.</summary>

#### Idea

Config path: `logger.backup_count`.

The parameter `backup_count` determines how many rotated log files are kept on the Python backend.

Choose a retention count that matches your operational needs (for example, keeping enough history to cover the typical time between incidents and detection). If you ship logs elsewhere, you can keep this low.

#### Default if omitted

If omitted, the Python backend uses its default retention count.

#### Rust backend behavior

The Rust backend does not apply size-based rotation or retention counts.

</details>

<a id="log_keys"></a>

### `logger.log_keys`

<details>
<summary><b>Purpose:</b> The parameter <code>log_keys</code> reduces the amount of message content written to logs by keeping only selected fields.</summary>

#### Idea

Config path: `logger.log_keys`.

The parameter `log_keys` controls how much of the message content is written to disk when JSON file logging is enabled. This is commonly used to keep logs lightweight or avoid writing large or sensitive payloads.

Use this setting to balance observability with volume and confidentiality:

* If payloads can be large, `log_keys` keeps logs small and stable.
* If payloads can contain sensitive data, `log_keys: []` can prevent accidental persistence of content.
* If you need request tracing, include stable identifiers such as message IDs, user IDs, or types.

#### Default if omitted

If not provided, the default is `null`, which means "do not filter".

> [!TIP]
> **[For developers] How filtering works**
>
> When filtering is enabled, the server keeps:
>
> * `_version` (if present)
> * selected keys inside `_payload` and `_type`
>
> This preserves stable identifiers and message classification while avoiding large or sensitive payload fields in logs.

#### Examples

```json
"log_keys": null
```

Logs full content.

```json
"log_keys": []
```

Logs only minimal structure (useful when payloads are sensitive or very large).

```json
"log_keys": ["msg_id", "type", "user_id"]
```

Logs only the listed keys inside `_payload` and `_type`, plus `_version`.

</details>

## Hyper parameters

### What hyper parameters control

The `hyper_parameters` section contains the operational limits and timing constants that keep the server responsive under normal traffic and predictable under stress.

In practice, these settings control four things:

1. **How much short-term burstiness the server can absorb** (buffers).
2. **How much one client is allowed to consume** (rate limits and idle timeouts).
3. **How the server recovers from abnormal conditions** (accept backoff and quarantine).
4. **How strongly the server slows clients down when it needs to protect itself** (throttle and flow-control delays, plus runtime parallelism).

Most deployments can start with defaults. You typically adjust hyper parameters when you observe one of the following: dropped messages due to bursts, clients that are too noisy, high CPU usage, or frequent backpressure actions in otherwise expected usage.

<a id="connection_buffer_size"></a>

### `hyper_parameters.connection_buffer_size`

<details>
<summary><b>Purpose:</b> The parameter <code>connection_buffer_size</code> sets the capacity of the global buffer that stores per-client load reports flowing into the backpressure monitoring pipeline.</summary>

#### Idea

Config path: `hyper_parameters.connection_buffer_size`.

The parameter `connection_buffer_size` determines how many "this client is getting busy" updates the server can temporarily store while it decides whether to slow someone down. If this buffer fills up, the server may stop recording some of these busy updates.

If you expect large rooms or frequent bursts, increase this buffer so the server can continue "seeing" load changes while it is busy. If you keep this small, the backpressure monitor may miss some short spikes because updates are dropped when the buffer is full.

#### Default if omitted

If omitted, it defaults to the value `128`.

#### What it changes

Higher values allow more clients to report load at once during bursts. Lower values cause reports to be dropped earlier when the system is busy.

</details>

<a id="command_buffer_size"></a>

### `hyper_parameters.command_buffer_size`

<details>
<summary><b>Purpose:</b> The parameter <code>command_buffer_size</code> sets the capacity of the global buffer that stores backpressure actions emitted by the monitor before the main loop applies them.</summary>

#### Idea

Config path: `hyper_parameters.command_buffer_size`.

The parameter `command_buffer_size` determines how many "server reactions" can be queued up at once (examples: "slow this client down", "pause this client", "disconnect this client"). If this buffer fills up, some reactions may be delayed or not queued.

If you notice that backpressure actions are slow to take effect during bursts, increasing this buffer can help the server queue more reactions at once. If you keep it small, the monitor may be forced to skip or delay some actions during extreme spikes.

#### Default if omitted

If omitted, it defaults to the value `32`.

#### What it changes

Higher values allow more pending "slow down" or "disconnect" actions to queue during bursts. Lower values constrain how many actions can accumulate.

</details>

<a id="control_channel_capacity"></a>

### `hyper_parameters.control_channel_capacity`

<details>
<summary><b>Purpose:</b> The parameter <code>control_channel_capacity</code> sets the capacity of the per-client buffer used to deliver control signals to a specific client session task (throttle and flow control).</summary>

#### Idea

Config path: `hyper_parameters.control_channel_capacity`.

The parameter `control_channel_capacity` determines, per client, how many "slow down / pause" signals the server can stack up for that one client. If this fills up for a client, additional slow-down signals for that client may not get through until earlier ones are processed.

If a client oscillates between normal and overloaded conditions, a slightly larger buffer can keep control signals flowing smoothly. If this is too small, control signals may fail to enqueue when the client is already under pressure, which makes the response less consistent.

#### Default if omitted

If omitted, it defaults to the value `8`.

#### What it changes

Higher values allow multiple control signals to queue for a client under unstable load. Lower values make the control channel more immediate, but signals may be skipped if the client is already saturated.

</details>

<a id="queue_monitor_capacity"></a>

### `hyper_parameters.queue_monitor_capacity`

<details>
<summary><b>Purpose:</b> The parameter <code>queue_monitor_capacity</code> sets the capacity of the per-client buffer used to stage local load measurements before forwarding them into the global reporting buffer.</summary>

#### Idea

Config path: `hyper_parameters.queue_monitor_capacity`.

The parameter `queue_monitor_capacity` determines, per client, how many "how busy am I?" measurements can be temporarily stored before being forwarded to the server's global slowdown logic. If this fills up, some measurements may be skipped until the buffer drains.

This buffer mainly matters during short bursts. If you expect clients to broadcast to many peers in bursts, increasing it can help preserve a smoother stream of load measurements. If it is too small, the server may skip some measurements while the client is busy, which reduces the monitor's visibility into short spikes.

#### Default if omitted

If omitted, it defaults to the value `100`.

#### What it changes

Higher values allow each client task to record short spikes in load without blocking itself. Lower values reduce memory use, but measurements may be skipped during spikes.

</details>

<a id="rate_limit_msgs_per_minute"></a>

### `hyper_parameters.rate_limit_msgs_per_minute`

<details>
<summary><b>Purpose:</b> The parameter <code>rate_limit_msgs_per_minute</code> sets a per-client message rate limit; if a client exceeds this rate, the server warns the client and does not broadcast excess messages.</summary>

#### Idea

Config path: `hyper_parameters.rate_limit_msgs_per_minute`.

The parameter `rate_limit_msgs_per_minute` determines how many messages one client is allowed to send per minute. If a client goes above this, the server warns them and ignores extra messages instead of letting them flood everyone.

Set this based on the expected client behavior. For interactive chat, users can legitimately send bursts. For automated clients, a misconfiguration can generate sustained high rates. This limit provides a predictable ceiling on how much one client can consume.

#### Default if omitted

If omitted, it defaults to the value `300`.

</details>

<a id="client_timeout_secs"></a>

### `hyper_parameters.client_timeout_secs`

<details>
<summary><b>Purpose:</b> The parameter <code>client_timeout_secs</code> disconnects clients that have been inactive for the specified number of seconds.</summary>

#### Idea

Config path: `hyper_parameters.client_timeout_secs`.

The parameter `client_timeout_secs` determines how long a client can stay silent before the server assumes it is idle and drops the connection (to avoid dead connections piling up).

Choose a timeout that matches your environment's connection patterns. In production, this prevents dead or abandoned connections from accumulating. If you have receive-only clients, ensure they send an occasional heartbeat, or set this to `null` if idle connections are expected and safe.

#### Default if omitted

If omitted, it defaults to the value `300`.

#### Special value

If set to `null`, inactivity timeout is disabled.

</details>

<a id="timeout_check_interval_secs"></a>

### `hyper_parameters.timeout_check_interval_secs`

<details>
<summary><b>Purpose:</b> The parameter <code>timeout_check_interval_secs</code> controls how often the server checks whether clients have been idle for too long.</summary>

#### Idea

Config path: `hyper_parameters.timeout_check_interval_secs`.

The parameter `timeout_check_interval_secs` determines how often the server checks for idle clients. A smaller value detects dead connections faster; a larger value reduces background checking work.

If you need faster cleanup of dead connections, lower this value. If you have extremely large numbers of clients and want to minimize periodic overhead, a higher value can be acceptable, at the cost of slower timeout enforcement.

#### Default if omitted

If omitted, it defaults to the value `30`.

</details>

<a id="accept_error_backoff_ms"></a>

### `hyper_parameters.accept_error_backoff_ms`

<details>
<summary><b>Purpose:</b> The parameter <code>accept_error_backoff_ms</code> controls how long the server waits after an accept error before retrying, to avoid a tight retry loop under system resource pressure.</summary>

#### Idea

Config path: `hyper_parameters.accept_error_backoff_ms`.

The parameter `accept_error_backoff_ms` determines how long the server waits after a failed "accept new connection" attempt before trying again. This prevents the server from spinning in a tight loop if the OS temporarily refuses new connections.

In normal operation, this value is rarely visible. It becomes relevant when the OS is under stress (file descriptor exhaustion, transient network issues). Keeping a small backoff prevents CPU burn during such events while still allowing recovery.

#### Default if omitted

If omitted, it defaults to the value `100`.

</details>

<a id="quarantine_cooldown_secs"></a>

### `hyper_parameters.quarantine_cooldown_secs`

<details>
<summary><b>Purpose:</b> The parameter <code>quarantine_cooldown_secs</code> controls how long a client address is blocked after a forced disconnect.</summary>

#### Idea

Config path: `hyper_parameters.quarantine_cooldown_secs`.

The parameter `quarantine_cooldown_secs` determines how long (in seconds) a disconnected client is temporarily blocked from reconnecting. This prevents a misbehaving client from instantly reconnecting and repeating the same overload.

If you are defending against buggy or abusive clients that reconnect immediately, increase this cooldown so the server has time to recover. If clients are trusted and disconnects are usually accidental, a shorter cooldown improves recovery time.

#### Default if omitted

If omitted, it defaults to the value `300`.

</details>

<a id="quarantine_cleanup_interval_secs"></a>

### `hyper_parameters.quarantine_cleanup_interval_secs`

<details>
<summary><b>Purpose:</b> The parameter <code>quarantine_cleanup_interval_secs</code> controls how often the server removes expired entries from the quarantine list.</summary>

#### Idea

Config path: `hyper_parameters.quarantine_cleanup_interval_secs`.

The parameter `quarantine_cleanup_interval_secs` determines how often (in seconds) the server cleans up expired blocks so clients can reconnect once their cooldown expires.

This is primarily an operational hygiene setting. A shorter interval removes expired entries more promptly; a longer interval reduces background work. Most deployments can keep the default.

#### Default if omitted

If omitted, it defaults to the value `60`.

</details>

<a id="throttle_delay_ms"></a>

### `hyper_parameters.throttle_delay_ms`

<details>
<summary><b>Purpose:</b> The parameter <code>throttle_delay_ms</code> controls the time added as a delay when throttling is applied; this is a gentle slowdown intended to smooth bursts.</summary>

#### Idea

Config path: `hyper_parameters.throttle_delay_ms`.

The parameter `throttle_delay_ms` determines how much delay (in milliseconds) the server adds when it throttles a client. This is the "speed bump" amount.

If you want the server to apply a light speed bump rather than a noticeable pause, keep this small. If clients are generating aggressive bursts, increasing this delay can reduce churn and help the system stabilize with less need for stronger actions.

#### Default if omitted

If omitted, it defaults to the value `200`.

</details>

<a id="flow_control_delay_ms"></a>

### `hyper_parameters.flow_control_delay_ms`

<details>
<summary><b>Purpose:</b> The parameter <code>flow_control_delay_ms</code> controls the time added as a pause when flow control is applied; this is a stronger slowdown intended to stop a client from overwhelming the server during high load.</summary>

#### Idea

Config path: `hyper_parameters.flow_control_delay_ms`.

The parameter `flow_control_delay_ms` determines how long (in milliseconds) the server pauses a client when flow control is triggered. This is a stronger brake than throttling.

This should generally be longer than `throttle_delay_ms`. If it is too short, flow control may not meaningfully reduce pressure. If it is too long, legitimate clients may experience noticeable latency spikes when the server enters protection mode.

#### Default if omitted

If omitted, it defaults to the value `1000`.

</details>

<a id="worker_threads"></a>

### `hyper_parameters.worker_threads`

<details>
<summary><b>Purpose:</b> The parameter <code>worker_threads</code> controls the number of worker threads used by the Rust runtime.</summary>

#### Idea

Config path: `hyper_parameters.worker_threads`.

The parameter `worker_threads` (default: `num_cores - 1`) determines how many CPU worker threads the Rust server uses to process work. More threads can help on busy machines, but it is usually best to keep this close to the default unless you are tuning with real load tests.

The default is usually appropriate. Increase this only if you have evidence that the server is CPU-bound and under-utilizing cores. Decrease it if you intentionally want the server to use fewer CPU resources on a shared machine.

#### Default if omitted

It defaults to "number of CPU cores minus one", with a minimum of 1.

</details>

## Backpressure policy

### How backpressure protects the server

The backpressure policy lives in the config at `hyper_parameters.backpressure_policy`.

Backpressure is the server's "automatic stability system". Its goal is to prevent a situation where one overloaded broadcast causes the server to accumulate too many pending tasks and memory allocations.

In plain terms, the server continuously estimates how much work it is about to create when forwarding a message. A message that must be forwarded to many other clients creates more work than a message forwarded to a few clients. When that estimated work exceeds configured thresholds, the server takes steps of increasing severity:

1. **Throttle**: inject a small delay for the sending client to slow the rate of work creation.
2. **Flow control**: inject a larger pause to more strongly limit the client.
3. **Disconnect**: as a last resort, remove the client and quarantine its address for a cooldown period.

In practice, the thresholds decide *when* each step becomes acceptable, and the delays decide *how strong* the slowdown feels.

The thresholds and the choice of steps are controlled by the parameters below.

<a id="enable_throttle"></a>

### `hyper_parameters.backpressure_policy.enable_throttle`

<details>
<summary><b>Purpose:</b> The parameter <code>enable_throttle</code> turns on the "gentle slowdown" step.</summary>

#### Idea

Config path: `hyper_parameters.backpressure_policy.enable_throttle`.

The parameter `enable_throttle` determines whether the server is allowed to use the "slow down" step. If this is on, the server can tell a client to slow down before doing anything harsher.

Enable this in most deployments. Throttling is a low-friction way to smooth bursts without disrupting client sessions. If you disable it, the server will rely more quickly on stronger measures (flow control and disconnect).

#### Default if omitted

If omitted, it defaults to the value `true`.

</details>

<a id="throttle_threshold"></a>

### `hyper_parameters.backpressure_policy.throttle_threshold`

<details>
<summary><b>Purpose:</b> The parameter <code>throttle_threshold</code> controls the load threshold at which throttling begins.</summary>

#### Idea

Config path: `hyper_parameters.backpressure_policy.throttle_threshold`.

The parameter `throttle_threshold` determines when the server considers a client "too busy" and starts slowing them down. Higher means the server tolerates more burstiness; lower means it reacts sooner.

Set this based on expected room size or fan-out. If it is too low, clients may be slowed down during normal operation. If it is too high, the server may postpone throttling until pressure is already severe.

#### Default if omitted

If omitted, it defaults to the value `100`.

</details>

<a id="enable_flow_control"></a>

### `hyper_parameters.backpressure_policy.enable_flow_control`

<details>
<summary><b>Purpose:</b> The parameter <code>enable_flow_control</code> turns on the stronger pause step.</summary>

#### Idea

Config path: `hyper_parameters.backpressure_policy.enable_flow_control`.

The parameter `enable_flow_control` determines whether the server is allowed to use the "temporary pause" step. If this is on, the server can tell a client to pause briefly so the system can catch up.

Enable this when you want a firm protection layer that prevents runaway load during spikes. If you disable it, the server will either keep throttling (if enabled) or jump directly to disconnect (if enabled) when thresholds are exceeded.

#### Default if omitted

If omitted, it defaults to the value `true`.

</details>

<a id="flow_control_threshold"></a>

### `hyper_parameters.backpressure_policy.flow_control_threshold`

<details>
<summary><b>Purpose:</b> The parameter <code>flow_control_threshold</code> controls the load threshold at which flow control begins.</summary>

#### Idea

Config path: `hyper_parameters.backpressure_policy.flow_control_threshold`.

The parameter `flow_control_threshold` determines when the server starts applying flow control (the pause step). This is usually set higher than the throttle threshold because it is a stronger response.

This is typically higher than `throttle_threshold`. A common approach is to treat throttling as early smoothing and flow control as hard braking. If these two thresholds are too close, the server will enter pause mode frequently, which can feel abrupt to clients.

#### Default if omitted

If omitted, it defaults to the value `300`.

</details>

<a id="enable_disconnect"></a>

### `hyper_parameters.backpressure_policy.enable_disconnect`

<details>
<summary><b>Purpose:</b> The parameter <code>enable_disconnect</code> turns on the last-resort disconnect step.</summary>

#### Idea

Config path: `hyper_parameters.backpressure_policy.enable_disconnect`.

The parameter `enable_disconnect` determines whether the server is allowed to disconnect a client when things get extreme. If this is on, the server can disconnect a client to protect itself and other clients.

Enable this if you need strong protection against extreme overload or abusive clients. If you disable disconnect, the server will try to recover using throttle and flow control alone, which can be acceptable in trusted environments but provides less isolation when a client is persistently disruptive.

#### Default if omitted

If omitted, it defaults to the value `true`.

</details>

<a id="disconnect_threshold"></a>

### `hyper_parameters.backpressure_policy.disconnect_threshold`

<details>
<summary><b>Purpose:</b> The parameter <code>disconnect_threshold</code> controls the load threshold at which the server disconnects the client and places it in quarantine.</summary>

#### Idea

Config path: `hyper_parameters.backpressure_policy.disconnect_threshold`.

The parameter `disconnect_threshold` determines when the server decides a client is so overloaded or disruptive that it should be disconnected. This is the last-resort threshold.

Treat this as the safety fuse. If it is too low, legitimate clients may be disconnected during real traffic spikes. If it is too high, the server may spend too long in a degraded state trying to recover without removing the source of pressure.

#### Default if omitted

If omitted, it defaults to the value `500`.

</details>

## Tuning recipes

This section gives a starting point for common deployment goals. The intent is to provide safe defaults, not to replace measurement and load testing.

Unless stated otherwise, names below refer to `hyper_parameters.*`. Backpressure policy settings live at `hyper_parameters.backpressure_policy.*`.

### Interactive chat (low latency, many small messages)

Focus on allowing frequent small messages without aggressively slowing users:

* Raise `rate_limit_msgs_per_minute` if users legitimately send bursts.
* Keep `throttle_delay_ms` modest.
* Keep `flow_control_delay_ms` moderate so the system can recover quickly from spikes.
* Set thresholds based on expected room sizes.

### Broadcast-heavy usage (many recipients per message)

Focus on preventing the server from creating too many concurrent sends:

* Increase `connection_buffer_size` and `queue_monitor_capacity` so monitoring signals can keep up.
* Choose thresholds proportional to the expected number of recipients.
* Use JSON file logs and `log_keys` to keep logs compact.

### Abuse-resistant deployment (untrusted clients)

Focus on limiting damage from malicious or buggy clients:

* Lower `rate_limit_msgs_per_minute`.
* Lower thresholds and keep disconnect enabled.
* Increase `quarantine_cooldown_secs` if repeated reconnect attempts are part of the threat model.
* Consider disabling detailed payload logging via `log_keys: []` if payloads may contain sensitive content.

## Complete example config

```json
{
  "host": "127.0.0.1",
  "port": 8888,

  "version": "rust",

  "logger": {
    "log_level": "INFO",

    "enable_console_log": true,
    "console_log_format": "\u001b[92m%(asctime)s\u001b[0m - \u001b[94m%(name)s\u001b[0m - %(levelname)s - %(message)s",

    "enable_file_log": true,
    "enable_json_log": true,
    "log_file_path": "logs/",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",

    "max_file_size": 1000000,
    "backup_count": 3,
    "date_format": "%Y-%m-%d %H:%M:%S.%3f",
    "log_keys": null
  },

  "hyper_parameters": {
    "connection_buffer_size": 256,
    "command_buffer_size": 64,
    "control_channel_capacity": 8,
    "queue_monitor_capacity": 100,

    "client_timeout_secs": 600,
    "rate_limit_msgs_per_minute": 1000,
    "timeout_check_interval_secs": 30,
    "accept_error_backoff_ms": 100,

    "quarantine_cooldown_secs": 600,
    "quarantine_cleanup_interval_secs": 60,

    "throttle_delay_ms": 200,
    "flow_control_delay_ms": 1000,

    "worker_threads": 4,

    "backpressure_policy": {
      "enable_throttle": true,
      "throttle_threshold": 50,
      "enable_flow_control": true,
      "flow_control_threshold": 150,
      "enable_disconnect": true,
      "disconnect_threshold": 300
    }
  }
}
```

---

<p align="center">
  <a href="./server.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.server.server</b></code></a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="./../server.md">Next: <code style="background: transparent;">Summoner<b>.server</b></code> &raquo;</a>
</p>
