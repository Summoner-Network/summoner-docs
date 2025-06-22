# Composability: The Real Kind

Many agent frameworks claim composability, but what they mean is the ability to plug multiple APIs into a single orchestrator. This is coordination — not true composition.

Summoner treats composability as a **graph-level property**. If two agent networks share even one node—such as a roaming agent or a public address—they can be **glued** together. The resulting graph remains valid: message routes work, agent relationships hold, and behavior continues uninterrupted.

This is not a metaphor. Like in topology, the graph can grow locally and organically. An agent might arrive on a USB stick or via QR code. As long as the identity is preserved, the graph remains intact.

Traditional systems cannot do this. Each orchestrator manages its own domain. If you try to connect two networks, you must construct a proxy or bridge manually.

In Summoner, composition is seamless. If two networks share a node, they merge. No re-registration. No synchronization step. No orchestration.

*Example:* Two distributed research labs each maintain an agent network. At a joint workshop, one roaming agent logs into both systems. Immediately, agents from both labs can collaborate—share data, launch tasks, co-author outputs—without reconfiguration or permissioning.

This model supports organic, bottom-up growth. It is not merely a technical convenience—it reflects how real distributed systems evolve.

<span style="position: relative; top: -6px; font-size: 0.9em;"><em><u>Page content covered</u></em></span>&nbsp; ![](https://progress-bar.xyz/100)

<p align="center">
  <a href="why2_self.md">&laquo; Previous: Mobility and Ownership in Distributed Systems </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="why3_mmo.md">Next: From API Gateways to Persistent Worlds &raquo;</a>
</p>