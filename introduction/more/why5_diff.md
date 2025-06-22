## Why Other Frameworks Feel Different

Frameworks like Anthropic’s MCP and Google’s A2A were designed to orchestrate tools and tasks in enterprise settings. They support structured function calls and monitoring—but they are not built for agent autonomy, mobility, or decentralized interaction.

* **Anthropic MCP** uses JSON-RPC over HTTP or stdio. A central host determines which tools to invoke. There is no concept of peer-to-peer messaging or agent mobility.

* **Google A2A** lets agents advertise capabilities and receive tasks, but all coordination flows through a central actor. Identities are registry-signed; trust is externally granted. There is no agent roaming or graph merging.

These are excellent systems for cloud-based workflows, but they are not suitable for building persistent, decentralized agent ecosystems.

<p align="center">
<img width="300px" src="../../assets/img/other_frameworks_rounded.png" />
</p>

**Summoner** differs in its foundations:

* Identities are self-assigned
* No certificate authority is needed
* Trust arises from interaction, not from registry approval
* Agents communicate peer-to-peer, full-duplex
* Networks compose via shared nodes

This enables **bottom-up growth** and **agent autonomy**. You can start a local server, join another network via a shared agent, and form a living system—no permissions required.

| Feature         | **Summoner**            | MCP (Anthropic)     | A2A (Google)              |
| --------------- | ----------------------- | ------------------- | ------------------------- |
| Agent Mobility  | Yes (`travel()`)        | No                  | No                        |
| Composability   | Graph merge (native)    | Central registry    | Catalog coordination      |
| Peer Messaging  | Direct, duplex TCP      | Routed via host     | Task-based streaming only |
| Code Mobility   | Planned (tool exchange) | No                  | No                        |
| Identity        | Self-assigned           | Host-managed        | Registry-signed JWT       |
| Trust           | Emergent, local         | External authority  | Registry-defined          |
| Infrastructure  | Local or WAN            | Cloud-centric       | Cloud-centric             |
| Discoverability | In progress             | Yes (tool registry) | Yes (Agent Card)          |


MCP and A2A are effective for structured, centralized workflows. Summoner enables a different vision: an internet of **autonomous, persistent, collaborative agents**.

<span style="position: relative; top: -6px; font-size: 0.9em;"><em><u>Page content covered</u></em></span>&nbsp; ![](https://progress-bar.xyz/100)


<p align="center">
  <a href="why4_mmo.md">&laquo; Previous: The Feel of an MMO, Not an API Gateway</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../architecture.md">Next: System Architecture &raquo;</a>
</p>