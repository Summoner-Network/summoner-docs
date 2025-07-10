# Summoner SDK Guides

> A single place to explore everything you need—from first install to expert-level customizations—using a version-agnostic approach.

**Purpose & audience**  
- **Who:** software engineers and architects building with the Summoner SDK  
- **What:** conceptual overviews, step-by-step recipes, and deep dives  
- **Goal:** get you productive quickly, while also giving you patterns to scale and extend

**Prerequisites**  
- Python 3.10+ (or your preferred supported runtime)  
- Basic understanding of asynchronous programming  
- Familiarity with agent-based or event-driven architectures (helpful but not required)

---

## Contents

### 1. Getting started  
Learn how to install the SDK and run your first agent in minutes.  
- **What is the Summoner SDK for?**  
  - Key concepts: client, server, agent, relay  
  - Common use-cases  
- **Installation**  
  - Package requirements  
  - Supported platforms  
- **Quickstart**  
  - Your first “Hello, world” agent  
  - Brief walkthrough of code structure  

### 2. Fundamentals  
Understand the core abstractions and how they fit together.  
- **Clients and agents**  
  - Roles & responsibilities  
  - Identity and lifecycle  
- **Servers and relay**  
  - Message routing  
  - Scaling considerations  
- **Traveling between servers**  
  - Agent mobility model  
  - State serialization & restore  
- **Agent behaviour as flows**  
  - Defining FSM-style logic  
  - Tips for clarity and maintainability  
- **Async programming and event loops**  
  - Integrating with asyncio  
  - Best practices for error handling  

### 3. How-tos  
Hands-on recipes for common tasks.  
- **Client**  
  - Design and create agents  
  - Configure agent identity  
  - Set up an asynchronous database  
  - Persist agent states  
  - Organize behaviour as async tasks  
- **Server**  
  - Install & configure on Linux and macOS  
  - Expose a local server to the Internet  
- **System**  
  - Debug clients, servers, and agents  
  - Integrate your own agent stack  
- **Protocol**  
  - Multiparty interactions  
  - Message validation & reputation systems  
  - Encrypt and decrypt messages  
  - Establish secure handshakes  

### 4. Advanced usage  
Patterns and extensions for power users.  
- Mix agent behaviours for complex workflows  
- Custom server architectures & plugins  
- Fine-tune client performance  
- Build a simple game/event system  
- Create your own agent framework on top of Summoner  


## [***Getting started***](getting_started/index.md)
- [What is the Summoner SDK for?](getting_started/what_is.md)
- [Installation](getting_started/installation.md)
- [Quickstart](getting_started/quickstart/index.md)


## [***Fundamentals***](fundamentals/index.md)
- [Clients and agents](fundamentals/client_agent.md)
- [Servers and relay](fundamentals/server_relay.md) 
- [Traveling between servers](fundamentals/traveling.md)
- [Agent behaviour as flows](fundamentals/flow.md) 
- [Async programming and event loops](fundamentals/async.md)

## [***How-tos***](howtos/index.md)
* **Client**
    - [Design and create agents](howtos/client/design_create.md)
    - [Configure agent identity](howtos/client/id.md)
    - [Set up an asynchronous database](howtos/client/async_db.md)
    - [Persist agent states](howtos/client/state_persist.md)
    - [Organize agent behavior as asynchronous tasks](howtos/client/async_task.md)
* **Server**
    - [Set up a server on linux](howtos/server/setup_macos.md)
    - [Set up a server on macos](howtos/server/setup_linux.md)
    - [Open (local) server to the internet](howtos/server/to_internet.md)
* **System**
    - [Debug clients, servers and agents](howtos/system/debug.md)
    - [Integrate and connect your own agent stack](howtos/system/integrate.md)
* **Protocol**
    - [Multiparty handling](howtos/proto/multiparty.md)
    - [Validate messages and build a reputation ststem](howtos/proto/validation.md)
    - [Encrypt and decrypt messages](howtos/proto/encrypt_decrypt.md)
    - [Create handshake with your collaborators](howtos/proto/handshakes.md)

## [***Advanced usage***](advanced_usage/index.md)
- [Mix agent behaviors](advanced_usage/merge.md)
- [Advanced server setup](advanced_usage/server_setup.md)
- [Advanced client setup](advanced_usage/client_setup.md)
- [Create a game using Summoner](advanced_usage/game_event.md)
- [Create your own agent framework using Summoner](advanced_usage/agent_framework.md)



<p align="center">
  <a href="../introduction/minisdk/conclusion.md">&laquo; Previous: From miniSummoner to Summoner</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="getting_started/index.md">Next: Getting Started &raquo;</a>
</p>