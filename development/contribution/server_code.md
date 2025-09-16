# Contributing to the Rust Server Codebase

The Rust server powers high-performance messaging and orchestration. Its design, security boundaries, and release process are maintained by the internal team.

> [!IMPORTANT]
> **Scope**
>
> * Direct changes to the Rust server are **internal-only**.
> * There is **no server plugin or extension API** at this time.
> * Community input is welcome through **issues** and focused **design discussions**.

## What you can do today

* **Report bugs** with a minimal reproduction and logs.
* **Propose behavior changes** via a short design note in an issue.
* **Discuss performance findings** with reproducible benchmarks.
* **Contribute examples and modules** on the client side. See [Creating an Agent Class](agent_framework.md).

> [!NOTE]
> If your idea adds functionality rather than changing core protocol or I/O, deliver it as a client-side module or example. This keeps the server surface small and easier to secure.

## Reporting a server bug

Provide enough detail to reproduce the issue. Use this checklist:

```markdown
### Summary
Short description of the failure.

### Steps to Reproduce
1) ...
2) ...
3) ...

### Expected vs Actual
Expected: ...
Actual: ...

### Environment
- OS and kernel
- rustc and cargo versions (from `rustup`)
- Server commit or tag
- Config used (attach sanitized json/toml)
- Client SDK and Python versions
- Network conditions (localhost, WAN, container)

### Logs
Relevant lines only. Redact secrets.

### Notes
Throughput, connection count, or timing details if performance related.
```

> [!NOTE]
> Reproduce with a clean toolchain from `rustup`, a fresh build, and default configuration where possible. If the bug depends on specific `.env` or firewall settings, describe those explicitly.

## Proposing a behavior change

Server changes can affect protocol compatibility, replay protection, or security posture. Keep proposals narrow.

```markdown
### Problem
What cannot be achieved with the current server.

### Proposed Direction
Smallest change that solves it. Mention config flags or defaults.

### Compatibility
On-the-wire impact and migration notes.

### Alternatives
Other approaches you considered.

### Measurement
How we can verify correctness or performance.
```

If you can prototype the idea on the client side first, link the repo. Real usage helps us evaluate the need and risk.

## Out of scope for external PRs

* Protocol definitions and envelope formats
* Cryptography, key handling, and replay protection
* Core networking, concurrency model, and shutdown semantics
* Release tooling and deployment pipeline

Use issues to discuss these areas. Attach measurements or traces where relevant.

## Security reports

> [!IMPORTANT]
> Do **not** file public issues for vulnerabilities or credential exposure.
> Email **[info@summoner.org](mailto:info@summoner.org)** with steps to reproduce, affected versions, and impact. We will coordinate a fix and disclosure.

## Internal process (for awareness)

* Changes include tests, benchmarks when relevant, and upgrade notes.
* Performance regressions are treated as bugs.
* The server aims for parity with the Python reference behavior while prioritizing safety and observability.

If you are unsure whether something belongs in the server or as a client-side extension, open an issue and describe the end goal. We will guide you toward the right path.

<p align="center">
  <a href="issues.md">&laquo; Previous: Submitting an Issue </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="agent_framework.md">Next: Creating an Agent Class &raquo;</a>
</p>
