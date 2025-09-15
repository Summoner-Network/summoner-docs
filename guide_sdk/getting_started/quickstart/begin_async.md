# Working with Asynchronous Programming in Summoner

> A practical guide to concurrency in Summoner: how the event loop runs, which parts of the client are `async`, how receive/send overlap, and how to wire in async DBs, queues, and one-time setup safely.

<p align="center">
  <img width="300px" src="../../../assets/img/begin_async_summoner_rounded.png"/>
</p>

## Concurrency, not (necessarily) parallelism

Summoner's Python client rides on `asyncio`. The model is cooperative: your coroutines *yield* at `await` points, and the loop gives time to other tasks. This is perfect for network I/O — such as sockets, databases, and files — where most time is spent waiting. It is not automatic parallelism: CPU-heavy work in a handler will pause everything else until you move it off the loop (threads or processes). In practice, aim for short, mostly-I/O handlers that always `await` their external calls.

Under the hood, some pieces delegate to Rust via PyO3 and run on **Tokio**. That does not change your code shape — you still `await` — but it does mean the heavy lifting on the wire happens in non-blocking Rust, often with the GIL released. The net effect is a responsive Python loop with predictable back-pressure.

## Where `async` lives in the client

Everything you register is asynchronous. The runtime awaits your coroutines. The table below maps the surface area:

| Registration                   | Handler shape                                      | Purpose                                                              |
| ------------------------------ | -------------------------------------------------- | -------------------------------------------------------------------- |
| `@client.receive(route=...)`   | `async def (payload) -> Optional[Event]`           | Normalize input; propose outcomes (`Move` / `Stay` / `Test`).        |
| `@client.send(route=..., ...)` | `async def () -> Optional[Union[str, dict, list]]` | Emit messages (ticks or hubs). `multi=True` returns a list to batch. |
| `@client.hook(...)`            | `async def (payload) -> Optional[payload]`         | Pre/post processing (auth, schema, stamping, rate limits).           |
| `@client.upload_states()`      | `async def (payload) -> state-shape`               | Advertise current node(s) to the flow engine.                        |
| `@client.download_states()`    | `async def (proposals) -> None`                    | Commit chosen node(s) from the proposals.                            |


Behind those handlers is a plain TCP socket with newline-delimited frames (JSON Lines by default). Python uses asyncio streams, and many servers use Rust/Tokio. As long as framing and schema match, both sides remain non-blocking. Writers back off with `drain()`, and readers `await readline()`.

## How the runtime executes

`client.run(...)` starts the client and keeps two long-lived coroutines in flight:

* **Receiver**: reads, runs RECEIVE hooks, selects eligible `@receive` by route/state, awaits each, and aggregates outcomes into a single proposal set.
* **Sender**: ticks and hubs run independently; SEND hooks stamp payloads; writes go out with back-pressure (`drain()`), so the loop never busy-spins.

These two loops *overlap*. There is no polling and no shared sleep you need to manage. On a single inbound frame, you will see:

```
upload_states ──► select receivers ──► run @receive ──► aggregate outcomes
      ▲                                                 │
      └───────────── download_states ◄──────────────────┘
                                  │
                                  └──► @send (ticks + hubs) ──► socket
```

A few details matter in practice:

* **Ordering.** Reads are FIFO per connection. Within a tick, multiple receivers can run (by priority, or per-key). Summoner aggregates all outcomes first, then calls `download_states()` once. That is why your receivers should be pure and your commit logic centralized.
* **Back-pressure.** If the socket cannot flush immediately, `StreamWriter.drain()` yields. Your senders will simply progress more slowly, and you do not have to throttle by hand unless you *want* lower cadence.
* **Fairness.** Because everything yields, a long chain of small awaits remains responsive. The main culprit for "unfairness" is accidental blocking (sync DB calls, `time.sleep`, large JSON dumps). Avoid those, or push them off the loop.

## Running one or many clients

Inside a single client you can compose coroutines freely — `await`, `asyncio.gather`, timeouts — just like any asyncio app. Across multiple clients in one process, remember that `.run(...)` owns *its* event loop and blocks that thread. Two workable patterns:

* **Straightforward:** one **thread or process per client**, each calling `.run(...)`. This keeps loops isolated and failure domains small.
* **Advanced orchestration:** drive `client.run_client(...)` yourself on the client's loop:

```python
import threading

def launch(client, host, port, cfg):
    def boot():
        # decorators must be imported before booting
        # if you use flow arrows, define styles and call flow.ready() first
        client.loop.run_until_complete(
            client.run_client(host=host, port=port, config_path=cfg)
        )
    t = threading.Thread(target=boot, daemon=True)
    t.start()
    return t
```

`.run(...)` adds "bookends" (config load, flow activation/`ready()`, signal handlers, graceful shutdown). If you call `run_client(...)` directly, perform whatever prep your client needs (especially `flow.add_arrow_style(...)` and `flow.ready()` if you use routes with arrows).

## Fan-out safely with `gather`

If a handler issues independent I/O operations such as DB and HTTP, schedule them concurrently and await them together:

```python
@client.receive(route="")
async def rx(msg):
    user_coro  = db_get_user(msg["uid"])
    flags_coro = http_get_feature_flags(msg["uid"])
    user, flags = await asyncio.gather(user_coro, flags_coro)
    ...
```

If you want fault isolation, wrap with a timeout or collect exceptions:

```python
import asyncio

async def with_timeout(coro, seconds):
    return await asyncio.wait_for(coro, timeout=seconds)

res = await asyncio.gather(
    with_timeout(user_coro, 1.0),
    with_timeout(flags_coro, 0.5),
    return_exceptions=True,
)
```

The goal is always the same: keep the loop yielding and never perform synchronous waits for I/O that you could `await`.

## Async databases (pattern, not ceremony)

Using an async driver keeps handlers non-blocking. The pattern is simple: open once, `await` every operation, and keep transactions short.

```python
import aiosqlite, asyncio
from summoner.client import SummonerClient
from typing import Any, Optional

client = SummonerClient()
_db: Optional[aiosqlite.Connection] = None

async def setup():
    global _db
    _db = await aiosqlite.connect("example.db")
    await _db.execute("""CREATE TABLE IF NOT EXISTS hits(
        k TEXT PRIMARY KEY, n INTEGER NOT NULL)""")
    await _db.commit()

@client.receive(route="")
async def count(msg: Any) -> None:
    if not isinstance(msg, dict) or "k" not in msg:
        return
    async with _db.execute("SELECT n FROM hits WHERE k=?", (msg["k"],)) as cur:
        row = await cur.fetchone()
    n = (row[0] if row else 0) + 1
    await _db.execute("INSERT OR REPLACE INTO hits(k,n) VALUES(?,?)", (msg["k"], n))
    await _db.commit()

@client.send(route="")
async def report():
    await asyncio.sleep(2)  # gentle pacing; yields the loop
    async with _db.execute("SELECT SUM(n) FROM hits") as cur:
        row = await cur.fetchone()
    return {"kind": "stats", "total_hits": int(row[0] or 0)}

client.loop.run_until_complete(setup())
client.run(host="127.0.0.1", port=8888)
```

A few DB notes that save pain:

* Most drivers are not process safe. Do not share a connection across processes. If you run multiple clients, give each its own connection.
* Avoid holding a database lock across other awaits. The moment you `await`, control can switch, and you can serialize unrelated work.
* If you return an Event from a receiver, annotate as `Optional[Event]`.

```python
async def teardown():
    if _db is not None:
        await _db.close()

# later, on exit path (if you manage your own loop/threads):
client.loop.run_until_complete(teardown())
```

## Queues for producer/consumer

In practice, `asyncio.Queue` is the easiest way to stage work between receivers and senders without blocking. While receivers *produce* normalized items, tick senders *consume* and emit:

```python
import asyncio
from summoner.client import SummonerClient
from typing import Any, Optional

client = SummonerClient()
inbox: asyncio.Queue[dict] = asyncio.Queue()

@client.receive(route="")
async def enqueue(msg: Any):
    if isinstance(msg, dict):
        await inbox.put({"when": asyncio.get_running_loop().time(), **msg})

@client.send(route="")
async def drain() -> Optional[dict]:
    try:
        item = inbox.get_nowait()
    except asyncio.QueueEmpty:
        await asyncio.sleep(0.2)  # polite idle yield
        return
    return {"kind": "processed", **item}
```

You can also batch: declare `multi=True` on the sender and drain multiple items per tick to smooth bursts.

```python
@client.send(route="", multi=True)
async def drain_batch():
    items = []
    for _ in range(10):
        try:
            items.append(inbox.get_nowait())
        except asyncio.QueueEmpty:
            break
    if not items:
        await asyncio.sleep(0.2)
        return
    return [{"kind": "processed", **it} for it in items]
```

## Why asyncio streams (client) and Tokio (server)?

Summoner chooses boring tech for the wire: newline-delimited TCP frames. The benefits are tangible:

* **Clarity.** A frame is a line. Debugging is `tail -f` friendly. If you want JSON Lines, you have it by default.
* **Back-pressure.** `await StreamWriter.drain()` (Python) and Tokio sinks (Rust) answer *"can the OS accept more bytes?"* by **suspending the coroutine** until the socket is writable again. The scheduler resumes you when there is capacity. This naturally throttles output; neither side busy-loops.
* **Interoperability.** Anything that can read/write lines over TCP can talk to you. It also makes it trivial to swap in a TLS wrapper when needed.

If you do need multiplexing or request/response correlation, put it at the schema level (IDs in messages), not as extra sockets.

## One-time setup on startup

Run warmups and setup first: warm caches, create directories, run migrations. Then start the client loop.

```python
async def setup(): ...

# ... your code here ...

client.loop.run_until_complete(setup())
client.run(...)
```

This ensures you do not carry partially initialized state into your handlers.

## Pitfalls & quick fixes

Most problems come from blocking the loop or mismatched expectations about ownership.

| Situation                                                     | Why it happens                                            | What to do                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `time.sleep(...)` in a handler                                | Blocks the event loop                                     | Replace with `await asyncio.sleep(...)`.                                                                                                                                                                                                                                                                                            |
| Sync console I/O in hot paths (`BlockingIOError`, mixed logs) | Stdout/stderr are not awaitable                            | Use `aioconsole.aprint/ainput` **everywhere inside async handlers** (or the client's logger). Avoid `print` in coroutines.                                                                                                                                                                                                          |
| "Queue 80% full" warnings                                     | You are producing faster than you can send                 | Pace tick senders, batch (`multi=True`), or lower per-tick fan-out.                                                                                                                                                                                                                                                                 |
| Long transactions pin other work                              | Locks held across awaits                                  | Keep them short; avoid `await` while holding a lock when you can refactor.                                                                                                                                                                                                                                                          |
| `asyncio.gather(client.run(...), ...)` across clients         | Each client owns its loop; `.run(...)` blocks that thread | Run each client in its own thread or process and call `.run(...)`. For an advanced setup, drive `client.run_client(...)` on that client’s event loop inside a dedicated thread using `client.loop.run_until_complete(...)`. If you bypass `.run(...)`, replicate its setup and teardown: load configuration, define arrow styles, call `flow.ready()`, and install signal handlers. |
| CPU-heavy work slows everything                               | Concurrency ≠ parallelism                                 | Offload with `asyncio.to_thread(...)` or a process pool; keep handlers I/O bound. Rust/Tokio code may run without the GIL, but that does not make Python handlers parallel.                                                                                                                                                          |
| Long-running tasks ignore shutdown                            | Not handling `CancelledError`                             | Wrap long loops with `try/except asyncio.CancelledError: ...` and clean up (close DB cursors, flush queues).                                                                                                                                                                                                                        |
<p align="center">
  <a href="begin_flow.md">&laquo; Previous: Orchestrating Agent Using Flows </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../../fundamentals/index.md">Next: Fundamentals &raquo;</a>
</p>