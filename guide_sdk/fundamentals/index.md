# Essentials on Summoner's intended coding style


Explain that there is a philsopy to get things right in async

Some messages are starved and listenning needs to be a loop until it triggers

- [Clients and agents](client_agent.md)
- [Servers and relay](server_relay.md) 
- [Traveling between servers](traveling.md)
- [Agent behaviour as flows](flow.md) 

---------

# Fundamentals

> Deepen your understanding of Summoner’s core abstractions, message flow, and runtime patterns.

**Purpose & audience**  
- **Who:** developers who have tried the Quickstart and want to master the building blocks  
- **What:** detailed conceptual guides on each fundamental component  
- **Outcome:** confidently architect and troubleshoot client, server, and flow-based systems

---

## Prerequisites

- Working Summoner SDK installation  
- Familiarity with Python `asyncio` (see [Async programming and event loops](async.md))  
- Basic knowledge of agents and relay servers (see [Quickstart](../getting_started/quickstart/index.md))

---

## Contents

### 1. Clients and agents  
[fundamentals/client_agent.md]  
Explore the distinctions and interactions between client processes and agent instances. Learn how identity, lifecycle hooks, and protocol handlers define your agent’s behavior.

### 2. Servers and relay  
[fundamentals/server_relay.md]  
Understand the relay’s role as a message router. Cover configuration, scaling strategies, trust boundaries, and best practices for monitoring and high availability.

### 3. Traveling between servers  
[fundamentals/traveling.md]  
Discover how agents migrate across relay nodes. Topics include state serialization, reconnection logic, and orchestrating seamless handoffs in a distributed network.

### 4. Agent behaviour as flows  
[fundamentals/flow.md]  
Delve into the flow-based model: defining states, transitions, and routes. See how FSM patterns, category-inspired composition, and higher abstractions simplify complex protocols.

### 5. Async programming and event loops  
[fundamentals/async.md]  
A focused look at Python’s `asyncio` in Summoner: event loop lifecycles, coroutine scheduling, integrating async databases and queues, and handling back-pressure.

---

<p align="center">
  <a href="../getting_started/quickstart/begin_async.md">&laquo; Previous: Async Programming</a>
  &nbsp;|&nbsp;
  <a href="client_agent.md">Next: Clients and Agents &raquo;</a>
</p>




<p align="center">
  <a href="../getting_started/quickstart/begin_async.md">&laquo; Previous: Beginner's Guide to Async Programming </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="client_agent.md">Next: Clients and Agents &raquo;</a>
</p>