# Prerequisites

Summoner's SDK currently supports installation on **Unix-based systems**, including Linux and macOS. This is because most of our scripts rely on the Unix shell [Bash](https://www.gnu.org/software/bash/).

Users on Windows may still use the SDK, but installation will require some adaptation. You may either:

* Use [Git Bash](https://gitforwindows.org/) or [WSL](https://learn.microsoft.com/en-us/windows/wsl/install), or
* Manually modify the installation scripts to use Windows-compatible commands.

<p align="center">
  <img width="240px" src="../../assets/img/summoners_library_rounded.png"/>
</p>

Please note that some components — especially the [Rust installation](https://www.rust-lang.org/tools/install) — may differ significantly from Unix workflows. However, Windows users can still rely on the **Python-only implementation** of the server and can freely use the client code, which is entirely written in Python.


## Software Requirements

To install the [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk), the following software must be available:

* `python3` (Python 3.9+ is required) and the `pip` package installer
* `git` available on your `PATH` (needed to clone repositories and follow tutorials)
* `rustc` and `cargo` (we **strongly recommend** installing Rust using the [`rustup`](https://rustup.rs) toolchain manager)


<p align="center">
  <img width="140px" src="../../assets/img/scroll_on_floor_rounded.png"/>
</p>


> [!NOTE]
> If you are using our **automated installation scripts** (typically described in each repository's `README.md`), all required Python and Rust packages will be installed for you — including:
>
> * All dependencies listed in the `setup.py` file of [`summoner-core`](https://github.com/Summoner-Network/summoner-core)
> * Any packages specified in `requirements.txt` files of other `summoner-*` modules derived from our [starter template](https://github.com/Summoner-Network/starter-template)
> 
> However, if you are setting things up manually — for instance, on Windows — you may need to install these dependencies yourself.

Our installation script usually sets up a Python virtual environment (`venv`). If you are using VS Code, be sure to select the interpreter from that environment — it's where all Python and Rust dependencies are installed. If you're not already inside the virtual environment, you can activate it with:

```bash
source venv/bin/activate
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

