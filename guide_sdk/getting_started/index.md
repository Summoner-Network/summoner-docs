## Getting Started

The Summoner platform is designed to help you create and run intelligent agents, with a focus on modularity and local-first development. It consists of two core components:

* **An SDK** for building, customizing, and orchestrating agents
* **A Desktop App** for managing deployment, testing, and runtime environments

To begin, you can clone the [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk) repository, which contains everything you need to create and run agents. If you prefer managing agents through a graphical interface, visit the [`summoner-desktop`](https://github.com/Summoner-Network/summoner-desktop) repository. The desktop app is fully functional today, though future versions may require account creation for cloud features.


<p align="center">
  <img width="240px" src="../../assets/img/reading_summoner_rounded.png" />
</p>

> [!NOTE]
> If you are looking to install and use the desktop app, refer to the [Desktop App Guide](../../guide_app/index.md).
>
> This section of the documentation focuses on the SDK: how to install it, run clients and servers locally, and use sample agents from the [`summoner-agents`](https://github.com/Summoner-Network/summoner-agents) repository.

The SDK is modular by design. It is built around a core library (`summoner-core`) and includes optional components that you can add or remove as needed. We will showcase the SDK using both its core modules and common extensions — for example, the agent classes from [`extension-agentclass`](https://github.com/Summoner-Network/extension-agentclass), which add decentralized identity, cryptographic tools, and other runtime capabilities.

---

**This section will guide you through:**

### 1. Understanding the SDK's role in the Summoner ecosystem

* [What does the Summoner SDK do?](what_is.md)

### 2. Setting up your development environment

* [Prerequisites](prerequisites.md): What you need before installing
* [Installation](installation.md): Step-by-step setup instructions

### 3. Exploring the SDK through a beginner-friendly walkthrough

* [Quickstart](quickstart/index.md): Your starting point

  * [Basics](quickstart/basics.md): Initial concepts and interactions
    * [Server](quickstart/basics_server.md)
    * [Client](quickstart/basics_client.md)
    
  * [Beginner guide](quickstart/begin.md): Foundational ideas

    * [Servers vs Clients](quickstart/begin_server.md)
    * [Clients vs Agents](quickstart/begin_client.md)
    * [Agent behavior as flows](quickstart/begin_flow.md)
    * [Async programming and event loops](quickstart/begin_async.md)

---

Whether you are exploring agent-based programming for the first time or integrating Summoner into a larger system, the upcoming pages will equip you with practical tools and a clear mental model of how everything fits together.

<p align="center">
  <a href="../index.md">&laquo; Previous: Summoner SDK Guides</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="what_is.md">Next: What Does the Summoner SDK Do? &raquo;</a>
</p>
