## Getting Started

The Summoner platform consists of two main components:

* An SDK for building and organizing your agents
* A desktop app for managing deployment and runtime environments

To get started with the SDK, clone the [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk) repository. For the desktop app, visit the [`summoner-desktop`](https://github.com/Summoner-Network/summoner-desktop) repository. The desktop app is fully functional today, but future versions may require you to create an account.

If you're looking to install and use the desktop app, refer to the [Desktop App Guide](../../guide_app/index.md). This section of the documentation focuses on the SDK: how to install it, run clients and servers locally, and use sample agents from the [`summoner-agents`](https://github.com/Summoner-Network/summoner-agents) repository.

The `summoner-sdk` is modular. It is built around a core library (`summoner-core`) and includes optional features that can be added or removed depending on your needs. We will showcase the SDK using both core components and common add-ons — for example, the agent classes from [`summoner-creatures`](https://github.com/Summoner-Network/summoner-creatures), which provide decentralized identity, cryptographic functionality, and other capabilities to extend core client behavior.

This section will walk you through:

1. A general overview of the SDK and its role in the Summoner ecosystem
2. Installation instructions
3. A quickstart tutorial with minimal code examples
4. A beginner’s guide explaining the architecture (clients, servers, agents), and key concepts such as async flows and event loops

### Documentation Structure

1. [What is the Summoner SDK for?](what_is.md)
   *When and how to use the SDK in your projects*

2. [Installation](installation.md)
   *How to obtain and verify the SDK package*

3. [Quickstart](quickstart/index.md)
   *Core principles and minimal working examples*

   * [Prerequisites](quickstart/prerequesites.md)
   * [Basics](quickstart/basics.md)

     * [Client](quickstart/basics_client.md)
     * [Server](quickstart/basics_server.md)
   * [Beginner guide](quickstart/beginner.md)

     * [Clients vs Agents](quickstart/begin_client.md)
     * [Servers vs Clients](quickstart/begin_server.md)
     * [Agent behavior as flows](quickstart/begin_flow.md)
     * [Async programming and event loops](quickstart/begin_async.md)

<hr><hr>

<p align="center">
  <a href="../index.md">&laquo; Previous: Summoner SDK Guides</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="what_is.md">Next: What is the Summoner SDK for? &raquo;</a>
</p>

<hr><hr>
