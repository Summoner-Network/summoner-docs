# Quickstart

This Quickstart introduces the core concepts required to work with the Summoner platform. You will begin with the communication infrastructure — TCP servers and clients — and progressively build toward agent orchestration using flows and asynchronous execution.

<p align="center">
  <img width="240px" src="../../../assets/img/quickstart_rounded.png" alt="Quickstart overview" />
</p>

### 1. **Core Communication Concepts**  
   You will start with an overview of protocols and how TCP structures communication in Summoner:  
   * [Basics](basics.md) —  *situates Summoner's protocol layer on top of TCP*

   You will then explore how Summoner builds on TCP through conceptual illustrations:  
   * [Server](basics_server.md) — *explores how a TCP server handles connections and routes communication*
   * [Client](basics_client.md) — *explores how a TCP client fits into Summoner's architecture*


### 2. **Summoner Network Architecture**

Next, we examine how the components interact within the broader system and how communication is mediated:

* [Getting Started With Servers](begin_server.md) — *shows how servers relay messages to coordinate communication between clients*
* [Getting Started With Clients & Agents](begin_client.md) — *explores how a TCP client fits into Summoner's architecture*


### 3. **Agent Behavior and Execution Model**  
   We then introduce agent orchestration concepts and execution models:  
   * [Agent Behavior as Flows](begin_flow.md) — *introduces flows as finite-state models of agent behavior*
   * [Async Programming and Event Loops](begin_async.md) — *explains how asynchronous execution keeps agents and servers responsive*

By completing this section, you will understand how to build and coordinate agents using the Summoner SDK — starting from raw network connections up to autonomous, flow-driven logic.

<p align="center">
  <a href="../installation.md">&laquo; Previous: Installation of the Summoner SDK</a>  
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;  
  <a href="basics.md">Next: Basics (Intro) &raquo;</a>
</p>
