# Quickstart

An end-to-end, minimal example to bring up your first Summoner agent and server in under five minutes. Follow these steps to see the core flow, then dive deeper via the linked sub-pages.

**Purpose & audience**  
- **Who:** Developers who have installed the SDK and want to see it in action immediately  
- **What:** a bare-bones client-server exchange and pointers to key concepts  
- **Outcome:** understand the “happy path,” so you can customize further

---

## Contents

1. [Prerequisites](prerequesites.md)  
   _Verify your environment meets the minimum requirements_  
2. [Basics](basics.md)  
   _Write and run your first client and server_  
   - [Client](basics_client.md)  
   - [Server](basics_server.md)  
3. [Beginner guide](beginner.md)  
   _Conceptual deep-dive for new users_  
   - [Clients versus agents](begin_client.md)  
   - [Servers versus clients](begin_server.md)  
   - [Agent behaviour as flows](begin_flow.md)  
   - [Async programming and event loops](begin_async.md)  

---

## 1. Prerequisites

Before you begin, confirm:

- Python 3.10+ and `python3` on your PATH  
- `summoner` CLI is available (`summoner --version`)  
- Bash shell (Linux/macOS) or Git Bash (Windows)  
- *(Optional)* Examples repo cloned:  
  ```bash
  git clone https://github.com/Summoner-Network/examples.git
```

> **Copy-template:**
> “Ensure your SDK installation is working by running `summoner --help`. If you cloned our examples repo, navigate into `examples/quickstart` to follow along with code snippets.”

---

## 2. Basics

Run a minimal client–server exchange:

1. **Start the server**

   ```bash
   summoner-server start --port 9000
   ```
2. **Create your agent** (`hello_agent.py`):

   ```python
   from summoner import Agent, run_client

   class HelloAgent(Agent):
       async def on_message(self, msg):
           print("Server says:", msg)
           await self.send("Hello back!")

   if __name__ == "__main__":
       run_client(HelloAgent, server_url="ws://localhost:9000")
   ```
3. **Run the agent**

   ```bash
   python hello_agent.py
   ```
4. **Observe the chat**: the server log and agent console should exchange “Hello” messages.

> **Copy-template:**
> “You’ve just run your first Summoner agent and server. The agent responds to any incoming message from the server by printing it and sending a reply. Next, explore how these components interact under the hood.”

### 2.1 Client

* Define an `Agent` subclass
* Implement `on_message` to handle inbound events
* Use `run_client()` to bootstrap the connection

### 2.2 Server

* Launch via `summoner-server start`
* Configure host, port, and logging via flags
* Routes messages between connected agents

---

## 3. Beginner guide

Solidify your understanding with conceptual explanations and diagrams:

* **Clients vs agents**: client hosts your code; agent is the runtime entity
* **Servers vs clients**: servers route messages; clients execute logic
* **Flows**: structure agent behaviour as a sequence of async steps
* **Async & event loops**: plug into Python’s `asyncio` for concurrency

> **Copy-template:**
> “In Summoner, each agent lives inside a client process. The server handles all message routing. Visualize the flow: Client → Server → Other Client, with asynchronous event loops powering non-blocking I/O.”

---

<p align="center">
  <a href="../installation.md">&laquo; Previous: Installation</a>
  &nbsp;|&nbsp;
  <a href="prerequesites.md">Next: Prerequisites &raquo;</a>
</p>


**Next steps:**

* Fill in the detailed code snippets and diagrams on the sub-pages.
* Adjust any flags or code paths to match your latest API.
* Let me know if you’d like templated sample outputs or sequence diagrams added!




-----


- [Prerequisites](guide_sdk/getting_started/quickstart/prerequesites.md)
- [Basics](guide_sdk/getting_started/quickstart/basics.md)
    - [Client](guide_sdk/getting_started/quickstart/basics_client.md)
    - [Server](guide_sdk/getting_started/quickstart/basics_server.md)
- [Beginner guide](guide_sdk/getting_started/quickstart/beginner.md)
    - [Clients versus agents](guide_sdk/getting_started/quickstart/begin_client.md)
    - [Servers versus clients](guide_sdk/getting_started/quickstart/begin_server.md)
    - [Agent behaviour as flows](guide_sdk/getting_started/quickstart/begin_flow.md)
    - [Async programming and event loops](guide_sdk/getting_started/quickstart/begin_async.md)



<p align="center">
  <a href="../installation.md">&laquo; Previous: Installation of Summoner's SDK</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="prerequisites.md">Next: Prerequisites &raquo;</a>
</p>