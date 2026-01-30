# How to Contribute

Thank you for helping improve Summoner. Contributions from the community focus on issues, modules, examples, and documentation. Core code changes are maintained by the internal team.

> [!IMPORTANT]
> **Scope and licensing**
>
> * All public repositories in the Summoner organization are intended to be licensed under the **Apache License, Version 2.0**. The **controlling terms are the `LICENSE` file at the root of each repository**. If a repository lacks a `LICENSE`, no license is granted and you should open an issue.
> * You may use, modify, and redistribute the code, including commercially, subject to the Apache-2.0 terms.
> * Keep the repository `LICENSE` file and any `NOTICE` file with your distributions. Respect third-party dependency licenses.
> * Trademarks, logos, and brand names are not licensed.
> * Direct code changes to `summoner-core` and official server implementations are maintained by the internal team. Use issues and modules to propose changes.

## Choose your path

* **Submit an issue**
  Report a bug, propose a feature, or ask a question. Clear problem statements and minimal examples help us triage faster. See [Submitting an Issue](issues.md).

* **Propose a design**
  For changes that affect behavior or SDK components, open an issue with a short design note. State the goal, the minimal surface area of change, and the impact on agents or servers. Link any prototype code.

* **Publish a module**
  Use the **starter-template** to build a module that plugs into the SDK. This is the preferred way to extend capabilities without modifying core. Your module can be included via `summoner-sdk` recipes. Choose **Apache-2.0** or another permissive, Apache-compatible license, and include your own `LICENSE` and any `NOTICE` content. See the template repo for details.

* **Contribute runnable examples**
  Add agents that demonstrate patterns such as `@receive` and `@send(multi=True)`. Keep dependencies minimal and document setup in a short README.

* **Improve documentation**
  Suggest clarifications and small fixes through issues. Reference the page and include the change you propose.

> [!NOTE]
> **Contribution terms**
>
> * By submitting a change to a repository, you agree that your contribution is provided under **Apache-2.0**.
> * See the repo `CONTRIBUTING.md` for the required Developer Certificate of Origin sign-off or CLA, if applicable.

> [!NOTE]
> **Environment expectations**
>
> * macOS and Linux are supported. On Windows, use WSL2 or Git Bash in VS Code.
> * Python **3.9 or newer** for core. Examples are validated on **3.11**.
> * Rust toolchain via `rustup` to build and run high-performance servers.

## What we look for during review

* **Clarity**. The problem and expected outcome are well defined.
* **Security**. No secrets in code. Do not bypass cryptographic envelopes, key handling, or replay protection.
* **Compatibility**. Works with the current SDK and server. Avoid hardcoded paths. Respect virtual environments.
* **Minimalism**. Small surfaces and minimal dependencies.
* **Documentation**. A brief README, a quick start, and, when relevant, a tiny test script.

> [!NOTE]
> **Adoption paths**
> Features may land as improvements to official modules or as independent community modules. Core changes start as design issues and are evaluated for security and protocol impact.

## What is out of scope for external PRs

Protocol definitions, cryptography, core server internals, and the release process are maintained by the internal team. Use issues to discuss ideas in these areas and attach prototypes as separate modules when possible.

Proceed to the specific guides:

* [Submitting an issue](issues.md)
* [Contributing to the server code base](server_code.md)
* [Creating an agent class](agent_framework.md)

<p align="center">
  <a href="../infrastructure/summoner_ext.md">&laquo; Previous: Summoner Updates and Extensions </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="issues.md">Next: Submitting an Issue &raquo;</a>
</p>
