# Submitting an Issue

Issues are the main way to report bugs, propose features, and ask questions. Clear reports help everyone move faster.

> [!IMPORTANT]
> **Scope**
>
> * Direct code changes to `summoner-core` and official servers are handled by the internal team.
> * Use issues to propose behavior changes. If the idea belongs outside core, consider publishing it as a module and link to it.

## Where to file

| Topic                                          | Repository            |
| ---------------------------------------------- | --------------------- |
| Core runtime, Python client SDK, Rust server   | `summoner-core`       |
| Example agents and patterns                    | `summoner-agents`     |
| Documentation corrections or gaps              | `summoner-docs`       |
| SDK assembly, build recipes                    | `summoner-sdk`        |
| Desktop application                            | `summoner-desktop`    |
| Official agent classes and releases            | `summoner-agentclass` |
| New module starting point or template feedback | `starter-template`    |

> [!NOTE]
> If you are unsure, pick the repo that best matches the code you ran. We can move the issue if needed.

## Before you open an issue

* Search existing issues to avoid duplicates.
* Update to the latest commit or tagged release in the repo you are using.
* Reproduce with a clean virtual environment when possible.

## Writing a good bug report

Include the following fields. Copy this block into your issue and fill it in.

```markdown
### Summary
Short description of the problem.

### Steps to Reproduce
1. …
2. …
3. …

### Expected vs Actual
- Expected: …
- Actual: …

### Minimal Example
<code or command snippet showing the smallest failing case>

### Environment
- OS: macOS 14.5 / Ubuntu 22.04
- Python: 3.11.8  (core requires 3.9+; examples validated on 3.11)
- Rust: rustc 1.xx.x (if relevant)
- Repo and commit/tag: <repo name> @ <hash or tag>
- How installed: setup script, venv active, extra deps if any

### Logs / Traceback
<copy relevant lines only; redact secrets>

### Additional Notes
Networking, firewall, or filesystem constraints if relevant.
```

Tips

* Prefer a minimal script over a large project.
* Paste only the log lines that show the failure.
* Do not include secrets in logs or screenshots.

## Feature requests and design proposals

A good proposal explains the problem, shows a small example, and describes the smallest change that solves it.

```markdown
### Problem
What cannot be done today.

### Proposed Direction
Smallest surface that solves it. API shape or CLI flag if applicable.

### Example
A short code or command snippet.

### Alternatives
Other options you considered and why they fall short.

### Impact
Which repos are affected and any compatibility notes.
```

If your idea is best delivered as an extension, create it with **starter-template** and link the repo in the issue. This helps us evaluate real usage and compatibility.

## Security and sensitive reports

> [!IMPORTANT]
> Do not open a public issue for vulnerabilities or secrets exposure.
> Email **[info@summoner.org](mailto:info@summoner.org)** with steps to reproduce and an impact summary. Include version and environment details. We will coordinate a fix and disclosure.

## What happens after you file

* We triage for scope and route to the right repository.
* We may ask for more details or a smaller reproduction.
* Accepted issues are scheduled based on impact and effort. Some items may be better served as community modules and we will say so clearly.

> [!NOTE]
> Labels and milestones are being standardized. You may see working labels such as `bug`, `enhancement`, `question`, `needs-info`, and `area:core/sdk/agents/desktop`. Names may change as the process matures.

<p align="center">
  <a href="index.md">&laquo; Previous: How to Contribute </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="server_code.md">Next: Contributing to the Server Code Base &raquo;</a>
</p>
