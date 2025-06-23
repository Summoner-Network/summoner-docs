## True Composability: Building Graphs, Not Pipelines

<span style="position: relative; top: -6px; font-size: 0.9em;"><em><u>Covers</u></em></span>&nbsp; ![](https://progress-bar.xyz/100)


Many frameworks claim **composability**. But what they usually mean is the ability to plug multiple APIs into one orchestrator. That is what one should call coordination: everything still flows through a central hub.

Traditional systems cannot do this. Each orchestrator controls its own domain, defining which agents exist, how they communicate, and under what permissions. To connect two such systems, you must build explicit bridges, align schemas, and manage identities manually.

This process is brittle, slow to evolve, and often requires centralized approval or configuration changes. It reflects coordination, not true structural integration.

<p align="center">
<img width="300px" src="../../assets/img/orch_no_comp_rounded.png" />
</p>

<!-- <div style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">

  <div style="flex: 1;">
    <p>
    Many frameworks claim <strong>composability</strong>. But what they usually mean is the ability to plug multiple APIs into one orchestrator. That is what one should call coordination: everything still flows through a central hub.
    </p>
    <p>
    Traditional systems cannot do this. Each orchestrator controls its own domain, defining which agents exist, how they communicate, and under what permissions. To connect two such systems, you must build explicit bridges, align schemas, and manage identities manually. <br>
    This process is brittle, slow to evolve, and often requires centralized approval or configuration changes. It reflects coordination, not true structural integration.
    </p>

  </div>

  <div style="flex: 0 0 auto; text-align: center;">
    <img src="../../assets/img/orch_no_comp_rounded.png" alt="Orchestration diagram" width="300px" />
  </div>

</div>
<span style="display: block; height: 0.5em;"></span> -->

**Summoner** takes a different approach. Here, composability is a <strong>graph-level behavior</strong>. Each agent is made of smaller parts — internal states or subagents — connected like nodes in a graph. And graphs can merge.

If two agents (or entire networks) share a common node — represented by the same _route_ endpoint — the graphs **glue together** along that node. Messages keep flowing. Interactions continue without interruption. There's no orchestrator coordinating it, just a shared structure that now extends across both systems.

**Example**  
> Two research labs each run their own agent networks. At a joint workshop, they realize one of their agents overlaps — a shared node that handles data classification. Instead of linking through an API, they simply connect the graphs at that node. Instantly, all other agents can interact, share tools, and co-author outputs — no reconfig, no manual bridge.

<p align="center">
<img width="220px" src="../../assets/img/agent_comp2_rounded.png" />
</p>

Summoner's model of composition is not merely a technical mechanism. It reflects a broader vision of agents as **self-contained entities**</strong>** with their own structure and behavior. This allows networks to grow _organically_. 

When collaboration arises, there is no need for permission or rewiring — the graphs simply extend. This bottom-up, permissionless model mirrors how real systems collaborate in practice: through shared structure and mutual context.

<!-- 
<div style="display: flex; align-items: center; gap: 20px;">

  <div style="flex: 0 0 auto; text-align: center;">
    <img src="../../assets/img/agent_comp2_rounded.png" alt="Composition diagram" width="220px" />
  </div>

  <div style="flex: 1; text-align: left;">
    <p>
    Summoner's model of composition is not merely a technical mechanism. It reflects a broader vision of agents as <strong>self-contained entities</strong> with their own structure and behavior. This allows networks to grow <em>organically</em>. 
    </p>
    <p>
    When collaboration arises, there is no need for permission or rewiring — the graphs simply extend. This bottom-up, permissionless model mirrors how real systems collaborate in practice: through shared structure and mutual context.
    </p>
  </div>

</div>
<span style="display: block; height: 0.5em;"></span> -->



<p align="center">
  <a href="why2_self.md">&laquo; Previous: Mobility and Ownership in Distributed Systems</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="why4_mmo.md">Next: From API Gateways to Persistent Worlds &raquo;</a>
</p>
