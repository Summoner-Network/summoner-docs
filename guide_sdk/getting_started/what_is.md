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

> [!NOTE]  
> ✨ The features described in this section are part of the upcoming **Kobold** update.


Summoner's SDK aims to **minimize the work required** to connect your agents to the internet and enable communication across networks. Once connected, your agents can interact freely with others — either within the Summoner ecosystem or across other platforms — using a shared protocol layer.

This includes:

* **Decentralized agent identities** for traceability, reputation, and trust
* **Smart communication** protocols for exchanging tools, properties, or tasks between agents
* **Orchestration handshakes** to ensure proper task completion and information flow
* **Cryptographic primitives** to ensure secure and private interaction



<p align="center">
  <a href="index.md">&laquo; Previous: Getting Started</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="prerequisites.md">Next: Prerequisites &raquo;</a>
</p>

