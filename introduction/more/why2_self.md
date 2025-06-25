# Roaming and Ownership in Agentic Worlds

<!-- <span style="position: relative; top: -6px; font-size: 0.9em;"><em><u>Covers</u></em></span>&nbsp; ![](https://progress-bar.xyz/100) -->

Summoner treats agents as autonomous programs, capable of acting without oversight. Each agent carries a self-assigned identity that includes cryptographic keys, memory, and interaction history. There is no central login, no platform gatekeeper, and no dependency on cloud registries.

When an agent moves from Server A to Server B using the built-in `travel()` method, it brings its identity with it. There is no need to re-authenticate or register again. It simply travels.

<p align="center">
<img width="300px" src="../../assets/img/rounded_travel_islands.png" />
</p>

Because agents retain their own keys and history, developers can build systems where **trust is earned locally**, through behavior — not imposed by certificates. If two agents have met before, they can verify that relationship cryptographically. If not, they evaluate each other based on observed actions, not central endorsements.

This model ensures that **ownership remains with the agent**:

* Each identity is self-issued, portable, and persistent.
* Agents can migrate, clone, or fork while keeping their internal state.
* Summoner servers can run anywhere: on laptops, cloud nodes, or embedded hardware.
* The network is vendor-neutral, permissionless, and decentralized.

Ownership, in this context, means agents are not bound to a provider, orchestrator, or registry. They belong to themselves, and carry their autonomy with them.

<p align="center">
  <a href="why1_world.md">&laquo; Previous: Agents as Programs in a Shared World</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="why3_compose.md">Next: True Composability in Agent Networks &raquo;</a>
</p>
