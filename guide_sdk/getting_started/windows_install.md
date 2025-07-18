# Basic Setup Guide for Windows

This guide walks through how to set up the [`summoner-core`](https://github.com/Summoner-Network/summoner-core) SDK on Windows.

<p align="center">
  <img width="240px" src="../../assets/img/windows_install_rounded.png"/>
</p>

> [!WARNING]
> This tutorial covers only the `summoner-core` repository. Installing the full SDK (i.e., [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk)) follows a similar structure but requires additional Git commands to download and configure other components such as agent modules and tool extensions from our other repositories.


## Recommended Shells

We recommend using one of the following terminal environments:

* Git Bash (installed with Git for Windows)
* PowerShell (integrated in Windows)
* VS Code’s built-in terminal (set to Git Bash or PowerShell)


## 1. Clone the Repository

Open your terminal and navigate to a directory where you'd like to install the SDK:

```bash
git clone https://github.com/Summoner-Network/summoner-core.git
cd summoner-core
```

## 2. Set Up a Python Virtual Environment

To avoid interfering with system-wide packages, it's best to create a Python virtual environment.

### Create the virtual environment:

```bash
python -m venv .venv
```

This creates a folder named `.venv` inside the project.

### Activate the environment:

* In Git Bash:

  ```bash
  source .venv/Scripts/activate
  ```

* In PowerShell:

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

* In Command Prompt (if needed):

  ```cmd
  .venv\Scripts\activate.bat
  ```

Once activated, your prompt will show something like:

```
(.venv) C:\Users\You\summoner-core>
```

## 3. Install the Package

From inside the project directory (with the virtual environment activated), run:

```bash
pip install -e .
```

This installs `summoner-core` in "editable mode," meaning any code changes you make in the local directory will immediately apply when you run the SDK — no need to reinstall.

If you prefer a one-time install without linking to local files:

```bash
pip install .
```

This installs a static copy of the package and does not reflect local edits.


## 4. Notes on Server Configuration

By default, the current implementation of the `summoner-core` server uses the Python-only backend. Although Rust support is integrated into the project structure, it is currently not enable used on Windows — the server will automatically default to the Python version, and no Rust compilation or dependencies are required.

<p align="center">
  <a href="installation.md">&laquo; Previous: Back to Installation</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="quickstart/index.md">Next: Quickstart &raquo;</a>
</p>

