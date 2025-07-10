# Async Programming and Event Loops


NOTE: refer to the agent library if needed

This is the opportunity to illustrate all concepts of create_task and run_until_completion I use in each example 

---------


# Async Programming and Event Loops

> A deep dive into Python’s `asyncio` model as leveraged by Summoner, covering task scheduling, blocking operations, and integration with agent lifecycles.

**Purpose & audience**  
- **Who:** developers building production-grade agents and servers with Summoner  
- **What:** in-depth patterns for the event loop, creating and managing tasks, and handling blocking work  
- **Outcome:** write robust, non-blocking code that cleanly integrates with Summoner’s `run_client` and `run_server`

---

## 1. The Event Loop

Summoner’s CLI entrypoints (`run_client`, `run_server`) create and run an `asyncio` event loop under the hood. The loop:

- **Schedules coroutines** and callbacks  
- **Manages I/O** (network sockets, timers)  
- **Handles shutdown** on signals (SIGINT/SIGTERM)  

> **Sample copy:**  
> “You rarely need to call `asyncio.get_event_loop()` directly. Instead, override lifecycle hooks—Summoner will call them inside the managed loop.”

---

## 2. Creating and Scheduling Tasks

### 2.1 `create_task`

Use `self.loop.create_task(...)` inside your agent’s `setup()` hook to fire-and-forget background work:

```python
class MyAgent(Agent):
    def setup(self):
        # start a periodic heartbeat task
        self.loop.create_task(self._heartbeat())

    async def _heartbeat(self):
        while True:
            await asyncio.sleep(30)
            self.logger.info("heartbeat")
````

* Tasks run concurrently with message handlers
* Errors in a task don’t crash the loop; attach exception handlers if needed

### 2.2 `ensure_future`

An alternative to `create_task`, returning a `Task` object you can await or cancel:

```python
task = asyncio.ensure_future(self._cleanup())
await task  # wait for it to finish
```

---

## 3. Blocking Code and Executors

### 3.1 `run_in_executor`

Offload CPU-bound or blocking calls to a separate thread or process:

```python
result = await self.loop.run_in_executor(
    None,  # default thread pool
    blocking_function, arg1, arg2
)
```

* Keeps the event loop responsive
* Useful for heavy computation or legacy blocking APIs

---

## 4. Waiting for Completion

### 4.1 `run_until_complete`

In non-Summoner scripts (e.g. one-off utilities), you may use:

```python
loop = asyncio.get_event_loop()
loop.run_until_complete(main_coroutine())
```

* Blocks the current thread until the coroutine finishes
* **Do not** mix with `run_client`/`run_server`—use only in standalone scripts

---

## 5. Cancellation and Cleanup

* **Cancel a task:**

  ```python
  task.cancel()
  try:
      await task
  except asyncio.CancelledError:
      pass
  ```
* **Graceful shutdown:** implement `async def teardown(self):` in your agent to close resources (e.g., database connections, file handles).

> **Sample copy:**
> “Summoner calls your agent’s `teardown()` when the loop is stopping. Use it to cancel any background tasks and clean up state.”

---

## 6. Integrating with Summoner

Summoner agents and servers expose `self.loop`, so you can schedule tasks anywhere:

* **In `setup()`:** initialize queues, databases, and tasks
* **In `on_connect()`:** start session-specific coroutines
* **In `teardown()`:** cancel tasks, close connections

```python
class AsyncAgent(Agent):
    def setup(self):
        self.processor = self.loop.create_task(self._process_queue())

    async def teardown(self):
        self.processor.cancel()
        await self.processor
```

---

<p align="center">
  <a href="flow.md">&laquo; Previous: Agent behaviour as Flows</a>
  &nbsp;|&nbsp;
  <a href="../howtos/index.md">Next: How-tos</a>
</p>





<p align="center">
  <a href="flow.md">&laquo; Previous: Agent behaviour as Flows </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../howtos/index.md">Next: "How-to" tutorials &raquo;</a>
</p>