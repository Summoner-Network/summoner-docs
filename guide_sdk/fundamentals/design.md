# Agent Design Principles

design.md > design.md

## Format

Expectation: send / receive disconnected.
Race -> connect them

### Configuration
Best practive if unsure

### Structure
- agent.py
- requirements.txt
- folders, etc.. 
- databases

### Plan for crashs and messages not received
 - fsm logic
 - design strategies
    - start simple: travel and function
    - decompose function into task and:
        - valiation 
        - registration 
        - message processing

NOTE: Rely on the agent libraires to give easy examples and then link to the more complex ones

## Async programming

Only 1 async context should be used.
USe client.loop


## Flows

Hubs?

## Traveling
Tutorials on traveling agent and the idea that controling an agent cam be done by a "summoner"

### Giving orders (show examples)

NOTE: refer to the agent library if needed

- Chat agent giving order -> to travel to other server
- Question agent receive orders, go to server where answer agent is

## Learnings from designing agents

1) Hook are processing all messages, while send and receive would implement specialized message processing.
    - Hooks: every message
    - Send/Receive: tailored (event-related)

2) Send should can read states but should not write (change) the states. This is what happens in the negotiation, which might explain why message-droping can break the workflow. If state changes follows receive and triggers, it should be more organized. So states should be handled on receiving end.
    - receive("interested --> accept_too"): still compute history
    - add: can this solve the problem?
        - receive("accept_too --> none", priority = -1) (receipt of new offer or interest -> reset)
        - receive("none --> interested", priority = 0)

3) Best way to mix client is to use:
    - connectors
    - user server for client-client communication

4) Important in case we use initial arrows; download states input can have None keys 
    {None: [], "state:...": [] }

5) In flow, a way to forget about a graph walkthrough is to return None: then no state is proposed for the key.

6) Receive using on_triggers or on_actions is only triggered once. Safer to use handlers without any event

7) best practice: 
 - Using triggers and not action (and also using parentd) can allow us to send several times, as long as the tirgger is true
 - use download state to upstates to not have conflicting logic. Download state should handle priority

8) Priority: Priority=-1 is to ensure we dont cut abrutly and we broacast enough to finish handsahke


9) Do not update database in receive because it can create race conditions. In fact hooks should not update or initiate states. THis should be delegated to update and download states.

10) counters to switch state should preferentially be on the send driver if not dependent of receiving messages (otherwise the counter) will not trigger. Controling you own state is through send and letting other control your states is through receive.

11) on_triggers ands on_actions should really only be for broadcasting event to which agent subscrib (get from a database andsend with multi to "to" is needed other no multi with one message) --> smart contract is a lower level of it.

12) download_states absolutely makes sense when we have various compete parallel tracks competing to reach the node for certain conditions: handshake finalize if exceed 1000 and negotiation finalize is trade is successful. Also, download state is useful to sort out all the Stay and Move from the same state (forking). As we develop more than just Move and Stay (Test, ...) this will be useful.

13) This integration is fundamental to our platform because it is a POC for composing layer of logic in the SDK. This mean that we can add layers that the users will not see while the users can add their own layers, all such that our logic layers and the user's layer do not conflict.
In other words, my efforts in getting this right is showing me a "Zen of Summoner" where:

receive and send logic hide a natural initiator / responder behavior
initiators would tend to change states inside the send decorator
responders would tend to change states insider the download_states decorator
initiators have more logic in the send
responders may tend to have more receive handlers
what an initiator would tend to handle in send, the responder would tend to handle through receive

Important: does a change of state need to be triggered by a message from another party (receive needed), or is it controled by something internal (counter, etc)? (control in send -- because they ast on a clock)

Reputation is computed on this principle: 
not receive and had to cut -1
too many conflict in nonces -1

14) A single send driver per database type can prevent race (think about nonces, etc). Receive can be used on non-parallel tracks (fork-merge). Memory access in receive should make sense with the receipt of a signal / trigger

15) sends are queued and fire as soon as possible. 
Brainstorming: "This is why we need a nonce store. But we might need to control sends through queue. Or we reset the nonce in the receive to avoid trace."
This is on_triggers and on_actions exist. They prevent the execution of a send without the finishing of the related receive (think about nonces=None and then being updated).
The send run on a tick, so this is what happens when we do not have the trigger / actions:

```log
2025-09-08 08:55:21.266 - HSBuyAgent_0 - INFO - [resp_exchange_0 --> resp_interested] check local_nonce='7198471969' ?= your_nonce='7198471969'
2025-09-08 08:55:21.267 - HSBuyAgent_0 - INFO - [resp_exchange_0 --> resp_accept] check local_nonce='7198471969' ?= your_nonce='7198471969'
2025-09-08 08:55:21.267 - HSBuyAgent_0 - INFO - [resp_exchange_0 --> resp_refuse] check local_nonce='7198471969' ?= your_nonce='7198471969'
2025-09-08 08:55:21.272 - HSBuyAgent_0 - INFO - [send][responder:resp_exchange_0] respond #1 | my_nonce=7198471969
2025-09-08 08:55:21.273 - HSBuyAgent_0 - INFO - [resp_exchange_0 --> resp_interested] REQUEST RECEIVED #2
2025-09-08 08:55:21.273 - HSBuyAgent_0 - INFO - [resp_exchange_0 --> resp_accept] REQUEST RECEIVED #2
2025-09-08 08:55:21.274 - HSBuyAgent_0 - INFO - [resp_exchange_0 --> resp_refuse] REQUEST RECEIVED #2
```






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
  <a href="client_agent.md">&laquo; Previous: Clients and Agents </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../howtos/index.md">Next: "How-to" tutorials &raquo;</a>
</p>