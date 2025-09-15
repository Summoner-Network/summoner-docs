# Summoner Client and Agent Configurations (Local Use)

> This page focuses on configuration and parameterization needed to run a Summoner **client/agent** locally. Routing, flows, and advanced orchestration live on the adjacent pages.

<p align="center">
  <img width="240px" src="../../assets/img/summoner_fund_agent_rounded.png" />
</p>

## Philosophy: Clients Become Agents

A Summoner client initiates a TCP connection to a server, sends line-delimited messages, and receives broadcast envelopes from peers. In Summoner, this client is the substrate for **agents**: programmable clients that layer orchestration (endpoint graphs, FSM-style coordination) and, with the upcoming `SummonerAgent` class (Aurora Update), decentralized identity and reputation logic.

The wire format stays simple: messages are **one line** each and should end with `\n`. Servers rebroadcast a **line-delimited JSON envelope** to other peers:

```python
'{"remote_addr":"<ip:port>","content":"<original line minus trailing \\n>"}\n'
```

> [!NOTE]
> Summoner servers exclude the original sender when rebroadcasting, so each client sees traffic from peers, not its own echoes.

On the client, outgoing payloads are wrapped into typed, newline-terminated frames; incoming lines are recovered to their original types. This keeps agents observable and composable without hiding the network model.

> [!NOTE]
> **Typed envelopes (SDK).** On send, the SDK wraps your payload in a versioned, self-describing frame using the keys:
>
> * `"_version"`
> * `"_payload"`
> * `"_type"`
>
> and appends `\n`. On receive, it unpacks and casts types for you, so your handlers usually see a Python dict like `{"remote_addr": "...", "content": <typed_payload>}`. If a peer does not use Summoner, the SDK safely falls back to the raw JSON or string.
>
> Example of the inner typed frame (shown here as JSON for clarity):
>
> ```json
> {"_version":"1.0.0","_payload":{"n":"42","ok":"true"},"_type":{"n":"int","ok":"bool"}}
> ```
>
> You do not have to build or parse this yourself — the SDK's wrappers handle it.

## One Implementation: Python

The client/agent runtime is **Python-only**. Client configuration is kept in its **own file** and is not mixed with server configs. The client does **not** read a `version` key. If you include one for symmetry with server files, it will be ignored.

Keep client configs minimal and focused on the client's needs (address selection, reconnection, receiver/sender limits, and logging).

## Running a Client

The minimal entrypoint:

```python
from summoner.client import SummonerClient

if __name__ == "__main__":
    client = SummonerClient(name="my_client")
    client.run()  # connects to 127.0.0.1:8888 by default
```

Connect to a specific server inline:

```python
client.run(host="127.0.0.1", port=8888)
```

Run with a config (file or dict):

```python
# File-based
client.run(config_path="client_config.json")

# Dict-based (inline)
client.run(config_dict={"logger": {"log_level": "INFO"}})
```

Because configs can coexist with `.run(...)` arguments, it is important to know which values take effect (next section).

## Configuration Sources and Precedence

### Overview

Summoner accepts configuration from three places. Think of them as layers that resolve to one effective set of values at startup.

1. **Keyword arguments to `.run(...)`**
   Use these for quick experiments or when embedding the client. You can pass `host`, `port`, and optionally `config_path` or `config_dict`.

2. **`config_path`**
   A path to a JSON file. Best for reproducible runs and versioned presets.

3. **`config_dict`**
   A Python `dict` with the same keys as JSON. Ideal for notebooks/launchers; bypasses file I/O and wins over `config_path`.

<details>
<summary><b>Deployment Tips</b> </summary>

#### Precedence in practice

* If you pass a **`config_dict`**, it is used and any `config_path` is ignored.
* Else, if you pass a **`config_path`**, the file is loaded.
* Else, built-in defaults apply.

This order reflects explicitness: dict (constructed in code) > file (named by you) > defaults.

**Note.** Keys present but set to `null` are treated as "unset" and do **not** override `.run(...)` arguments. Use `null` intentionally when you want the code’s `host`/`port` to win.

#### Address precedence for the client

For the **Python client**, if **both** your code **and** the config specify `host`/`port`, the **config takes precedence**. This allows deployments to override code without edits. The `logger` section is always applied from config when present.

#### Data types

* `host`: string (e.g., `"127.0.0.1"`, `"localhost"`, or a LAN/WAN name).
* `port`: integer (0–65535), typically >1024.
* JSON has no comments; keep files minimal. Inline notes? Build the dict in Python.

#### Operational guidance

If you frequently switch environments, keep behavior (logging, reconnection, sender/receiver limits) in JSON and let configs override `host`/`port`. Your call sites remain clean while ops retains control.

</details>

### How to Run With Each Source

**Code-only, Python client**

```python
from summoner.client import SummonerClient
SummonerClient(name="local").run(host="127.0.0.1", port=8888)
```

**File-based, Python client**

```python
from summoner.client import SummonerClient
SummonerClient(name="local").run(config_path="client_config.json")
```

**Dict-based, Python client**

```python
from summoner.client import SummonerClient

cfg = {
  "logger": {"log_level": "INFO", "enable_console_log": True},
  "hyper_parameters": {
    "reconnection": {"retry_delay_seconds": 3, "primary_retry_limit": 3}
  }
}
SummonerClient(name="local").run(config_dict=cfg)
```

> [!CAUTION]
> A dict overrides a file if both are provided. For connectivity, the client prefers `host`/`port` from config when **present and non-null**.

## Config File Shape

Top-level keys you can set (Python client):

* `host`, `port`
* `logger`
* `hyper_parameters`

  * `reconnection`
  * `receiver`
  * `sender`

<details>
<summary><b>Examples (click me)</b> Minimal local dev configs</summary>
<br>

1. **No file:**
   Run with `.run(host="127.0.0.1", port=8888)`; defaults apply otherwise.

2. **Minimal file:**

   ```json
   {
     "logger": { "log_level": "INFO" }
   }
   ```

3. **Explicit address via config + quiet logs:**

   ```json
   {
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
<summary><b>Example (click me)</b> Production-leaning local config (Python)</summary>
<br>

The following config profile skews to **human-facing local work**: low latency sends, readable logs, bounded resources, and decisive reconnection. For bulk throughput runs, consider `batch_drain: true` and possibly a larger `concurrency_limit` after measuring.

```json
{
  "host": null,
  "port": null,

  "logger": {
    "log_level": "INFO",

    "enable_console_log": true,
    "console_log_format": "\u001b[92m%(asctime)s\u001b[0m - \u001b[94m%(name)s\u001b[0m - %(levelname)s - %(message)s",

    "enable_file_log": true,
    "enable_json_log": false,
    "log_file_path": "logs/",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",

    "max_file_size": 1000000,
    "backup_count": 3,
    "date_format": "%Y-%m-%d %H:%M:%S.%3f",
    "log_keys": null
  },
  
  "hyper_parameters": {

    "receiver": {
      "max_bytes_per_line": 65536,
      "read_timeout_seconds": null
    },

    "sender": {
      "concurrency_limit": 16,
      "batch_drain": false,
      "queue_maxsize": 128,
      "event_bridge_maxsize": 2000,
      "max_worker_errors": 3
    },

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

*When both code and config provide an address, the **config wins** for the client.*

* **Receiver limits protect the process**

  * `max_bytes_per_line: 65536` (64 KiB) caps any single incoming frame. Oversized lines are dropped with a warning, preventing one peer from clogging memory.
  * `read_timeout_seconds: null` blocks until a line arrives (lowest CPU overhead).
    Set a finite value only if you need the loop to "wake up" periodically for other tasks.

* **Sender tuned for low latency with safe headroom**

  * `concurrency_limit: 16` gives a healthy worker pool without excessive context switching on typical laptops/desktops.
  * `batch_drain: false` favors **lower latency**: workers flush their own writes. This is great for interaction and small bursts; if you later care about max throughput, try `true` to drain once per batch.
  * `queue_maxsize: 128` (≥ concurrency) provides back-pressure headroom for bursts without stalling producers too early.
  * `event_bridge_maxsize: 2000` supports reactive **flows** (bursty receive→send patterns) without dropping events. If you never use flows, reduce this to save memory.
  * `max_worker_errors: 3` shuts down the session if a worker crashes repeatedly, preventing silent crash loops.

</details>

<br>

# Parameter Reference by JSON Structure

The sections below follow the JSON structure. Each parameter has a clear purpose, suggested ranges, and relationships to others. Explanations aim to be beginner-friendly while giving you practical operator insights.

## `host` and `port`

<details>
<summary><b>(Click to expand)</b></summary>

* **Type**: string, integer
* **Default**: `host="127.0.0.1"`, `port=8888`
* **Used by**: **Python** (config can override `.run(...)`)

**What they control**
Where the client dials. `host` is the server's IP or DNS name; `port` is the numeric channel on that server.

**How resolution works**
If both your code and the config specify `host`/`port`, the **config value wins** for the client. This lets ops steer deployments without code edits.

**Beginner notes**

* Think of `host:port` like a phone number plus an extension. The phone number (IP/DNS) finds the machine; the extension (port) finds the specific program.
* `127.0.0.1` means "this same computer." Use this for quick local tests.

**Guidance**

* Keep `127.0.0.1` for isolated tests.
* Use `0.0.0.0` **only on servers** (not clients). Clients usually use a specific target, e.g., `"192.168.1.34"` or `"mybox.local"`.
* Choose ports above **1024** to avoid admin privileges (ports <1024 are "privileged").

**Interactions**

* If you configure a **fallback** (see `reconnection.default_host/default_port`), set them to a *different* address from the primary; otherwise there is no real failover.

**Common pitfalls**

* Firewalls and NAT: if the client cannot reach the server from another machine, verify the server is bound to a reachable IP and the port is open.

</details>

## `logger` (Python)

<details>
<summary><b>(Click to expand)</b></summary>

**What it controls**
Where logs go (console, files), how detailed they are, and how they are formatted (plain text vs JSON, timestamp precision, and optional key-filtering of message dictionaries).

### `logger.log_level`

* **Type**: string — default `"DEBUG"`

**Effect**
Controls verbosity.

* `"DEBUG"`: everything (great for first runs).
* `"INFO"`: calm, production-leaning baseline.
* `"WARNING"`/`"ERROR"`: only problems.

**Tip**
Start `"DEBUG"` while wiring things up; drop to `"INFO"` once stable.

---

### `logger.enable_console_log`

* **Type**: bool — default `true`

**Effect**
Prints to stdout. Keep this on for interactive work and during early testing.

---

### `logger.enable_file_log`, `logger.log_file_path`

* **Type**: bool, string — defaults `false`, `""`

**Effect**
Writes rotating log files to a directory (e.g., `"./logs"`). Great for long runs and post-mortems.

**Interaction**
Pairs well with `enable_json_log=true` if you want to analyze logs with tools (jq, Python, Splunk, etc.).

**Pitfall**
Relative paths are resolved against the process's working directory. In services, prefer absolute paths.

---

### `logger.enable_json_log`

* **Type**: bool — default `false`

**Effect**
Emits structured JSON logs instead of plain text. Easier to parse and filter.

**Beginner note**
Text is nice for humans; JSON is nice for programs. Choose based on your audience.

---

### `logger.date_format`

* **Type**: string — default `"%Y-%m-%d %H:%M:%S.%3f"` (supports `%<n>f`)

**Effect**
Controls timestamp style and fractional precision.

* `.%3f` → milliseconds
* `.%6f` → microseconds

**Tip**
Use microseconds for performance tests; milliseconds for everyday usage.

---

### `logger.log_keys`

* **Type**: array|null — default `null`

**Effect**
If your message is a **dict**, only the listed keys are logged. Reduces noise and avoids leaking sensitive fields.

**Example**
`["route","type","id"]` keeps routing and identity details but drops large payload bodies.

---

### Python-only extras (supported)

* `console_log_format` (string) — color/shape of console lines.
* `log_format` (string) — layout for file lines.
* `max_file_size` (int) — rotate after N bytes.
* `backup_count` (int) — keep N rotated files.

**Consequences**
Larger files and more backups consume disk; set limits that fit your environment.

</details>

## `hyper_parameters`

<details>
<summary><b>(Click to expand)</b> Client runtime behavior beyond basic connectivity.</summary>

### `reconnection` (object)

**What it controls**
How the client behaves if the server disconnects or refuses the connection: how long to wait, how many times to retry the **primary**, and how to fall back to a **default** address.

* **`retry_delay_seconds`**

  * **Type**: integer
  * **Default**: `3`
  * **What it does**: Fixed (not exponential) pause between attempts.
  * **Consequence**: Short delays make local testing snappy; long delays reduce "retry storms" on shared servers.

* **`primary_retry_limit`**

  * **Type**: integer or `null` (∞)
  * **Default**: `3`
  * **What it does**: How many times to try the primary before giving up.
  * **Consequence**: `null` means "keep trying forever," which is useful for daemons but can hide outages in CI unless you also alert on logs.

* **`default_host`, `default_port`**

  * **Type**: string, integer
  * **Default**: inherits from `host`/`port` if unset
  * **What they do**: The fallback server.
  * **Consequence**: If they inherit the same values, there is no real failover—set a distinct address to truly test fallback.

* **`default_retry_limit`**

  * **Type**: integer or `null` (∞)
  * **Default**: `2`
  * **What it does**: How many times to try the fallback before exiting.
  * **Consequence**: Prevents infinite loops if both endpoints are down.

**Beginner analogy**
Primary is your "first choice café." If it is closed, you try your "backup café" a few times before going home.

**Reasonable values**

* `retry_delay_seconds`: 1–3 (solo dev), 5–10 (shared lab).
* `primary_retry_limit`: 3–5 (or `null` for always-on agents).
* `default_retry_limit`: 2–3 (or `null` if you truly never want to exit).

**Pitfall**
Using very short delays (e.g., 0–1s) on a shared network can hammer a sick server. Be kind to your future self.

---

### `receiver` (object)

**What it controls**
How incoming messages are read from the TCP stream.

* **`max_bytes_per_line`**

  * **Type**: integer (bytes)
  * **Default**: `65536` (64 KiB)
  * **What it does**: Upper bound for a single incoming **line**. The client drops oversized lines with a warning to protect memory and prevent one peer from clogging the pipe.
  * **Consequence**: If your peers send huge JSON blobs, they will be dropped. Split large data across multiple messages or compress/encode out of band.

* **`read_timeout_seconds`**

  * **Type**: number or `null`
  * **Default**: `null` (wait indefinitely)
  * **What it does**: Adds a timeout to each line read; on timeout it sleeps \~10ms and tries again.
  * **Consequence**: This is **not** an idle disconnect. It just makes the loop "wake up" periodically so other tasks can run or so you can add time-based logic later.

**Beginner analogy**
Think of the line limit like the size of an envelope: if a letter does not fit, it gets rejected so the mailbox does not jam.

**Reasonable values**

* Keep 64 KiB unless you know your payloads are large.
* Use a finite timeout (e.g., 0.5–2s) if you need the receive loop to "breathe" regularly.

**Pitfall**
Setting `read_timeout_seconds` too tiny (e.g., 0.001) can waste CPU on wakeups without benefit.

---

### `sender` (object)

**What it controls**
How outgoing messages are produced and written onto the socket. Under the hood, senders push work into a queue; a pool of worker tasks pulls from that queue and writes to the network.

* **`concurrency_limit`**

  * **Type**: integer ≥ 1
  * **Default**: `50`
  * **What it does**: Number of parallel worker tasks allowed to send.
  * **Consequence**: More workers increase throughput for many small sends, but also increase contention and context switches. Very high values can add overhead.

* **`batch_drain`**

  * **Type**: bool
  * **Default**: `true`
  * **What it does**: Controls when the TCP buffer is flushed.

    * `true`: all workers write; the loop drains once per batch → **fewer syscalls**, steadier throughput.
    * `false`: each worker drains after its own writes → **lower latency** for tiny bursts, potentially more syscalls.
  * **Consequence**: Use `true` for streaming or regular chatter; try `false` for sporadic, latency-sensitive pings.

* **`queue_maxsize`**

  * **Type**: integer ≥ 1
  * **Default**: `concurrency_limit`
  * **What it does**: The back-pressure buffer for pending sends. If the queue fills, producers block until space frees up.
  * **Consequence**: If this is **smaller** than `concurrency_limit`, the client warns and throttling happens earlier; if it is **too large**, memory use can spike during bursts.

* **`event_bridge_maxsize`**

  * **Type**: integer ≥ 1
  * **Default**: `1000`
  * **What it does**: Capacity for the internal bridge that carries **events** from receivers to senders when **flows** are active (reactive sending).
  * **Consequence**: Bigger values let you absorb larger "bursts" of events; too big wastes memory.

* **`max_worker_errors`**

  * **Type**: integer ≥ 1
  * **Default**: `3`
  * **What it does**: If the same worker crashes this many times in a row, the client tears down the sender loop and ends the session.
  * **Consequence**: Prevents silent failure loops (e.g., a bug that makes a worker crash immediately on each task).

**Beginner analogy**
Imagine a post office:

* The **queue** is the mail cart.
* **Workers** are clerks stuffing letters into the chute.
* **Drain** is when the chute actually dumps the letters into the truck.

**Recommended starting points**

* `concurrency_limit`: 10–50 on desktops; 1–8 on small devices.
* `queue_maxsize`: match or slightly exceed `concurrency_limit`.
* Keep `batch_drain=true` unless you are optimizing for the lowest single-message latency.
* Leave `max_worker_errors=3` unless debugging.

**Pitfalls**

* Setting `queue_maxsize` far above `concurrency_limit` can hide back-pressure until memory swells.
* Setting `concurrency_limit` extremely high can reduce overall throughput due to contention.

</details>

<br>

# Putting It Together Locally

A quick path to success:

1. Start a local server (`127.0.0.1:8888`).
2. Run the client with `.run(host="127.0.0.1", port=8888)` and confirm send/receive.
3. Add a `client_config.json` to tune **logging** and **reconnection** first.
4. For heavier tests, adjust **`receiver.max_bytes_per_line`**, **`sender.concurrency_limit`**, **`sender.queue_maxsize`**, and **`batch_drain`**.

> [!TIP]
> If you aim the client at a LAN/WAN server, ensure the server binds to a reachable IP (e.g., `0.0.0.0`) and inbound firewall rules allow the chosen port.

<p align="center">
  <a href="server_relay.md">&laquo; Previous: Servers and Relay </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="design.md">Next: Agent Design Principles &raquo;</a>
</p>
