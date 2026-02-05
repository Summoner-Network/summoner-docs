# <code style="background: transparent;">Summoner<b>.server.server</b></code>

This page documents the **Python SDK interface** for running a Summoner server via `SummonerServer`. It focuses on how to use the class and its methods, and what behavior to expect when you call them.

A Summoner server is a TCP broadcast relay: clients connect to a host and port, send newline-delimited messages, and the server forwards each message to all other connected clients as a JSON envelope.

`SummonerServer` is the primary SDK entry point for running a server process. It handles configuration loading (from a file path or in-memory dict), logger initialization, termination signal handling (where supported), and the overall server lifecycle (start, run, and shutdown).

## `SummonerServer.__init__`

```python
def __init__(self, name: Optional[str] = None) -> None
```

### Behavior

Creates a server instance and prepares internal state for running the server.

* Sets a logical `name` used for logging.
* Creates a dedicated asyncio event loop for this server instance and sets it as the current loop.
* Initializes internal registries:

  * a set of connected clients (writers),
  * a mapping of active handler tasks to client addresses,
  * locks for safe concurrent access to those registries.

### Inputs

#### `name`

* **Type:** `Optional[str]`
* **Meaning:** A human-readable identifier for logs and diagnostics.
* **Default behavior:** If `name` is not a string, a placeholder is used (`"<server:no-name>"`).

### Outputs

This constructor returns a `SummonerServer` instance.

### Examples

#### Basic initialization

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")
```

## `SummonerServer.run`

```python
def run(
    self,
    host: str = "127.0.0.1",
    port: int = 8888,
    config_path: Optional[str] = None,
    config_dict: Optional[dict[str, Any]] = None,
) -> None
```

### Behavior

Starts the server and blocks the calling thread until the server stops.

At a high level, `run(...)` does four things:

1. Loads the server configuration (from `config_dict` or `config_path`).
2. Configures logging using the loaded config.
3. Installs termination signal handlers (where supported).
4. Runs the server until it is interrupted (Ctrl+C) or shut down.

The server can run using different backend implementations selected by configuration. At the SDK level, you always start the server the same way (by calling `run(...)`); the backend selection is handled internally based on the loaded config and the platform.

### Inputs

#### `host`

* **Type:** `str`
* **Meaning:** The network interface address to bind to.
* **Common values:**

  * `"127.0.0.1"`: accept only local connections (development).
  * `"0.0.0.0"`: accept connections from other machines (LAN/cloud).
* **Default:** `"127.0.0.1"`

#### `port`

* **Type:** `int`
* **Meaning:** The TCP port to listen on.
* **Default:** `8888`

#### `config_path`

* **Type:** `Optional[str]`
* **Meaning:** Path to a JSON configuration file.
* **When used:** Used when `config_dict` is not provided.

#### `config_dict`

* **Type:** `Optional[dict[str, Any]]`
* **Meaning:** In-memory configuration dictionary.
* **Precedence:** If provided, it is used instead of `config_path`.
* **Validation:** Must be a `dict` or `None`. Any other type raises `TypeError`.

#### Configuration fields used by `run(...)`

This method expects configuration keys such as:

* `version` (optional): selects which backend to run.
* `logger` (optional): logging configuration.
* `hyper_parameters` (optional): backend tuning parameters.

The full set of configuration keys is documented in the [configugration guide](configs.md).

### Outputs

* Returns `None`.
* This call **blocks** until the server exits.
* The server attempts a clean shutdown on `KeyboardInterrupt` and cancellation.

### Examples

#### Minimal usage (no config file)

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")
server.run(host="127.0.0.1", port=8888)
```

#### Load from a JSON config file

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")
server.run(
    host="127.0.0.1",
    port=8888,
    config_path="server.json",
)
```

#### Pass config as a dictionary

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")
server.run(
    host="127.0.0.1",
    port=8888,
    config_dict={
        "logger": {"log_level": "INFO", "enable_console_log": True},
        "version": "python",
    },
)
```

#### Backend selection through config (SDK usage)

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")
server.run(
    host="0.0.0.0",
    port=8888,
    config_dict={
        "version": "python",  # or "rust" depending on your deployment
        "logger": {"log_level": "INFO", "enable_console_log": True},
    },
)
```

## `SummonerServer.run_server`

```python
async def run_server(self, host: str = "127.0.0.1", port: int = 8888) -> None
```

### Behavior

Async entry point that binds a TCP server and runs it forever (Python backend).

* Creates the asyncio server via `asyncio.start_server(...)`.
* Uses `handle_client(...)` for each incoming connection.
* Logs the listening address.
* Runs `serve_forever()` until cancelled.

In typical SDK usage you should call `run(...)`, which handles configuration and lifecycle management. `run_server(...)` is primarily useful when embedding the server into an existing asyncio application.

### Inputs

#### `host`

* **Type:** `str`
* **Meaning:** Bind address.
* **Default:** `"127.0.0.1"`

#### `port`

* **Type:** `int`
* **Meaning:** Bind port.
* **Default:** `8888`

### Outputs

An awaitable coroutine (the method is `async`). It does not return under normal operation because it runs the server forever.

### Examples

#### Embedding in an existing asyncio program

```python
import asyncio
from summoner.server import SummonerServer

async def main():
    server = SummonerServer(name="summoner:server")
    await server.run_server(host="127.0.0.1", port=8888)

asyncio.run(main())
```

## `SummonerServer.handle_client`

```python
async def handle_client(
    self,
    reader: asyncio.streams.StreamReader,
    writer: asyncio.streams.StreamWriter,
) -> None
```

### Behavior

Handles one client connection end-to-end.

* Registers the client connection.
* Repeatedly reads newline-delimited data (`await reader.readline()`).
* For each received line:

  * logs the incoming message,
  * broadcasts a JSON envelope to all other connected clients.
* On disconnect or error:

  * removes the client from internal state,
  * closes the socket,
  * logs the disconnect.

**Broadcast envelope**

Receivers get:

```json
{"remote_addr":"<ip:port>","content":"<line-without-trailing-\\n>"}
```

### Inputs

#### `reader`

* **Type:** `asyncio.StreamReader`
* **Meaning:** Read side of the TCP connection.

#### `writer`

* **Type:** `asyncio.StreamWriter`
* **Meaning:** Write side of the TCP connection.

### Outputs

An awaitable coroutine (the method is `async`). It returns when the client disconnects or the task is cancelled.

### Examples

This method is not typically called directly; it is provided as the callback to `asyncio.start_server(...)`.

## `SummonerServer.set_termination_signals`

```python
def set_termination_signals(self) -> None
```

### Behavior

Installs process termination signal handlers on non-Windows platforms.

* Registers handlers for:

  * SIGINT (Ctrl+C)
  * SIGTERM (process termination)
* Each handler triggers `shutdown()`.

On Windows, signal handler installation is skipped.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

You normally do not call this directly because `run(...)` calls it as part of normal startup.

## `SummonerServer.shutdown`

```python
def shutdown(self) -> None
```

### Behavior

Triggers server shutdown by cancelling all tasks in the server's event loop.

* Logs that shutdown has started.
* Cancels all loop tasks to drive `serve_forever()` and client handlers to exit.

This method is typically invoked through signal handlers or process interruption.

### Inputs

None.

### Outputs

Returns `None`.

### Examples

#### Programmatic shutdown (advanced)

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")

# In a real program, you would call server.run(...) in another thread/process,
# then call server.shutdown() when you want to stop it.
server.shutdown()
```

## `SummonerServer.wait_for_tasks_to_finish`

```python
async def wait_for_tasks_to_finish(self) -> None
```

### Behavior

Waits for all tracked client handler tasks to complete.

* Takes a snapshot of the active tasks under a lock.
* Awaits completion via `asyncio.gather(..., return_exceptions=True)`.

This is used during shutdown to reduce the likelihood of leaving client handlers mid-cleanup.

### Inputs

None.

### Outputs

An awaitable coroutine (the method is `async`). Returns after pending tasks are complete.

### Examples

This method is usually called internally during shutdown sequencing in `run(...)`.

## End-to-end example

### Example: start server and test with netcat

#### server.py

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")
server.run(host="127.0.0.1", port=8888)
```

#### terminal A

```bash
nc 127.0.0.1 8888
```

#### terminal B

```bash
nc 127.0.0.1 8888
```

#### behavior

* Type a line in terminal A.
* Terminal B receives a JSON envelope containing:

  * `remote_addr` (A's address as seen by the server),
  * `content` (the typed line, without the trailing newline).

---

<p align="center">
  <a href="../server.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.server</b></code></a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="./configs.md">Next: <code style="background: transparent;">Summoner<b>.server</b></code> configuration guide &raquo;</a>
</p>
