# How to Use Templates

Templates let you start fast with the right folder layout, scripts, and integration points. They also make it easy to assemble your own SDK from modules.

> [!IMPORTANT]
> **Licensing status**
> Public repos are visible for evaluation. There is no published license yet. Do not redistribute or use in production without written permission. This page will be updated when the license is finalized.

## Template catalog and known derivatives

**Templates**

* **starter-template**
  GitHub Template for building a native module that plugs into the Summoner SDK.
  Includes `install.sh` to bootstrap a venv, pull `summoner-core`, validate imports, and run a test server.

* **summoner-sdk**
  Recipe-driven SDK assembler. Reads `build.txt` and installs the listed modules, then prepares a venv.
  Supports `setup`, `reset`, and `dev_setup` for using the `summoner-core` dev branch.

> [!NOTE]
> **Derived repositories**
> This registry lists projects created from the templates. Add yours via a doc PR once published.
>
> | Template         | Derived repo | Notes                                                    |
> | ---------------- | ------------ | -------------------------------------------------------- |
> | starter-template | *TBD*        | Link to your repo and a one-line description.            |
> | summoner-sdk     | *TBD*        | Link to your SDK recipe repo if you track it separately. |

## From “Use this template” to your own SDK

**What happens when you click “Use this template”**

* GitHub creates a new repository under your account with the template’s files.
* You control visibility, branches, and protections.
* Shell scripts are ready to set up a local environment.

> [!NOTE]
> **Starter flow**
>
> ```bash
> # create your repo from the template on GitHub first
> git clone https://github.com/<you>/<your-repo>.git
> cd <your-repo>
> source install.sh setup
> # optional: validate with a throwaway server
> bash install.sh test_server
> ```

**Adapting the template to compile your own SDK**

You can wire your module repo to a full SDK build using `summoner-sdk`. The pattern below adds a `build_sdk` helper inside your template’s `install.sh`.

```bash
# inside install.sh (add near other commands)
build_sdk() {
  set -e
  local SDK_DIR="${SDK_DIR:-sdk}"
  if [ ! -d "$SDK_DIR" ]; then
    git clone https://github.com/Summoner-Network/summoner-sdk "$SDK_DIR"
  fi

  # Declare which modules your SDK should include
  cat > "$SDK_DIR/build.txt" <<'EOF'
summoner-agentclass
<your-github-user>/<your-module-repo>@main
# Pin by tag when you cut releases, for example:
# <your-github-user>/<your-module-repo>@v0.2.1
EOF

  # Build the SDK and activate its venv
  (
    cd "$SDK_DIR"
    source build_sdk.sh setup
  )
  # Activate environment for convenience
  # shellcheck disable=SC1091
  source "$SDK_DIR/venv/bin/activate"
  echo "[ok] SDK built. venv activated."
}
```

Run it from your project root:

```bash
bash install.sh build_sdk
```

This produces a working SDK venv that includes your module and any listed dependencies, with clean imports:

```python
from summoner.server import SummonerServer
# your module will be importable per its package name
```

**Using the core’s dev branch when needed**

If your module depends on unreleased changes in `summoner-core`, use the supported switch:

```bash
# inside the SDK directory
source build_sdk.sh dev_setup
# or reset and re-run dev setup
source build_sdk.sh dev_reset
```

**Recommended structure for your module**

Keep your Python package under `tooling/` in the template repo. Re-export public symbols in `tooling/<your_package>/__init__.py`. During SDK assembly the module will be installed like any other package, so client code will import it by package name.

> [!IMPORTANT]
> **Publishing your derivative**
>
> * Add a short README with usage and a minimal example.
> * Pin module versions in `build.txt` once you tag releases.
> * Open a doc PR here to list your repo in the table above.

<p align="center">
  <a href="github_infra.md">&laquo; Previous: Github Repo Organization </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="summoner_ext.md">Next: Summoner Updates and Extensions &raquo;</a>
</p>
