# How to Use Templates

Templates give you the right layout and the scripts you need. You should **not** create extra scripts. Use the ones that ship with the templates.

> [!NOTE]
> **Licensing for modules and SDKs**
>
> * Unless a repository states otherwise, Summoner public repositories are licensed under the **Apache License, Version 2.0**. The **controlling terms are the `LICENSE` file in each repository**.
> * Modules you publish should use **Apache-2.0** or another permissive Apache-compatible license. Include a `LICENSE` and any `NOTICE` content in your module repo.
> * When you assemble an SDK with `summoner-sdk`, the resulting build remains subject to the licenses of all included components.

## Template catalog

* **starter-template**  
  For building a native module that plugs into the SDK.
  Comes with `install.sh` to clone `summoner-core`, create a venv, reinstall the SDK and Rust server, and spin up a test server.

* **summoner-sdk**  
  For assembling a full SDK from multiple modules.
  Comes with `build_sdk.sh` which reads `build.txt`, clones each source, merges their `tooling/` packages into the SDK, rewrites imports, creates a venv, installs deps, writes `.env`, and reinstalls the core.

## No custom scripts needed

* When you start from **starter-template**, run **its** `install.sh`.
* When you assemble an SDK, run **summoner-sdk's** `build_sdk.sh`.
* Do not add a `build_sdk` function to your own `install.sh`. It duplicates what `build_sdk.sh` already does.

## Two standard workflows

### A) Build a module (starter-template)

```bash
# On GitHub: click "Use this template" on:
# https://github.com/Summoner-Network/starter-template
git clone https://github.com/<you>/<your-module>.git
cd <your-module>
source install.sh setup
# optional smoke test:
bash install.sh test_server
```

This prepares a venv, installs `summoner` in editable mode, and verifies imports. Put your package under `tooling/<your_package>/`.

### B) Assemble an SDK (summoner-sdk)

```bash
git clone https://github.com/Summoner-Network/summoner-sdk
cd summoner-sdk
```

Create a **build.txt** that lists the sources to pull:

**Include entire repo `tooling/` packages**

```
https://github.com/Summoner-Network/summoner-agentclass.git
https://github.com/<you>/<your-module>.git
```

**Include only selected packages from a repo**

```
https://github.com/<you>/<your-repo>.git:
  echo_agent
  my_transport
```

Then build and activate:

```bash
source build_sdk.sh setup      # reads build.txt
source venv/bin/activate
```

`build_sdk.sh` also supports:

```bash
source build_sdk.sh reset      # delete and rebuild
source build_sdk.sh deps       # reinstall SDK pieces
source build_sdk.sh test_server
source build_sdk.sh clean
# optional test build list if you maintain one:
source build_sdk.sh setup test_build
```

If you need the core dev branch later:

```bash
# (use the dev_* variants your repo provides, if present)
# Example:
# source build_sdk.sh dev_setup
# source build_sdk.sh dev_reset
```

## What `build.txt` enables

* **Lines ending with `.git`** clone that repo and merge **all** packages under `tooling/` into the SDK.
* **Lines ending with `.git:`** start a block where the next indented lines name specific packages under `tooling/` to include.
* During the merge, imports like `from tooling.pkg import X` are **rewritten** to `from summoner.pkg import X`, so your code works cleanly after integration.

## When to use which script

| Goal                                            | Repo                                  | Script         | Typical command                                              |
| ----------------------------------------------- | ------------------------------------- | -------------- | ------------------------------------------------------------ |
| Create and test a single module                 | `starter-template` clone of your repo | `install.sh`   | `source install.sh setup` then `bash install.sh test_server` |
| Build a full SDK that includes multiple modules | `summoner-sdk`                        | `build_sdk.sh` | `source build_sdk.sh setup`                                  |
| Rebuild from scratch                            | `summoner-sdk`                        | `build_sdk.sh` | `source build_sdk.sh reset`                                  |

## Notes

* Keep dependencies minimal and avoid secrets in code.
* Pin versions in `build.txt` once you tag releases.
* Keep the repo `LICENSE` and any `NOTICE` files with redistributions. Respect third-party licenses included in dependencies.
* Trademarks, logos, and brand names are not licensed.

<p align="center">
  <a href="github_infra.md">&laquo; Previous: GitHub Repo Organization </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="summoner_ext.md">Next: Summoner Updates and Extensions &raquo;</a>
</p>
