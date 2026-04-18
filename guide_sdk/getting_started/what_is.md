## What Does the Summoner SDK Do?

The Summoner SDK provides the logic layer that connects your agents to the open internet — whether they run on your local machine, a local server, or in the cloud.


Summoner is built around core principles of **ownership** and **privacy**. For this reason, we prioritize **local-first deployments**: you can run agents on your own hardware and connect them over wide-area networks (WAN) to other agents, whether hosted by peers or on private servers. That said, we also support — and are actively improving — options for cloud-based deployment.

<p align="center">
  <img width="240px" src="../../assets/img/summoner_build_machine_rounded.png" />
</p>

At its core, the SDK is designed to **orchestrate agents**. These agents can:

* Be built with other frameworks and connected to Summoner's network through simple wrappers or interfaces
* Be written natively using our SDK (see examples in our [`summoner-agents`](https://github.com/Summoner-Network/summoner-agents) repository)

Once agents are connected, you can link them to the desktop app to simplify deployment and setup. The desktop app supports tasks like dependency installation, configuration management, and decentralized identity generation for your agents. For more, see the [Desktop App Guide](../../guide_app/index.md).

### Why it Matters

Summoner's SDK aims to **minimize the work required** to connect your agents to the internet and enable communication across networks. Once connected, your agents can interact freely with others — either within the Summoner ecosystem or across other platforms — using a shared protocol layer.

At the **core** layer, this includes:

* **Async clients and relays** for open TCP-based communication
* **Routes, flows, triggers, and hooks** for structuring agent behavior
* **DNA portability** so client behavior can be exported, merged, or reconstructed

On top of that, **optional extensions** such as [Aurora](../../reference/lib_agent/aurora.md) can add identity records, envelope handling, policy hooks, and richer handshake layers when your agents need them. The broader extension space is documented in the [Agent Extensions reference](../../reference/lib_agent/index.md), and Aurora's main client class is documented on [`SummonerAgent`](../../reference/lib_agent/aurora/agent.md).



<p align="center">
  <a href="index.md">&laquo; Previous: Getting Started</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="prerequisites.md">Next: Prerequisites &raquo;</a>
</p>
