# Summoner SDK Guides

This section helps you learn how to use the Summoner SDK — from setup to advanced usage. It begins with installation and basic concepts, then covers client-server architecture, agent flows, and asynchronous behavior. Finally, it provides step-by-step how-tos and advanced techniques for customizing or extending your system.

---

We begin with an introduction to the SDK, its core principles, and installation process:

[**Getting Started**](getting_started/index.md)

* [What Does the Summoner SDK Do?](getting_started/what_is.md)
* [Prerequisites](getting_started/prerequisites.md)
* [Installation](getting_started/installation.md)
* [Quickstart](getting_started/quickstart/index.md)

To deepen your understanding, the next section explains the core concepts needed to manage and orchestrate agent behavior effectively:

[**Fundamentals**](fundamentals/index.md)

* [Clients and agents](fundamentals/client_agent.md)
* [Servers and relays](fundamentals/server_relay.md)
* [Traveling between servers](fundamentals/traveling.md)
* [Agent behavior as flows](fundamentals/flow.md)
* [Async programming and event loops](fundamentals/async.md)

The **How-tos** provide step-by-step guides to apply the fundamentals in practical settings and extend your own stack:

[**How-tos**](howtos/index.md)

* **Client**

  * [Design and create agents](howtos/client/design_create.md)
  * [Configure agent identity](howtos/client/id.md)
  * [Set up an asynchronous database](howtos/client/async_db.md)
  * [Persist agent state](howtos/client/state_persist.md)
  * [Organize agent behavior as asynchronous tasks](howtos/client/async_task.md)

* **Server**

  * [Set up a server on Linux](howtos/server/setup_linux.md)
  * [Set up a server on macOS](howtos/server/setup_macos.md)
  * [Expose a local server to the internet](howtos/server/to_internet.md)

* **System**

  * [Debug clients, servers, and agents](howtos/system/debug.md)
  * [Integrate your own agent stack](howtos/system/integrate.md)

* **Protocol**

  * [Handle multiparty interactions](howtos/proto/multiparty.md)
  * [Validate messages and build a reputation system](howtos/proto/validation.md)
  * [Encrypt and decrypt messages](howtos/proto/encrypt_decrypt.md)
  * [Create handshakes with collaborators](howtos/proto/handshakes.md)

The **Advanced Usage** section is intended primarily for internal development, but users are welcome to explore it. It includes experimental or upcoming capabilities that will shape future add-ons and extensions of the SDK:

[**Advanced Usage**](advanced_usage/index.md)

* [Mix agent behaviors](advanced_usage/merge.md)
* [Advanced server setup](advanced_usage/server_setup.md)
* [Advanced agent setup](advanced_usage/agent_setup.md)
* [Create a safe sandbox server](advanced_usage/sandbox.md)
* [Build your own agent framework on top of Summoner](advanced_usage/agent_framework.md)

---

### What Next?

Once you are ready to try the SDK in a real-world setting, we recommend starting with the [**Desktop App Guide**](guide_app/index.md), which walks through creating and deploying a working agent inside the official Summoner Desktop App.

<p align="center">
  <a href="../introduction/minisdk/conclusion.md">&laquo; Previous: From miniSummoner to Summoner</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="getting_started/index.md">Next: Getting Started &raquo;</a>
</p>
