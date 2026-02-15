# <code style="background: transparent;">Summoner<b>.client</b></code> configuration guide

This page explains how to configure `SummonerClient.run(...)` in a way that is understandable to readers who do not want to study the implementation. Each setting is described by its purpose, behavior, default value, and the practical consequences of changing it.

A Summoner client is an async runtime that connects to a TCP relay, receives newline-delimited messages, runs your registered handlers (`@receive`, `@send`, `@hook`), and optionally uses flow-aware routing (parsed routes, a state tape, and reactive senders). Most configuration exists to answer three operational questions:

1. Where does the client connect (`host`, `port`), and how does it reconnect (`hyper_parameters.reconnection`)?
2. What is recorded for observability (`logger`)?
3. How does the client stay stable under load (`hyper_parameters.receiver` and `hyper_parameters.sender`)?

> [!NOTE]
> **Loading & precedence**
>
> * You can pass a configuration dictionary directly to `client.run(...)` as `config_dict`, or provide a JSON file path via `config_path`.
> * `config_dict` takes precedence over `config_path`.
> * **Host/Port precedence**
>
>   * If `host` / `port` are present in the config, they override the arguments you pass to `run(host, port)`.
>   * If they are omitted (or `null`), the client uses the `run(host, port)` arguments.
>
> Internally, a session connects to `current_host = self.host or run_host` and `current_port = self.port or run_port`.



## Table of contents

* [Core](#core)

  * [`host`](#host)
  * [`port`](#port)

* [Logger](#logger)

  * [What the client logger emits](#what-the-client-logger-emits)
  * [`logger`](#logger-object)

* [Hyper parameters](#hyper-parameters)

  * [What hyper parameters control](#what-hyper-parameters-control)
  * [Reconnection](#reconnection)

    * [`hyper_parameters.reconnection.retry_delay_seconds`](#retry_delay_seconds)
    * [`hyper_parameters.reconnection.primary_retry_limit`](#primary_retry_limit)
    * [`hyper_parameters.reconnection.default_host`](#default_host)
    * [`hyper_parameters.reconnection.default_port`](#default_port)
    * [`hyper_parameters.reconnection.default_retry_limit`](#default_retry_limit)
  * [Receiver](#receiver)

    * [`hyper_parameters.receiver.max_bytes_per_line`](#max_bytes_per_line)
    * [`hyper_parameters.receiver.read_timeout_seconds`](#read_timeout_seconds)
  * [Sender](#sender)

    * [`hyper_parameters.sender.concurrency_limit`](#concurrency_limit)
    * [`hyper_parameters.sender.queue_maxsize`](#queue_maxsize)
    * [`hyper_parameters.sender.batch_drain`](#batch_drain)
    * [`hyper_parameters.sender.event_bridge_maxsize`](#event_bridge_maxsize)
    * [`hyper_parameters.sender.max_worker_errors`](#max_worker_errors)

* [Tuning recipes](#tuning-recipes)

* [Complete example](#complete-example-config)



## Core

### `host`

<details>
<summary><b>Purpose:</b> The parameter <code>host</code> is the network address the client connects to.</summary>

#### Typical values and meaning

* `"127.0.0.1"` connects to a server on the same machine (development).
* A LAN or public IP (or DNS name) connects to a server reachable over the network.

#### Default if omitted

If `host` is not provided (or set to `null`), the client uses the `host` argument passed to `SummonerClient.run(host=...)`. The default `run()` value is `"127.0.0.1"`.

#### Practical consequences

* Setting `host` in the config makes the target stable across runs, independent of `run(host=...)`.
* Leaving it unset makes `run(host=...)` the single place to control the target.

</details>

### `port`

<details>
<summary><b>Purpose:</b> The parameter <code>port</code> is the TCP port number the client connects to.</summary>

#### Default if omitted

If `port` is not provided (or set to `null`), the client uses the `port` argument passed to `SummonerClient.run(port=...)`. The default `run()` value is `8888`.

</details>



## Logger

Logging is how the client answers basic operational questions such as: "Did I connect?", "Why am I reconnecting?", "Which hook failed?", "Are my senders crashing?", and "Is backpressure building inside the client runtime?"

### What the client logger emits

The client commonly logs:

* connection success and clean disconnects
* retry attempts and fallback transitions (primary target to default target)
* failures in hooks (receive/send hook exceptions are logged and the payload is preserved)
* sender worker crashes (with a configurable "consecutive crash" threshold)
* queue pressure warnings (for example, when the send queue is close to full)
* parsing warnings when flow is enabled and a route fails to parse at registration time

<a id="logger-object"></a>

### `logger`

<details>
<summary><b>Purpose:</b> The <code>logger</code> object configures the client logger behavior (level, handlers, formatting).</summary>

#### Idea

Config path: `logger`.

The client forwards this dictionary directly to:

```python
configure_logger(self.logger, logger_cfg)
```

This means the accepted keys and their behavior are defined by `summoner.logger.configure_logger`, not by the client itself.

#### Default if omitted

If omitted, `{}` is used. You still get a logger instance, but you get whatever default handler and formatting behavior your logger implementation chooses.

#### Practical consequences

* Use a stable `logger` config for repeatable output across environments.
* Keep the log level at `"INFO"` for normal usage and `"DEBUG"` for short investigations. Under load, debug logging can be noisy.

</details>



## Hyper parameters

### What hyper parameters control

The `hyper_parameters` section contains runtime limits and timing constants that control:

1. **Reconnection behavior** (how long to wait between attempts, when to fail over)
2. **Receive-side safety** (line size limits, optional read timeouts)
3. **Send-side throughput and backpressure** (worker concurrency, queue sizes, and failure thresholds)

All hyper parameters are optional. If omitted, defaults apply.



## Reconnection

<a id="retry_delay_seconds"></a>

### `hyper_parameters.reconnection.retry_delay_seconds`

<details>
<summary><b>Purpose:</b> The parameter <code>retry_delay_seconds</code> sets how long the client sleeps between connection attempts.</summary>

#### Idea

Config path: `hyper_parameters.reconnection.retry_delay_seconds`.

This is the backoff delay used after connection failures such as refused connections, disconnects, or OS-level connection errors.

#### Default if omitted

If omitted, it defaults to `3`.

#### Practical consequences

* Lower values reconnect faster but can spam logs and create tight retry loops in failure scenarios.
* Higher values reduce noise and load on the target server during outages.

</details>

<a id="primary_retry_limit"></a>

### `hyper_parameters.reconnection.primary_retry_limit`

<details>
<summary><b>Purpose:</b> The parameter <code>primary_retry_limit</code> sets how many retries are allowed before failing over to the default target.</summary>

#### Idea

Config path: `hyper_parameters.reconnection.primary_retry_limit`.

The client starts in a "Primary" stage. If it cannot maintain a session, it retries up to this limit.

#### Default if omitted

If omitted, it defaults to `3`.

#### Practical consequences

* Higher values keep trying the primary target longer.
* Lower values fail over faster.

</details>

<a id="default_host"></a>

### `hyper_parameters.reconnection.default_host`

<details>
<summary><b>Purpose:</b> The parameter <code>default_host</code> is the host used when the client falls back after primary retries are exhausted.</summary>

#### Idea

Config path: `hyper_parameters.reconnection.default_host`.

If not set, the client uses the top-level `host` from the config as the fallback host.

#### Default if omitted

If omitted, it defaults to the value of top-level `host` (which may itself be `null`).

#### Practical consequences

* Set `default_host` if you want an explicit fallback independent of the primary host.
* If both `default_host` and top-level `host` are `null`, the fallback stage will still use the `run(host=...)` argument.

</details>

<a id="default_port"></a>

### `hyper_parameters.reconnection.default_port`

<details>
<summary><b>Purpose:</b> The parameter <code>default_port</code> is the port used when the client falls back after primary retries are exhausted.</summary>

#### Default if omitted

If omitted, it defaults to the value of top-level `port` (which may itself be `null`).

</details>

<a id="default_retry_limit"></a>

### `hyper_parameters.reconnection.default_retry_limit`

<details>
<summary><b>Purpose:</b> The parameter <code>default_retry_limit</code> sets how many retries are allowed in the fallback stage.</summary>

#### Idea

Config path: `hyper_parameters.reconnection.default_retry_limit`.

After the primary stage fails, the client enters a "Default" stage and retries up to this limit.

#### Default if omitted

If omitted, it defaults to `2`.

#### Special value

If set to `null`, the fallback stage retries indefinitely.

</details>



## Receiver

<a id="max_bytes_per_line"></a>

### `hyper_parameters.receiver.max_bytes_per_line`

<details>
<summary><b>Purpose:</b> The parameter <code>max_bytes_per_line</code> caps the size of a single incoming line.</summary>

#### Idea

Config path: `hyper_parameters.receiver.max_bytes_per_line`.

Incoming messages are read using a line-based protocol. If a received line exceeds this size, it is dropped and the client continues.

#### Default if omitted

If omitted, it defaults to `65536` (64 KiB).

#### Practical consequences

* Increase this only if you expect legitimately large single-line payloads.
* Keeping it bounded reduces memory exposure to a single oversized message.

</details>

<a id="read_timeout_seconds"></a>

### `hyper_parameters.receiver.read_timeout_seconds`

<details>
<summary><b>Purpose:</b> The parameter <code>read_timeout_seconds</code> controls whether reads block indefinitely or time out and retry.</summary>

#### Idea

Config path: `hyper_parameters.receiver.read_timeout_seconds`.

* If `null`, the client blocks waiting for data.
* If set to a number, the client waits up to that duration for a line. If no data arrives, it sleeps briefly and retries.

#### Default if omitted

If omitted, it defaults to `null` (wait indefinitely).

#### Practical consequences

* `null` is simplest and avoids periodic wakeups.
* A small timeout can be useful if you want the receive loop to frequently re-check internal stop conditions, but it adds wakeups.

</details>



## Sender

<a id="concurrency_limit"></a>

### `hyper_parameters.sender.concurrency_limit`

<details>
<summary><b>Purpose:</b> The parameter <code>concurrency_limit</code> sets how many sender workers run concurrently.</summary>

#### Idea

Config path: `hyper_parameters.sender.concurrency_limit`.

The client starts this many worker tasks per session. Workers pull sender jobs from an internal queue.

#### Default if omitted

If omitted, it defaults to `50`.

#### Validation

Must be an integer `>= 1`, otherwise the client raises:

* `ValueError("sender.concurrency_limit must be an integer ≥ 1")`

#### Practical consequences

* Higher values increase parallelism but can increase load on your runtime and on the server.
* Lower values reduce throughput but can make behavior easier to reason about.

</details>

<a id="queue_maxsize"></a>

### `hyper_parameters.sender.queue_maxsize`

<details>
<summary><b>Purpose:</b> The parameter <code>queue_maxsize</code> sets the capacity of the internal send queue used for backpressure.</summary>

#### Idea

Config path: `hyper_parameters.sender.queue_maxsize`.

When the queue is full, the sender loop blocks while trying to enqueue new sender jobs. This is the main client-side backpressure mechanism.

#### Default if omitted

If omitted, it defaults to `concurrency_limit`.

#### Validation

Must be an integer `>= 1`, otherwise:

* `ValueError("sender.queue_maxsize must be an integer ≥ 1")`

#### Practical consequences

* Larger queues absorb bursts but increase buffering and can hide sustained overload.
* Smaller queues apply backpressure earlier and keep memory usage tighter.

The client also warns if:

* `queue_maxsize < concurrency_limit`

because producers will be throttled by the smaller queue capacity.

</details>

<a id="batch_drain"></a>

### `hyper_parameters.sender.batch_drain`

<details>
<summary><b>Purpose:</b> The parameter <code>batch_drain</code> controls how often the client flushes writes to the socket.</summary>

#### Idea

Config path: `hyper_parameters.sender.batch_drain`.

* If `true`, the sender loop drains once per batch.
* If `false`, each worker drains after writing its payload(s).

#### Default if omitted

If omitted, it defaults to `true`.

#### Practical consequences

* `true` reduces the number of `drain()` calls and usually improves throughput.
* `false` can reduce latency per message at the cost of more frequent draining.

</details>

<a id="event_bridge_maxsize"></a>

### `hyper_parameters.sender.event_bridge_maxsize`

<details>
<summary><b>Purpose:</b> The parameter <code>event_bridge_maxsize</code> sets the capacity of the internal bridge from receivers to reactive senders when flow is enabled.</summary>

#### Idea

Config path: `hyper_parameters.sender.event_bridge_maxsize`.

When flow-aware routing is enabled, receiver batches can produce events that trigger reactive senders. Those events are passed through an internal queue (the "event bridge"). If the bridge is full, the receiver side blocks, which slows input processing and applies backpressure.

#### Default if omitted

If omitted, it defaults to `1000`.

#### Practical consequences

* Larger values absorb bursts of receiver events.
* Smaller values apply backpressure earlier if receivers are producing events faster than senders can consume them.

</details>

<a id="max_worker_errors"></a>

### `hyper_parameters.sender.max_worker_errors`

<details>
<summary><b>Purpose:</b> The parameter <code>max_worker_errors</code> sets how many consecutive sender worker failures abort the session.</summary>

#### Idea

Config path: `hyper_parameters.sender.max_worker_errors`.

A sender worker can fail if a sender function raises unexpectedly. After this many consecutive failures in a worker, the client shuts down the sender loop for the session.

#### Default if omitted

If omitted, it defaults to `3`.

#### Validation

Must be an integer `>= 1`, otherwise:

* `ValueError("sender.max_worker_errors must be an integer ≥ 1")`

#### Practical consequences

* Lower values fail fast on buggy sender code.
* Higher values tolerate intermittent sender failures but can hide persistent errors.

</details>



## Tuning recipes

These recipes provide starting points. They do not replace measurement and load tests.

### Local development (fast feedback)

Goal: quick reconnects and readable logs.

* `retry_delay_seconds: 1`
* `primary_retry_limit: 5`
* `sender.concurrency_limit: 10 to 20`
* `sender.batch_drain: false` if you care about per-message latency while debugging

### Throughput-oriented sender loop

Goal: high send throughput without frequent flushes.

* `sender.batch_drain: true`
* Increase `sender.concurrency_limit` gradually
* Increase `sender.queue_maxsize` so short bursts do not stall the producer immediately

### Flow-heavy workloads (many reactive triggers)

Goal: avoid blocking receiver-side event production.

* Increase `sender.event_bridge_maxsize`
* Keep `sender.queue_maxsize` comfortably above the typical number of senders emitted per cycle

### Fail-fast behavior for unstable handlers

Goal: stop quickly when handler code is unhealthy.

* Keep `sender.max_worker_errors` low (default is already conservative)
* Use hook logging at `"INFO"` or `"DEBUG"` during investigations to spot failing hooks or invalid payloads



## Complete example config

```json
{
  "host": "127.0.0.1",
  "port": 8888,

  "logger": {
    "level": "INFO"
  },

  "hyper_parameters": {
    "reconnection": {
      "retry_delay_seconds": 2,
      "primary_retry_limit": 3,

      "default_host": "127.0.0.1",
      "default_port": 8888,
      "default_retry_limit": 2
    },

    "receiver": {
      "max_bytes_per_line": 65536,
      "read_timeout_seconds": null
    },

    "sender": {
      "concurrency_limit": 50,
      "queue_maxsize": 200,
      "batch_drain": true,
      "event_bridge_maxsize": 1000,
      "max_worker_errors": 3
    }
  }
}
```

---

<p align="center">
  <a href="./client.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.client.client</b></code></a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="./merger.md">Next: <code style="background: transparent;">Summoner<b>.client.merger</b></code> &raquo;</a>
</p>
