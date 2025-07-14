# Quickstart

This Quickstart introduces the core concepts required to work with the Summoner platform. You will begin with the communication infrastructure — TCP servers and clients — and progressively build toward agent orchestration using flows and asynchronous execution.

<p align="center">
  <img width="240px" src="../../../assets/img/quickstart_rounded.png" alt="Quickstart overview" />
</p>

1. **Core Communication Concepts**  
   You will start with an overview of protocols and how TCP structures communication in Summoner:  
   * [Basics](basics.md) introduces protocols, their historical context, and the role of TCP in structured messaging  

   You will then explore how Summoner builds on TCP through conceptual illustrations:  
   * [Client](basics_client.md) — where we describe how a TCP client fits into the Summoner architecture  
   * [Server](basics_server.md) — where we explain how the server handles connections and routes communication  

2. **Summoner Network Architecture**  
   Next, we examine how the components interact within the broader system and how communication is mediated:  
   * [Servers vs Clients](begin_server.md) — the server accepts connections and relays messages between clients, enabling coordinated, asynchronous communication  
   * [Clients vs Agents](begin_client.md) — agents define logic and behavior layered on top of TCP clients. The client handles message transport; the agent handles internal state and decisions  

3. **Agent Behavior and Execution Model**  
   We then introduce agent orchestration concepts and execution models:  
   * [Agent Behavior as Flows](begin_flow.md) — use finite-state automata (flows) to model agent behavior and transitions  
   * [Async Programming and Event Loops](begin_async.md) — use asynchronous programming to maintain non-blocking execution across agents and servers  

By completing this section, you will understand how to build and coordinate agents using the Summoner SDK — starting from raw network connections up to autonomous, flow-driven logic.

<p align="center">
  <a href="../installation.md">&laquo; Previous: Installation of the Summoner SDK</a>  
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;  
  <a href="basics.md">Next: Basics (Intro) &raquo;</a>
</p>
