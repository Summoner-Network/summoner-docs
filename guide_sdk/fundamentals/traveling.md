# Traveling Between Servers



NOTE: refer to the agent library if needed

- Chat agent giving order -> to travel to other server
- Question agent receive orders, go to server where answer agent is


Tutorials on traveling agent and the idea that controling an agent cam be done by a "summoner"

-------


# Traveling Between Servers

> Learn how to move agents seamlessly across different relay servers, enabling dynamic workflows and load distribution.

**Purpose & audience**  
- **Who:** developers building multi-relay or geo-distributed agent networks  
- **What:** overview of the travel API, code examples for instructing an agent to migrate, and best practices for state handoff  
- **Outcome:** you'll be able to send "move" commands to your agents and have them reconnect to a new server automatically

---

## 1. Why Agent Mobility?

- **Scalability:** distribute agents across multiple servers to balance load  
- **Proximity:** move agents closer to data or other collaborators  
- **Isolation:** spin up dedicated environments per task, then retire them  

> **Sample copy:**  
> "Instead of rebooting your entire network, tell individual agents to relocate. Summoner handles the disconnect, state serialization, and reconnect for you."




<p align="center">
  <a href="client_agent.md">&laquo; Previous: Clients and Agents </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="flow.md">Next: Agent behaviour as Flows &raquo;</a>
</p>