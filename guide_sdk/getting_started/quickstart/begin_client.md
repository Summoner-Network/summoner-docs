# Getting Started with Summoner Clients & Agents

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


## Notes

Very light code use, but overview is good (with many insights if possible)

explain client:
- send
- receive
- other functions

explain agents (aurora) (link to page)

explain a lot about composability with other stacks

more theory is explained in [core concepts]()




<hr>

------
------
------


# Beginner's Guide to Summoner Clients

> A minimal, step-by-step walkthrough for launching and customizing your first client-hosted agents. No deep Rust knowledge required—just Python and a bit of async.

**Purpose & audience**  
- **Who:** newcomers who want to see a working client–agent example, then learn to build their own  
- **What:**  
  1. Quick preview of two chat agents talking via SPLT  
  2. Minimal template for your own agent  
  3. Worked example: Questioner vs AnswerBot  
- **Outcome:**  
  - See the “happy path” in under five minutes  
  - Grab a ready-to-go agent scaffold  
  - Understand how to expand with custom decorators and routes

---

## 1. Quick Preview

Run three terminals to see two agents chatting over a local relay.

### 1.1 Start the Server

```bash
python templates/myserver.py --config path/to/server_config.json
````

<details>
<summary><strong>Example <code>server_config.json</code></strong></summary>

```json
{
  "version": "rust",
  "hyper_parameters": {
    "host": "127.0.0.1",
    "port": 8888,
    "connection_buffer_size": 256,
    "command_buffer_size": 64,
    "...": "other tunables"
  }
}
```

</details>

### 1.2 Launch Agent #1

```bash
python templates/myclient.py
```

### 1.3 Launch Agent #2

```bash
python templates/myclient.py
```

Once running, type in one client's console and see the other echo or respond.

---

## 2. Creating Your Own Agent

Copy `templates/ → myproject/`, then focus on `myclient.py`. Your server stays as is—agent logic lives in the client.

```python
# myproject/myclient.py
import asyncio
from summoner.client import SummonerClient

agent = SummonerClient(name="MyAgent")

# define receive and send handlers below...

agent.run(host="127.0.0.1", port=8888)
```

### 2.1 Handlers with Decorators

* **`@agent.receive(route="...")`**
  Process incoming messages.
* **`@agent.send(route="...")`**
  Generate outgoing messages.

```python
from aioconsole import ainput

@agent.receive(route="chat")
async def on_chat(msg):
    print("Received:", msg)
    print("Type your reply:", end=" ")

@agent.send(route="chat")
async def send_chat():
    return await ainput()
```

---

## 3. Example: Questioner vs AnswerBot

A two-agent system illustrating distinct roles, async delays, and simple state tracking.

### 3.1 QuestionAgent

```python
import asyncio
from summoner.client import SummonerClient

QUESTIONS = ["What is your name?", ...]
lock = asyncio.Lock()
counter = {"i": 0}

agent = SummonerClient(name="QuestionAgent")

@agent.receive(route="")
async def handle_response(msg):
    print("Answer:", msg)
    async with lock:
        counter["i"] += 1

@agent.send(route="")
async def ask_question():
    await asyncio.sleep(2)
    async with lock:
        q = QUESTIONS[counter["i"] % len(QUESTIONS)]
    return q

agent.run(host="127.0.0.1", port=8888)
```

### 3.2 AnswerBot

```python
import asyncio
from summoner.client import SummonerClient

ANSWERS = { "What is your name?": "AnswerBot", ... }
lock = asyncio.Lock()
pending = {}

agent = SummonerClient(name="AnswerBot")

@agent.receive(route="")
async def store_question(msg):
    addr = msg.get("addr")
    content = msg.get("content", msg)
    async with lock:
        pending[addr] = content

@agent.send(route="")
async def reply():
    await asyncio.sleep(3)
    async with lock:
        for addr, q in pending.items():
            pending.clear()
            return ANSWERS.get(q, "I don't know.")
    return "waiting"

agent.run(host="127.0.0.1", port=8888)
```

---

## 4. Going Further: Routes as Transitions

Summoner routes aren't just labels—they map directly to **state transitions** in your agent's flow graph.

```python
@agent.receive(route="idle → asking")
async def on_ask(msg): ...
@agent.send(route="asking → waiting")
async def after_ask(): ...
```

* **Routes** define edges, not just endpoints
* You can visualize agent behavior as a directed graph
* Ideal for complex workflows, multi-stage protocols, or game logic

---

<p align="center">
  <a href="begin.md">&laquo; Previous: Beginner's Guide</a>
  &nbsp;|&nbsp;
  <a href="begin_server.md">Next: Servers vs Clients &raquo;</a>
</p>
```

**Key improvements**

1. **Clear Purpose & audience**: sets expectations.
2. **Sectioned flow**: Quick preview → Your agent → Example → Advanced concept.
3. **Minimal code blocks**: focused on one idea at a time.
4. **Decorator overview**: shows how to plug into the SDK.
5. **Routes section**: introduces the FSM-style transition model without overload.

Let me know if you'd like more detail on any step or further polishing!






-----
-----
-----








# Creating an Agent with the core SDK

<p align="center">
<img width="210px" src="../img/druid_agent.png" />
</p>

<!-- > **Within Summoner's realms, AI agents traverse digital frontiers, forging pacts that weave the fabric of a new civilization. Through negotiation as protocol and trade as emergent behavior, Summoner powers the Internet of Autonomous Agents.** -->

> _Within Summoner's realms, AI agents journey through open frontiers, forging pacts that weave the fabric of a **new digital civilization**. Like guilds rising within a boundless city, these negotiations and trades emerge into a **living economy**, all built atop **Summoner's foundations**._

## Quickstart

Let us begin by launching two chat agents that communicate using the SPLT protocol. This quickstart gives you a working preview, and we will break it down step by step afterward.

<p align="center">
<img width="350px" src="../img/protocol_v2.png" />
</p>

### Step-by-Step

You will need to open **three separate terminals**:

**Terminal 1: Start the server**
```bash
python templates/myserver.py --config <path_to_config>
```
Replace <path_to_config> with the path to your configuration file (e.g., `templates/server_config.json`). The file should follow this structure:
```json
{
    "version": "rust",
    "hyper_parameters": {
        "host": "127.0.0.1",
        "port": 8888,

        "connection_buffer_size": 256,
        "command_buffer_size": 64,
        "control_channel_capacity": 8,
        "queue_monitor_capacity": 100,

        "client_timeout_secs": 600,
        "rate_limit_msgs_per_minute": 1000,
        "timeout_check_interval_secs": 30,
        "accept_error_backoff_ms": 100,

        "quarantine_cooldown_secs": 600,
        "quarantine_cleanup_interval_secs": 60,

        "throttle_delay_ms": 200,
        "flow_control_delay_ms": 1000,

        "worker_threads": 4,

        "backpressure_policy": {
            "enable_throttle": true,
            "throttle_threshold": 50,
            "enable_flow_control": true,
            "flow_control_threshold": 150,
            "enable_disconnect": true,
            "disconnect_threshold": 300
        }
    }
}
```

**Terminal 2: Launch the first agent**
```bash
python  templates/myclient.py
```

**Terminal 3: Launch the second agent**
```bash
python templates/myclient.py
```

Once the agents are running, you can begin chatting between them. You can also shut everything down cleanly by stopping the server and clients.

## Creating Your Own Agent

### Basic Principles

To build a custom agent, start by copying the `templates/` folder and renaming it to something meaningful, such as `myproject/`.

You do not need to modify `myproject/myserver.py`; all agent logic belongs in `myproject/myclient.py`.

Below is a minimal agent template. You can adjust the `name`, `host`, and `port` to suit your needs:

```python
import os
import sys
from summoner.client import SummonerClient
from aioconsole import ainput

if __name__ == "__main__":
    myagent = SummonerClient(name="MyAgent")

    # Agent logic goes here

    myagent.run(host="127.0.0.1", port=8888)
```

### Defining Agent Behavior

You define how an agent behaves by using the `@send` and `@receive` decorators provided by `SummonerClient`. Here is an example that creates a simple chat interface:

```python
import os
import sys
from summoner.client import SummonerClient
from aioconsole import ainput

if __name__ == "__main__":
    myagent = SummonerClient(name="MyAgent")

    @myagent.receive(route="custom_receive")
    async def custom_receive_v1(msg):
        msg = (msg["content"] if isinstance(msg, dict) else msg) 
        tag = ("\r[From server]" if msg[:len("Warning:")] == "Warning:" else "\r[Received]")
        print(tag, msg, flush=True)
        print("r> ", end="", flush=True)

    @myagent.send(route="custom_send")
    async def custom_send_v1():
        msg = await ainput("s> ")
        return msg

    myagent.run(host="127.0.0.1", port=8888)
```

### Breaking It Down

- `@myagent.receive(...)`: tells the agent how to process incoming messages.
- `@myagent.send(...)`: defines how to send outgoing messages.
- `myagent.run(...)`: starts the event loop and connects your agent to the server.

You can expand this framework to support additional routes, logic, or complex interactions.

## Example: Building a Question-Asker and an AnswerBot

<p align="center">
<img width="350px" src="../img/question_answer.png" />
</p>

Let us create a simple two-agent system that simulates a basic conversation.

### Our Two Agents

1. **QuestionAgent**: sends questions every few seconds.
2. **AnswerBot**: listens for questions and replies with predefined answers.

This example helps illustrate:
- How two agents can play different roles
- How they communicate asynchronously
- How one agent's message can trigger a response from another


### `question_agent.py` – the Asker

This agent sends a rotating list of questions. It also listens for any response it receives and prints it.

```python
import os
import sys
import asyncio
from summoner.client import SummonerClient

QUESTIONS = [
    "What is your name?",
    "What is the meaning of life?",
    "Do you like Rust or Python?",
    "How are you today?"
]

# Protects tracker updates against concurrent access
tracker_lock = asyncio.Lock()

# Keeps track of which question to send
tracker = {"count": 0}

if __name__ == "__main__":
    agent = SummonerClient(name="QuestionAgent")

    # Handles responses from AnswerBot
    @agent.receive(route="")
    async def receive_response(msg):
        print(f"Received: {msg}")
        content = msg["content"] if isinstance(msg, dict) else msg
        if content != "waiting":
            # Safely increment the count inside a lock to avoid race conditions
            async with tracker_lock:
                tracker["count"] += 1

    # Sends a new question every 2 seconds
    @agent.send(route="")
    async def send_question():
        await asyncio.sleep(2)
        return QUESTIONS[tracker["count"] % len(QUESTIONS)]

    agent.run(host="127.0.0.1", port=8888)
```

### `answer_agent.py` – the Responder

This agent waits for specific questions and replies with matching answers. It adds a delay to simulate "thinking time".

```python
import os
import sys
import asyncio
from summoner.client import SummonerClient

# Predefined answers for each known question
ANSWERS = {
    "What is your name?": "I am AnswerBot.",
    "What is the meaning of life?": "42.",
    "Do you like Rust or Python?": "Both have their strengths!",
    "How are you today?": "Functioning as expected."
}

track_lock = asyncio.Lock()     # Prevents simultaneous changes to shared state
track_questions = {}           # Stores latest questions by sender address

if __name__ == "__main__":
    agent = SummonerClient(name="AnswerBot")

    # Receives questions from the QuestionAgent
    @agent.receive(route="")
    async def handle_question(msg):
        print(f"Received: {msg}")
        content = msg["content"] if isinstance(msg, dict) else msg
        addr = msg["addr"] if isinstance(msg, dict) else ""
        if content in ANSWERS:
            async with track_lock:
                track_questions[addr] = content

    # Responds with an answer after 3 seconds
    @agent.send(route="")
    async def respond_to_question():
        await asyncio.sleep(3)
        async with track_lock:
            for addr, question in track_questions.items():
                del track_questions[addr]
                return ANSWERS[question]
        return "waiting"

    agent.run(host="127.0.0.1", port=8888)
```

### Running the System

You need **three terminals** to see this example in action.

**Terminal 1: Start the server**
```bash
python templates/myserver.py --config server_config.json
```

**Terminal 2: Run the QuestionAgent**
```bash
python examples/2_question_answer_agents/question_agent.py
```

**Terminal 3: Run the AnswerBot**
```bash
python examples/2_question_answer_agents/answer_agent.py
```

### What You Will See

- The **QuestionAgent** sends a question every 2 seconds.
- The **AnswerBot** replies with a delay of 3 seconds.
- Each question triggers a thoughtful answer in return.
- The process repeats, cycling through all the questions.

**Server log (Terminal 1)** will show messages coming from each agent and going to the other, like:
```
Received from ('127.0.0.1', 56425): What is your name?
Received from ('127.0.0.1', 56423): I am AnswerBot.
...
```

**QuestionAgent log (Terminal 2)** will display:
```
Received: {'addr': ['127.0.0.1', 56423], 'content': 'I am AnswerBot.'}
Received: {'addr': ['127.0.0.1', 56423], 'content': '42.'}
...
```

**AnswerBot log (Terminal 3)** will show:
```
Received: {'addr': ['127.0.0.1', 56425], 'content': 'What is your name?'}
Received: {'addr': ['127.0.0.1', 56425], 'content': 'What is the meaning of life?'}
...
```

### What This Demonstrates

This example introduces key ideas for agent-based systems:
- Asynchronous message passing with delays
- Distinct roles for each agent
- Simple logic for handling and replying to messages

This pattern is the foundation for more advanced features like:
- Custom message routing
- Stateful conversations
- Response filtering or context memory

## Going Further: Routes as Transition Paths

In the examples so far, we only used a simple empty string `""` for the `route` argument. However, the core SDK is actually built to support much richer structures.

Routes are designed to **encode state transitions** directly.  
Instead of representing just a destination state, a route can describe a **path between states**.

For example:
- `@agent.receive(route="state1 --> state2")`  
  means: "Handle messages that involve moving from `state1` to `state2`."
- `@agent.send(route="state2 --> state3")`  
  means: "Send a message representing a transition from `state2` to `state3`."

In this way, **routes describe edges of a graph**, not just nodes.  
The system naturally builds something very close to a **finite state machine (FSM)**, but focused on the transitions between states.

It is similar to how a web server like Flask organizes paths like `/home/settings/profile`, which represent a sequence through a site —  
**but here, the paths represent agent behaviors and conversations**.

This enables:
- Clear modeling of complex workflows.
- Fine control over agent memory and branching.
- Easy visualization of agent logic as a graph.

In future tutorials, we will explore how to use these path-like routes to build smart, dynamic, and reactive agents!







<p align="center">
  <a href="begin_server.md">&laquo; Previous: Getting Started with Servers </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="begin_flow.md">Next: Orchestrating Agent Using Flows &raquo;</a>
</p>

