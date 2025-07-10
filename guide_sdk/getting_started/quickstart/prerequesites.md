# Prerequesites


## Requirements
Pip requirements and libraries:

What will be intalled, what is in setup.py
requirements.txt

rust 

need linux and macos (bash or shell script)

submit issue is problem

(don't need to know how to code in rust)

## knowledge

- (async, event loops) asyncio
- fsm


------

Ensure your environment and knowledge are ready before diving into the Quickstart.

---

## 1. Environment

- **Operating system**  
  - Linux or macOS (Bash shell)  
  - *(Windows users: use Git Bash or WSL)*  
- **Python**  
  - Version 3.10 or later  
  - `python3` and `pip` on your `PATH`  
- **Rust toolchain**  
  - `rustc` and `cargo` installed (for native-module support)  
  - Not required if you only use the pip-installed SDK  
- **Git**  
  - `git` on your `PATH`

> **Copy-template:**  
> “We recommend using a Linux or macOS environment with Bash. Windows users can leverage Git Bash or WSL for full compatibility.”

---

## 2. SDK Dependencies

The SDK install process will pull in:

- **Core Python package** (`summoner-sdk`)  
- **Python build tools**:  
  - `setuptools`  
  - `wheel`  
  - `maturin` (for Rust extensions)  
- **Rust crates** (only if running the build script)

All required packages are listed in `setup.py` and `requirements.txt`.

> **Copy-template:**  
> “When you run `pip install summoner-sdk`, you’ll get the core client, server, and protocol libraries. If you use `build_sdk.sh`, the script also installs any Rust-based extensions listed in your `build.txt`.”

---

## 3. Development Tools

- **Virtual environment**  
  - Recommended: `python3 -m venv .venv`  
  - Alternatives: Conda, Pipenv  
- **Editor / IDE**  
  - Any editor supporting Python and optionally Rust  
- **Issue reporting**  
  - If you encounter problems, open an issue on the [Summoner SDK GitHub repo](https://github.com/Summoner-Network/summoner-sdk/issues).

---

## 4. Conceptual Knowledge

Familiarity with the following will help you follow the Quickstart and deeper guides:

- **Asynchronous programming**  
  - Python’s `asyncio` event loop  
  - `async`/`await` syntax  
- **Finite State Machines (FSM)**  
  - Modeling sequential agent behaviours  
  - State transitions and handlers  

> **Copy-template:**  
> “If you’re new to `asyncio`, check out the official Python docs. For FSM concepts, any tutorial on state machines will clarify how Summoner models agent flows.”

---

<p align="center">
  <a href="../index.md">&laquo; Previous: Quickstart (Intro)</a>
  &nbsp;|&nbsp;
  <a href="basics_client.md">Next: Client (Basics) &raquo;</a>
</p>
```

**How to use this template**

1. Adjust any links or package names to match your latest repo paths.
2. Swap in additional tools or versions if you support Windows natively.
3. Extend the Troubleshooting section if you encounter recurring setup errors.




<p align="center">
  <a href="../index.md">&laquo; Previous: Quickstart (Intro)</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="basics_client.md">Next: Client (Basics) &raquo;</a>
</p>