# Github Repo Organization

This page gives a quick map of the pinned repositories in the Summoner organization and how to use each one.

<p align="center">
  <img width="500" src="../../assets/img/pinned_repos_rounded.png" alt="Pinned repositories overview"/>
</p>

> [!NOTE]
> The screenshot reflects the current set of pinned repositories as of September 16, 2025.

## Overview at a glance

| Repo                    | Purpose                                                                                | Primary tech            | Key scripts                               | Typical use                                                  |
| ----------------------- | -------------------------------------------------------------------------------------- | ----------------------- | ----------------------------------------- | ------------------------------------------------------------ |
| **summoner-core**       | Core runtime used by agents and servers. Python client SDK and Rust server.            | Python, Rust            | `setup.sh`                                | Develop against the core. Build and run servers locally.     |
| **summoner-agents**     | Runnable agents that demonstrate SDK patterns like `@receive` and `@send(multi=True)`. | Python                  | `build_sdk.sh`, `install_requirements.sh` | Try examples and learn message patterns.                     |
| **summoner-docs**       | Documentation you are reading. Concepts, design notes, and developer guides.           | Markdown, static assets | n/a                                       | Read and contribute documentation improvements.              |
| **summoner-sdk**        | Assembles an SDK from listed modules in `build.txt`.                                   | Bash, Python            | `build_sdk.sh`                            | Build your own SDK from modules. Use `setup` or `dev_setup`. |
| **summoner-desktop**    | Optional desktop UI for running agents and servers.                                    | Node, Electron          | repo-specific commands                    | Inspect and manage agents visually.                          |
| **starter-template**    | Template to author a native module that plugs into the SDK.                            | Python, Rust            | `install.sh`                              | Create and test a new module under `tooling/`.               |
| **summoner-agentclass** | Native module that adds security and orchestration features to `SummonerClient`.       | Python                  | repo-specific                             | Use DID and cryptographic envelopes in your agents.          |

## How each repo is used

**summoner-core**
Core runtime and reference servers. The setup installs `summoner` in editable mode for clean imports.

```bash
git clone https://github.com/Summoner-Network/summoner-core
cd summoner-core
source setup.sh
# Python 3.9+ and Rust toolchain required
```

> [!IMPORTANT]
> Direct code changes to `summoner-core` are reserved to the internal team. Propose behavior changes via issues first.

**summoner-agents**
Runnable examples that exercise the SDK.

```bash
git clone https://github.com/Summoner-Network/summoner-agents
cd summoner-agents
source build_sdk.sh setup
source venv/bin/activate
python agents/agent_EchoAgent_0/agent.py
```

**summoner-docs**
Houses the documentation. Improve clarity, fix typos, and add examples through issues or doc-only PRs where allowed.

**summoner-sdk**
Build an SDK from a recipe of modules listed in `build.txt`.

```bash
git clone https://github.com/Summoner-Network/summoner-sdk
cd summoner-sdk
# Standard setup
source build_sdk.sh setup
# Use the core dev branch when needed
source build_sdk.sh dev_setup
```

**summoner-desktop**
Desktop UI. Follow the repo README for Node prerequisites and run commands.

**starter-template**
Start a new module in `tooling/`, validate with the test server, then publish.

```bash
git clone https://github.com/Summoner-Network/starter-template my-module
cd my-module
source install.sh setup
bash install.sh test_server
```

**summoner-agentclass**
Provides DID support and cryptographic envelopes that integrate with `SummonerClient`. Use when you need secure messaging and orchestration features in your agents.

> [!NOTE]
> Licensing is being finalized. Repositories are public for visibility and evaluation. Until a license is published, do not redistribute or integrate code into production without written permission.

<p align="center">
  <a href="index.md">&laquo; Previous: Development and Infrastructure </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="template_howto.md">Next: How to Use Templates &raquo;</a>
</p>
