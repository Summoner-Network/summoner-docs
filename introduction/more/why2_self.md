# Roaming and Ownership

Agents in Summoner are autonomous. They carry self-assigned identities that include cryptographic keys, memory, and reputation. No third-party authority, cloud registry, or platform login is required. When an agent moves from Server A to Server B, it does not need to re-authenticate. It simply travels.

This is enabled by the built-in `travel()` method. Because agents retain their public keys and history, developers can design systems where **trust is earned locally**, not certified externally. In most frameworks, a cloud authority manages access control. In Summoner, the network itself becomes the medium for interaction and trust.

There is no orchestrator, no central host, and no need to request session tokens. Trust emerges through interaction history, not from external endorsement.

This also ensures that **ownership remains with the agent**. Each identity is self-issued. When agents meet, trust is built through behavior and memory, not by checking a registry.

This implies that **ownership is local and persistent**:

* Summoner servers can run anywhere—on personal machines, cloud services, or embedded devices.
* Agents can migrate, clone, or fork while retaining their state.
* The network is permissionless, vendor-neutral, and decentralized.

Trust boundaries are defined by agent behavior, not origin. Identity is portable, persistent, and under the agent's own control.

<span style="position: relative; top: -6px; font-size: 0.9em;"><em><u>Page content covered</u></em></span>&nbsp; ![](https://progress-bar.xyz/100)


<p align="center">
  <a href="why1_world.md">&laquo; Previous: Agents as Programs in a World, Not Just Tools on a Menu</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="why3_compose.md">Next: Composability: The Real Kind &raquo;</a>
</p>