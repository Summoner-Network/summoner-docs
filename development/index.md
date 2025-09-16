# Developer & Contribution

This section is your entry point for working on Summoner. It explains how the repositories fit together, how to set up a development environment, and how contributions are handled. Internal teams maintain the core. External developers extend the platform by publishing modules that are assembled into an SDK.

This page is an overview. Detailed setup and policies live in the linked repositories.

## How contributions work

* Anyone can open issues for bugs, proposals, or questions.
* Core code ([`summoner-core`](https://github.com/Summoner-Network/summoner-core) and official servers) is maintained by the internal team.
* Extensions are community modules. Start from [`starter-template`](https://github.com/Summoner-Network/starter-template), then include your module via [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk).

> [!NOTE]
> **Licensing**
> Public repos are visible for evaluation. No license is published yet. Do not redistribute or use in production without written permission. This note will be updated when terms are finalized.

## Pick your path

* **Build and run.** Use examples, assemble an SDK from modules, or try the desktop app. See [**Development and infrastructure**](infrastructure/index.md).
* **Contribute.** File an issue, publish a module, or add runnable examples. See [**How to contribute**](contribution/index.md).

---

* [**Development and infrastructure**](infrastructure/index.md)

  * [GitHub repo organization](infrastructure/github_infra.md)
  * [How to use templates](infrastructure/template_howto.md)
  * [Summoner updates and extensions](infrastructure/summoner_ext.md)

* [**How to contribute**](contribution/index.md)

  * [Submitting an issue](contribution/issues.md)
  * [Contributing to the server code base](contribution/server_code.md)
  * [Creating an agent class](contribution/agent_framework.md)

---

## Releases in brief

Official updates focus on [`summoner-agentclass`](https://github.com/Summoner-Network/summoner-agentclass) and sometimes the [desktop app](https://github.com/Summoner-Network/summoner-desktop). The core server and core SDK evolve on their own cadence. Each agentclass release is kept in its own folder, so you can move forward or pin to an earlier behavior. See [**Summoner updates and extensions**](infrastructure/summoner_ext.md) for version selection and feature proposals.

## Working expectations

Provide a minimal, self-contained reproduction (small steps or a short script) that reliably triggers a bug. For changes that affect behavior, open a design issue first and link any prototype or module. Avoid secrets in code or logs and respect virtual environments.

<p align="center">
  <a href="../reference/lib_proto/smart_tools.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.smart_tools</b></code></a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="infrastructure/index.md">Next: Development and Infrastructure &raquo;</a>
</p>
