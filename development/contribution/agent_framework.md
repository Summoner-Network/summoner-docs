# Creating an Agent Class

You can contribute at two levels. Help improve our official `SummonerAgent` classes through issues in **summoner-agentclass**, or build your own agent module using **starter-template** and plug it into an SDK.

> [!IMPORTANT]
> **Scope and licensing**
>
> * Core server changes are internal. Extend behavior on the client side.
> * Repositories are public for evaluation. No license is published yet. Do not redistribute or use in production without written permission.
> * For the release model and where agent updates land, see **Summoner Updates and Extensions**.

## Option A — contribute to official `SummonerAgent`

Open focused issues in **summoner-agentclass**: [https://github.com/Summoner-Network/summoner-agentclass](https://github.com/Summoner-Network/summoner-agentclass).
Propose improvements, report bugs, or suggest new capabilities. Include a minimal example and expected behavior. We keep each release in a dedicated folder so you can pin to a known behavior or move to the latest.

> [!NOTE]
> If a feature fits better as an extension, prototype it as a module first. Link the repo in your issue so we can evaluate real usage.

## Option B — build your own module (How-To)

This path creates a module that provides one or more agent classes built on `SummonerClient`. You publish the module in your own repo, then include it in an SDK recipe.

**1) Create a repo from the template**

```bash
# On GitHub: click "Use this template" on
# https://github.com/Summoner-Network/starter-template
git clone https://github.com/<you>/<your-module>.git
cd <your-module>
source install.sh setup
bash install.sh test_server   # optional sanity check
```

This prepares a venv, installs `summoner` in editable mode, and verifies imports.

**2) Add your agent package under `tooling/`**

```
tooling/echo_agent/
├── __init__.py        # from .agent import EchoAgent
└── agent.py
```

Minimal sketch:

```python
# tooling/echo_agent/agent.py
from summoner.client import SummonerClient  # keep imports clean; installed by setup
# Patterns in examples use decorators like @receive and @send(multi=True)

class EchoAgent(SummonerClient):
    def __init__(self, name="EchoAgent"):
        super().__init__(name=name)

    # Example pattern: receive a message, reply with the same payload
    # The exact decorator import comes from the SDK you build.
    # Replace with the decorator your SDK exposes, for example:
    # @receive("echo")
    async def on_echo(self, ctx, msg):
        await ctx.reply(msg)

if __name__ == "__main__":
    agent = EchoAgent()
    agent.run()
```

Export the class:

```python
# tooling/echo_agent/__init__.py
from .agent import EchoAgent
```

**3) Build an SDK that includes your module**

```bash
git clone https://github.com/Summoner-Network/summoner-sdk sdk
cd sdk

cat > build.txt <<'EOF'
summoner-agentclass
<your-github-user>/<your-module>@main
EOF

source build_sdk.sh setup
source venv/bin/activate
```

Now your agent is importable alongside the core SDK:

```python
from echo_agent import EchoAgent
```

Use `source build_sdk.sh dev_setup` if you must target the core dev branch, then switch back to tags when available.

**4) Run and iterate**

* Keep dependencies minimal.
* Configure via `.env` or CLI flags. No secrets in code.
* Add a short README with a usage snippet.

**5) Publish and share**

* Tag releases and pin them in `build.txt`.
* Open an issue linking your repo if you want feedback or would like it considered for discovery in the future web app.

> [!NOTE]
> For a higher-level overview of extensions and release channels, see **Summoner Updates and Extensions**.

## Submission and review expectations

* Clear problem statement and scope.
* Small surface area with stable imports.
* Works with Python 3.9 or newer. Examples validated on 3.11.
* No hardcoded paths. Respect virtual environments.
* One tiny test script or example that is runnable end to end.

If you are unsure whether something belongs in core or as a module, open an issue first and describe the end goal. We will guide you to the right path.

<p align="center">
  <a href="server_code.md">&laquo; Previous: Contributing to the Server Code Base </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../../faq/index.md">Next: Frequently Asked Questions &raquo;</a>
</p>
