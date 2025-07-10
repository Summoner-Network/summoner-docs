# Beginner's Guide to Async Programming

Explain the principles of parallelism and async

Explain the async database use (important)

Explain which function is async and it is just a matter of putting
`async`

Explain that this is needed when using asqlite or asyncio.queue

-------


# Beginner’s Guide to Async Programming

> Learn the fundamentals of Python’s `asyncio` model as used by Summoner, and how to integrate async databases and queues into your agents.

**Purpose & audience**  
- **Who:** developers new to asynchronous programming in Python  
- **What:** core concepts of `async`/`await`, event loops, async databases, and queues  
- **Outcome:** write non-blocking agent code that uses `aiosqlite` and `asyncio.Queue` effectively

---

## 1. Concurrency vs Parallelism

- **Concurrency**  
  - Multiple tasks in progress, sharing a single thread  
  - Ideal for I/O-bound workloads  
- **Parallelism**  
  - Multiple tasks truly running at once on separate cores  
  - Python’s GIL limits true parallelism for CPU-bound code

> **Sample copy:**  
> “Summoner leverages concurrency: your agent can await network I/O, database calls, and timers without blocking other tasks.”

---

## 2. Event Loop Basics

- **Event loop**  
  - Drives all async execution (`asyncio.get_event_loop()`)  
  - Queues and schedules coroutines  
- **`run_client()` / `run_server()`**  
  - Under the hood, these start and manage the loop  
  - Gracefully handle shutdown on signals

> **Sample copy:**  
> “You don’t need to create the loop yourself—call `run_client(MyAgent)` and let Summoner wire everything up.”

---

## 3. Defining Async Functions

- Prefix with `async def`  
- Use `await` to call other coroutines  
- Cannot call `await` in a regular function

```python
async def fetch_data():
    data = await some_network_call()
    return data
````

> **Tip:** If you need to run blocking code (e.g., CPU work), offload with `loop.run_in_executor()`.

---

## 4. Async Databases with `aiosqlite`

1. **Open a connection** in `setup()`:

   ```python
   import aiosqlite

   class MyAgent(Agent):
       def setup(self):
           self.db = asyncio.get_event_loop().run_until_complete(
               aiosqlite.connect("state.db")
           )
   ```
2. **Use `await` for queries**:

   ```python
   async def log_event(self, event):
       await self.db.execute("INSERT INTO events (msg) VALUES (?)", (event,))
       await self.db.commit()
   ```
3. **Close on teardown**:

   ```python
   async def teardown(self):
       await self.db.close()
   ```

> **Sample copy:**
> “Using `aiosqlite` lets your agent read/write state without blocking the event loop—queries become first-class coroutines.”

---

## 5. Queues for Message Buffering

* **`asyncio.Queue`**

  * Thread-safe FIFO buffer for coroutines
  * Ideal for decoupling producers and consumers

```python
class MyAgent(Agent):
    def setup(self):
        self.queue = asyncio.Queue()
    
    async def on_message(self, msg):
        await self.queue.put(msg)

    async def background_task(self):
        while True:
            msg = await self.queue.get()
            self.logger.info(f"Processing {msg}")
```

> **Sample copy:**
> “Use queues to buffer messages or tasks—your agent can push into the queue in `on_message` and consume in a separate background task.”

---

## 6. Putting It Together

```python
import asyncio
import aiosqlite
from summoner import Agent, run_client

class AsyncAgent(Agent):
    def setup(self):
        self.queue = asyncio.Queue()
        self.db = asyncio.get_event_loop().run_until_complete(
            aiosqlite.connect("state.db")
        )
        self.loop.create_task(self.process_queue())

    async def on_message(self, msg):
        await self.queue.put(msg)

    async def process_queue(self):
        while True:
            msg = await self.queue.get()
            await self.db.execute("INSERT INTO msgs (content) VALUES (?)", (str(msg),))
            await self.db.commit()

    async def teardown(self):
        await self.db.close()

if __name__ == "__main__":
    run_client(AsyncAgent, host="127.0.0.1", port=8888)
```

> **Copy-template:**
> “This example shows a background task consuming a queue and persisting messages asynchronously to SQLite, all without blocking the agent’s main loop.”

---

<p align="center">
  <a href="begin_flow.md">&laquo; Previous: Agent Flows</a>
  &nbsp;|&nbsp;
  <a href="../../fundamentals/index.md">Next: Fundamentals</a>
</p>



<p align="center">
  <a href="begin_flow.md">&laquo; Previous: Beginner's Guide to Agent's Flows </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../../fundamentals/index.md">Next: Fundamentals &raquo;</a>
</p>