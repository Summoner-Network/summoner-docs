# Installation of the Summoner SDK

Quickly set up your development environment and get the Summoner SDK installed—either via our one-stop build script or directly from PyPI.

## Purpose & audience
- **Who:** Developers who want a friction-free way to install and start using Summoner  
- **What you’ll get:**  
  - Clear, version-agnostic installation steps  
  - A choice between pip install vs. our build/dev script  
  - Troubleshooting tips and verification commands

---

## 1. Prerequisites

Before installing, ensure you have:

- **Python 3.10+** and `python3` on your PATH  
- **Git** on your PATH  
- **Bash shell** (for the build script)  
- *(Optional)* `venv` or `conda` for isolated environments  

> **Tip:** On Windows, use WSL or Git Bash to run our build script.

---

## 2. Installation Methods

You can install the SDK in **two** ways:

| Method                     | Pros                                       | Cons                           |
|----------------------------|--------------------------------------------|--------------------------------|
| **`pip install summoner-sdk`** | Fastest; pulls latest published release   | No native-module merging       |
| **`build_sdk.sh` script**  | Clones core + merges your native modules   | Requires Bash, build.txt setup |

---

### 2.1. Via PyPI (pip)

**Steps**  
1. Create and activate a virtual environment  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
```

2. Install the SDK

   ```bash
   pip install summoner-sdk
   ```
3. Verify installation

   ```bash
   summoner --version
   ```

> **Sample copy:**
> “Installing from PyPI is the fastest way to get started. It delivers the core SDK without any native-module extensions.”

---

### 2.2. Using the Build & Dev Script

Our `build_sdk.sh` handles cloning the core repo, merging your native modules, creating a venv, and running smoke tests.

#### 2.2.1. Setup

1. Place your native-module repos in `build.txt` (one URL per line).
2. *(Optional)* For a quick demo, list a starter-template in `test_build.txt`.

#### 2.2.2. Running the Script

* **Source mode** (recommended): keeps you in the activated venv

  ```bash
  source build_sdk.sh setup [build|test_build]
  ```
* **Execute mode**: runs in a subshell; you’ll need to manually activate

  ```bash
  bash build_sdk.sh setup
  source venv/bin/activate
  ```

#### 2.2.3. Key Commands

| Command       | What it does                                                         | Example                         |
| ------------- | -------------------------------------------------------------------- | ------------------------------- |
| `setup`       | Clone core, merge native modules, create & activate venv, run extras | `source build_sdk.sh setup`     |
| `delete`      | Remove all generated dirs (sdk/, venv/, native\_build/)              | `bash build_sdk.sh delete`      |
| `reset`       | Shortcut for delete + setup                                          | `bash build_sdk.sh reset`       |
| `deps`        | Reinstall Rust/Python deps in venv                                   | `bash build_sdk.sh deps`        |
| `test_server` | Launch a demo server against your SDK                                | `bash build_sdk.sh test_server` |
| `clean`       | Wipe build artifacts, keep venv                                      | `bash build_sdk.sh clean`       |

> **Sample copy:**
> “The build script is ideal if you’re developing custom native extensions. It reads your `build.txt`, clones each repo, merges them into Summoner Core, then spins up a ready-to-use venv.”

---

## 3. Verifying Your Installation

Whichever method you choose, confirm everything is in place:

```bash
# Check SDK CLI
summoner --help

# Run a minimal smoke-test
echo "from summoner import Agent; print(Agent)" | python3
```

---

## 4. Troubleshooting

* **“command not found: summoner”**

  * Ensure you’ve activated your venv: `source venv/bin/activate`
  * Check your PATH: `which summoner`

* **Build script errors**

  * Verify `build.txt` URLs are correct
  * Confirm `git` and `python3` are installed

* **Version mismatch**

  * For pip: `pip install --upgrade summoner-sdk`
  * For script: `bash build_sdk.sh deps`

---

<p align="center">
  <a href="what_is.md">&laquo; Previous: What is the Summoner SDK for?</a>
  &nbsp;|&nbsp;
  <a href="quickstart/index.md">Next: Quickstart &raquo;</a>
</p>
```

### Why this structure?

1. **Front matter & sidebar\_label**
   ­Integrates nicely with your docsite sidebar.
2. **Purpose & audience**
   ­Sets expectations (“why read this?”).
3. **Clear Install Methods**
   ­Beginners can choose pip, power-users can opt for build script.
4. **Tables for commands**
   ­Easily scannable reference for each script command.
5. **Copy-templates**
   ­Neutral-tone paragraphs you can copy/paste.
6. **Troubleshooting**
   ­Addresses the most common pain points right on this page.


<p align="center">
  <a href="what_is.md">&laquo; Previous: What is Summoner's SDK used for?</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="quickstart/index.md">Next: Quickstart &raquo;</a>
</p>