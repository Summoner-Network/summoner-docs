# Prerequisites

Summoner's SDK supports installation on **POSIX systems** (Linux and macOS) and **Windows**. On POSIX, the installer scripts run in the Unix shell [Bash](https://www.gnu.org/software/bash/). On Windows, the native installer scripts are written for [PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows?view=powershell-7.5). Windows users can also run some Bash-based workflows via [Git Bash](https://gitforwindows.org/), or, for full POSIX compatibility, via [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

<p align="center">
  <img width="240px" src="../../assets/img/summoners_library_rounded.png"/>
</p>

Summoner supports two server backends: a **Rust server** and a **Python server**. On **POSIX**, the installer uses the Rust server by default, which requires [Rust](https://www.rust-lang.org/tools/install). If you prefer to avoid Rust, you can select the Python server by passing `--server python` (see the README in [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk/)). On **native Windows**, the default backend is the Python server (no Rust required). If you want to use the Rust server on Windows, install and run Summoner through **WSL**.

## Software Requirements

To install the [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk), the following software must be available:

* `python3` (Python 3.9+ is required) and the `pip` package installer
* `git` available on your `PATH` (needed to clone repositories and follow tutorials)

If you use the **Rust server**, you also need:

* `rustc` and `cargo` (we **strongly recommend** installing Rust using the [`rustup`](https://rustup.rs) toolchain manager)

<p align="center">
  <img width="140px" src="../../assets/img/scroll_on_floor_rounded.png"/>
</p>

> [!NOTE]
> If you are using our **automated installation scripts** (typically described in each repository's `README.md`), the scripts will install the required Python packages into your environment, and will also build/install Rust components when the Rust toolchain is available. This includes:
>
> * All dependencies listed in the `setup.py` file of [`summoner-core`](https://github.com/Summoner-Network/summoner-core)
> * Any dependencies listed in the `requirements.txt` files of SDK extensions you include in `build.txt` (e.g. `extension-utilities`, `extension-agentclass`). These extensions are typically hosted in repositories created from our [extension template](https://github.com/Summoner-Network/extension-template).

Our installation script usually sets up a Python virtual environment (`venv`). If you are using VS Code, be sure to select the interpreter from that environment — it's where all Python and Rust dependencies are installed. If you're not already inside the virtual environment, you can activate it with:

```bash
source venv/bin/activate
```

On Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

## Knowledge Requirements

Beyond software setup, some background knowledge can significantly enhance your ability to use and understand the SDK.

We recommend familiarity with:

* [Finite state machines and automata](https://en.wikipedia.org/wiki/Finite-state_machine)
* [Multi-agent systems](https://en.wikipedia.org/wiki/Multi-agent_system) and, more broadly, [complex systems](https://en.wikipedia.org/wiki/Complex_system)
* [Asynchronous programming](https://en.wikipedia.org/wiki/Asynchrony_%28computer_programming%29)

<p align="center">
  <img width="240px" src="../../assets/img/golem_wizard_rounded.png" />
</p>

For users interested in the **theoretical foundations of agent design**, the SDK draws from several areas in mathematics and computer science, such as:

* [Graph theory](https://en.wikipedia.org/wiki/Graph_theory), including [graph traversal](https://en.wikipedia.org/wiki/Graph_traversal) and [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
* [Category theory](https://en.wikipedia.org/wiki/Category_theory)
* [Higher category theory](https://en.wikipedia.org/wiki/Higher_category_theory)



<p align="center">
  <a href="what_is.md">&laquo; Previous: What Does the Summoner SDK Do?</a>  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="installation.md">Next: Installation &raquo;</a>
</p>

