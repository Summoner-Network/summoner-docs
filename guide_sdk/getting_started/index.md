# Getting Started

A rapid introduction to installing the Summoner SDK and running your first agent and server. Follow these steps to set up your environment and explore the essentials in minutes.

**Purpose & audience**  
- **Who:** new Summoner SDK users  
- **What:** step-by-step setup and first-run walkthrough  
- **Outcome:** have a working client, agent, and server in minutes

---

## Prerequisites

- **Python** 3.10 or later  
- **Git** installed and on your PATH  
- Familiarity with the command line  
- *(Optional)* virtual environment tool (venv, conda)

---

## Contents

1. [Installation](installation.md)  
   _How to obtain and verify the SDK package_  
2. [Quickstart](quickstart/index.md)  
   _Run a minimal example end-to-end_  
   1. [Prerequisites](quickstart/prerequesites.md)  
   2. [Basics](quickstart/basics.md)  
      - [Client](quickstart/basics_client.md)  
      - [Server](quickstart/basics_server.md)  
   3. [Beginner guide](quickstart/beginner.md)  
      - [Clients versus agents](quickstart/begin_client.md)  
      - [Servers versus clients](quickstart/begin_server.md)  
      - [Agent behaviour as flows](quickstart/begin_flow.md)  
      - [Async programming and event loops](quickstart/begin_async.md)

---

## 1. Installation

**What you’ll learn**  
- Setting up a Python virtual environment  
- Installing Summoner via pip  
- Verifying the installation  

**Outline**  
1. Create a venv (`python -m venv .venv`)  
2. Activate it (`source .venv/bin/activate` on Linux/macOS)  
3. Install the package (`pip install summoner-sdk`)  
4. Run `summoner --version` to confirm  

> **Sample copy:**  
> “To install the Summoner SDK, first create and activate a virtual environment. Then run `pip install summoner-sdk`. Finally, execute `summoner --version` to verify you have the latest release.”

---

## 2. Quickstart

A bare-bones example that brings up an agent and a server, showing core flow.

### 2.1 Prerequisites

- Confirm Python 3.10+ (`python --version`)  
- Ensure Git is available (`git --version`)  
- *(Optional)* Clone the examples repo:  
```bash
  git clone https://github.com/Summoner-Network/examples.git
```

> **Sample copy:**
> “Before proceeding, make sure your environment meets the requirements above. If you’d like to follow along with our example code, clone the official examples repository.”

### 2.2 Basics

#### 2.2.1 Client

* Define your first `Agent` subclass
* Implement an `on_message` handler
* Run the client with `run_client(...)`

> **Code snippet:**
>
> ```python
> # agent.py
> from summoner import Agent, run_client
>
> class HelloAgent(Agent):
>     async def on_message(self, msg):
>         print("Received:", msg)
>         await self.send("ack")
>
> if __name__ == "__main__":
>     run_client(HelloAgent)
> ```

#### 2.2.2 Server

* Start the relay server (`summoner-server start`)
* Configure host/port via flags or config file
* Observe agent connections in logs

> **Sample copy:**
> “The server routes messages between agents. Launch it with `summoner-server start --host 0.0.0.0 --port 8000`, then watch for connection messages in the console.”

### 2.3 Beginner guide

Deepen your understanding of core concepts through explanations and diagrams.

* **Clients vs agents**: roles and lifecycle
* **Servers vs clients**: routing vs execution
* **Flows**: modeling agent logic as stateful sequences
* **Async & event loops**: integrating with asyncio

> **Sample copy:**
> “In Summoner, a client process hosts your agent code, while the server handles message routing and persistence. Below is a sequence diagram illustrating a simple request–response flow.”

---

<p align="center">
  <a href="../index.md">&laquo; Previous: Summoner SDK Guides</a>
  &nbsp;|&nbsp;
  <a href="installation.md">Next: Installation &raquo;</a>
</p>
```

### How to use this template

1. **Drop in your front-matter** (for sidebar navigation).
2. **Adjust the sample copy** to your tone and style.
3. **Fill out each linked page** using the section outlines as your guide.
4. Iterate in small steps: once you’ve drafted **Installation**, come back here for feedback before moving on.

Let me know if you’d like more detail or another page next!



-----


- [Installation](guide_sdk/getting_started/installation.md)
- [Quickstart](guide_sdk/getting_started/quickstart/index.md)
    - [Prerequisites](guide_sdk/getting_started/quickstart/prerequesites.md)
    - [Basics](guide_sdk/getting_started/quickstart/basics.md)
        - [Client](guide_sdk/getting_started/quickstart/basics_client.md)
        - [Server](guide_sdk/getting_started/quickstart/basics_server.md)
    - [Beginner guide](guide_sdk/getting_started/quickstart/beginner.md)
        - [Clients versus agents](guide_sdk/getting_started/quickstart/begin_client.md)
        - [Servers versus clients](guide_sdk/getting_started/quickstart/begin_server.md)
        - [Agent behaviour as flows](guide_sdk/getting_started/quickstart/begin_flow.md)
        - [Async programming and event loops](guide_sdk/getting_started/quickstart/begin_async.md)

<p align="center">
  <a href="../index.md">&laquo; Previous: Summoner SDK Guides</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="installation.md">Next: Getting Started &raquo;</a>
</p>