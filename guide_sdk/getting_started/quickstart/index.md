# Quickstart

This Quickstart introduces the core concepts required to work with the Summoner platform. You will begin with the communication infrastructure — TCP servers and clients — and progressively build toward agent orchestration using flows and asynchronous execution.

<p align="center">
  <img width="240px" src="../../../assets/img/quickstart_rounded.png" alt="Quickstart overview" />
</p>

### 1. **Core Communication Concepts**  
   You will start with an overview of protocols and how TCP structures communication in Summoner:  
   * [Basics](basics.md) —  *introduces protocols, their historical context, and the role of TCP in structured messaging*

   You will then explore how Summoner builds on TCP through conceptual illustrations:  
   * [Client](basics_client.md) — *describes how a TCP client fits into the Summoner architecture*
   * [Server](basics_server.md) — *explains how the server handles connections and routes communication*

### 2. **Summoner Network Architecture**

Next, we examine how the components interact within the broader system and how communication is mediated:

* [Servers vs Clients](begin_server.md) — *shows how servers relay messages to enable coordinated, asynchronous communication*
* [Clients vs Agents](begin_client.md) — *shows how agents handle identity and behavior; and clients manage transport and message flow*


### 3. **Agent Behavior and Execution Model**  
   We then introduce agent orchestration concepts and execution models:  
   * [Agent Behavior as Flows](begin_flow.md) — *shows how finite-state automata (flows) can be used to model agent behavior and transitions*
   * [Async Programming and Event Loops](begin_async.md) — *shows how responsiveness is maintained through asynchronous execution*

By completing this section, you will understand how to build and coordinate agents using the Summoner SDK — starting from raw network connections up to autonomous, flow-driven logic.

<p align="center">
  <a href="../installation.md">&laquo; Previous: Installation of the Summoner SDK</a>  
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;  
  <a href="basics.md">Next: Basics (Intro) &raquo;</a>
</p>
