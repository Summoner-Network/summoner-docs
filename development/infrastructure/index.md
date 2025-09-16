# Development and Infrastructure

This page explains what to use depending on your goal, how the repositories fit together, and what is reserved to the internal team. It also clarifies the current licensing status.

## Who uses what

**If you want to try or build with Summoner**

* Use **examples**
  Repo: `summoner-agents`. Run ready-made agents that show `@receive` and `@send(multi=True)` patterns.
  Typical flow:

  ```bash
  git clone https://github.com/Summoner-Network/summoner-agents
  cd summoner-agents
  source build_sdk.sh setup
  source venv/bin/activate
  python agents/agent_EchoAgent_0/agent.py
  ```

* Assemble **your own SDK** from modules
  Repo: `summoner-sdk`. Edit `build.txt`, then:

  ```bash
  git clone https://github.com/Summoner-Network/summoner-sdk
  cd summoner-sdk
  source build_sdk.sh setup
  source venv/bin/activate
  ```

* Create a **new module**
  Repo: `starter-template`. Start a native package under `tooling/`, then integrate it via `summoner-sdk`.

* Optional desktop UI
  Repo: `summoner-desktop`. A visual interface for running agents and servers.

**If you want to contribute**

* Open issues in the relevant public repo. See “How to contribute” for scope and expectations.
* Publish modules from the **starter-template** and reference them in `summoner-sdk` recipes.
* For proposed changes to core behavior, open a design issue first. Direct code changes to core are internal.

> [!NOTE]
> **Environment expectations**
>
> * macOS and Linux are supported. On Windows, use WSL2 or Git Bash in VS Code.
> * Python **3.9 or newer**. Example agents are validated on **3.11**.
> * Rust toolchain installed via `rustup` to build servers.
> * The setup installs `summoner` in editable mode. Example:
>
>   ```python
>   from summoner.server import SummonerServer
>   ```

## Licensing and IP status

As of today there is **no license file** in the public repositories. Code is available for reading and evaluation but remains protected by default copyright.

> [!IMPORTANT]
> **Until a license is published**
>
> * You may clone and run locally for evaluation.
> * Do not redistribute, relicense, or integrate code into production without written permission.
> * Documentation, issue discussions, and APIs are public to enable design proposals and module development.
> * A formal license and contributor terms are planned. The docs will be updated when they are finalized.

## What is reserved to the internal team

* Direct code changes to **`summoner-core`** and official server implementations.
* Protocol decisions, security-critical components, and release management.
* Official modules published under the Summoner organization and their versioning.
* Branding assets and the desktop application release pipeline.

External developers are encouraged to extend the platform through modules, open focused issues, and propose designs with clear scope and rationale.

<p align="center">
  <a href="../index.md">&laquo; Previous: Developer & Contribution </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="github_infra.md">Next: Github Repo Organization &raquo;</a>
</p>
