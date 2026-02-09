# Summoner Updates and Extensions

Summoner grows along two tracks. Official releases that advance our **SummonerAgent** classes, and community extensions that add capabilities as modules.

> [!IMPORTANT]
> **Where releases land**
>
> * Primary focus is the `summoner-agentclass` repository: [https://github.com/Summoner-Network/summoner-agentclass](https://github.com/Summoner-Network/summoner-agentclass).
> * Some releases target the Desktop app.
> * The core server and the core SDK evolve steadily in parallel. Their cadence is independent from agentclass releases.

## Official releases and version selection

Each **SummonerAgent** release is preserved as its own folder inside `summoner-agentclass`. This lets you move forward to the latest agent behavior or pin to an earlier one.

* You always have access to the latest **core server** and **core client** code.
* To return to a previous agentclass implementation, choose the matching release folder in `summoner-agentclass`.

```bash
git clone https://github.com/Summoner-Network/summoner-agentclass
cd summoner-agentclass
# Explore historical agentclass releases
ls releases/
# Use a specific release folder (example placeholder)
cd releases/<release-id>/
```

Updates will be announced on the website, on social media, and in the planned web app.

> [!NOTE]
> **Licensing**
> Unless a repository states otherwise, Summoner public repositories are licensed under the **Apache License, Version 2.0**.
> The **controlling terms are the `LICENSE` file at the root of each repository**. If a repository lacks a `LICENSE`, no license is granted and you should open an issue.
>
> **What Apache-2.0 allows**
>
> * Use, modify, and redistribute the code, including commercially.
> * Patent license from contributors.
>
> **Your obligations**
>
> * Keep the repo `LICENSE` and any `NOTICE` files with your distributions.
> * State significant changes you make.
> * Respect third-party dependency licenses.
>
> **Scope**
>
> * Trademarks, logos, and brand names are not licensed.
> * Security disclosure policies and secrets handling still apply.

## Extend Summoner with modules

Use the **extension-template** to author a module that plugs into the SDK. See the repo for full instructions: [https://github.com/Summoner-Network/extension-template](https://github.com/Summoner-Network/extension-template).

Typical flow:

```bash
# create from template on GitHub, then:
git clone https://github.com/<you>/<your-module>.git
cd <your-module>
source install.sh setup
bash install.sh test_server
```

Assemble an SDK that includes your module with **summoner-sdk**:

```bash
git clone https://github.com/Summoner-Network/summoner-sdk
cd summoner-sdk

# declare modules to include
cat > build.txt <<'EOF'
summoner-agentclass
<your-org>/<your-module>@main
EOF

# build and activate
source build_sdk.sh setup
source venv/bin/activate
```

> [!NOTE]
> **Module licensing**
> Community modules should use **Apache-2.0** or another permissive Apache-compatible license. Include a `LICENSE` and any `NOTICE` content in your module repository.

## Propose features and improvements

Submitting focused issues and participating in discussion is the most effective way to have new features integrated, either in **core** or in our official modules.

When opening an issue:

* State the problem and expected outcome.
* Include a minimal example or short design note.
* Mention the affected repo and environment.
* If your idea belongs outside core, consider publishing it as a module first and link to it.

## Community and discussion channels

* **Today**. Use GitHub issues for questions, bug reports, and proposals.
* **Planned**. A web app with forums, bug reports, and contact help.
* **Discord**. The server is being revamped and is not accessible right now. We will update these docs if it reopens.
* **Reddit**. Official subreddit: [https://www.reddit.com/r/SummonerOfficial/](https://www.reddit.com/r/SummonerOfficial/). Community-run spaces are welcome, though they are not official support channels.

<p align="center">
  <a href="template_howto.md">&laquo; Previous: How to Use Templates </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../contribution/index.md">Next: How to contribute &raquo;</a>
</p>
