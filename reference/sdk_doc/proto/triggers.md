# <code style="background: transparent;">Summoner<b>.protocol.triggers</b></code>

This page documents the **Python SDK interface** for working with Summoner signals and trigger trees.

The module provides:

* A **signal-tree loader** that parses an indented "TRIGGERS" definition into a nested tree.
* A dynamically generated **`Trigger` class** whose attributes are `Signal` instances.
* Lightweight **event wrappers** (`Move`, `Stay`, `Test`) and an `Action` container.
* Utilities for extracting `Signal` from either a `Signal` or an `Event`.


## `is_valid_varname`

```python
def is_valid_varname(name: str) -> bool
```

### Behavior

Checks whether `name` is a valid Python identifier suitable for use as a generated `Trigger.<name>` attribute.

### Inputs

#### `name`

* **Type:** `str`
* **Meaning:** Candidate signal name.

### Outputs

* **Type:** `bool`
* **Meaning:** `True` if the name matches identifier rules, otherwise `False`.

### Examples

```python
from summoner.protocol.triggers import is_valid_varname

assert is_valid_varname("OK") is True
assert is_valid_varname("all_good") is True
assert is_valid_varname("not valid") is False
assert is_valid_varname("123bad") is False
```

## `preprocess_line`

```python
def preprocess_line(raw: str, lineno: int, tabsize: int) -> Optional[tuple[int, int, str]]
```

### Behavior

Normalizes a raw line from a triggers file:

* Strips the trailing newline.
* Expands tabs into spaces (using `tabsize`).
* Measures indentation from leading spaces.
* Removes inline comments starting with `#`.
* Skips blank or comment-only lines.

### Inputs

#### `raw`

* **Type:** `str`
* **Meaning:** Raw line from the triggers definition.

#### `lineno`

* **Type:** `int`
* **Meaning:** 1-based line number used for error messages.

#### `tabsize`

* **Type:** `int`
* **Meaning:** Tab expansion width.

### Outputs

* **Type:** `Optional[tuple[int, int, str]]`
* **Meaning:**

  * Returns `(lineno, indent, name)` if the line defines a signal.
  * Returns `None` if the line should be skipped.

### Examples

```python
from summoner.protocol.triggers import preprocess_line

assert preprocess_line("OK\n", 1, 8) == (1, 0, "OK")
assert preprocess_line("    acceptable  # comment\n", 2, 8) == (2, 4, "acceptable")
assert preprocess_line("# comment-only\n", 3, 8) is None
assert preprocess_line("   \n", 4, 8) is None
```

## `update_hierarchy`

```python
def update_hierarchy(indent: int, indent_levels: list[int]) -> int
```

### Behavior

Maintains indentation state while parsing a triggers file and returns the computed tree depth for the current line.

* If `indent` matches the current level, depth stays the same.
* If `indent` increases, a new depth level is created.
* If `indent` decreases, it must match a previously seen indentation level; otherwise parsing fails.

### Inputs

#### `indent`

* **Type:** `int`
* **Meaning:** The indentation (in spaces) of the current line.

#### `indent_levels`

* **Type:** `list[int]`
* **Meaning:** The current stack of indentation levels. Mutated in place.

### Outputs

* **Type:** `int`
* **Meaning:** The computed depth for the current line.

### Examples

```python
from summoner.protocol.triggers import update_hierarchy

levels = [0]
assert update_hierarchy(0, levels) == 0
assert update_hierarchy(4, levels) == 1
assert levels == [0, 4]
assert update_hierarchy(4, levels) == 1
assert update_hierarchy(0, levels) == 0
```

## `simplify_leaves`

```python
def simplify_leaves(tree: dict[str, Any]) -> None
```

### Behavior

Post-processes a nested dict tree in place so that empty dictionaries are replaced with `None` to mark leaves.

### Inputs

#### `tree`

* **Type:** `dict[str, Any]`
* **Meaning:** The parsed nested tree.

### Outputs

Returns `None` (operates in place).

### Examples

```python
from summoner.protocol.triggers import simplify_leaves

tree = {"OK": {"acceptable": {}}, "error": {}}
simplify_leaves(tree)
assert tree == {"OK": {"acceptable": None}, "error": None}
```

## `parse_signal_tree_lines`

```python
def parse_signal_tree_lines(lines: list[str], tabsize: int = 8) -> dict[str, Any]
```

### Behavior

Parses a list of trigger-definition lines into a nested dict tree.

Rules:

* Each non-empty, non-comment line defines a signal name.
* Indentation defines parent-child relationships.
* Names must be valid Python identifiers.
* Duplicate names at the same indentation scope are rejected.
* Inconsistent indentation decreases (to an unseen indent level) raises an error.

### Inputs

#### `lines`

* **Type:** `list[str]`
* **Meaning:** Raw lines that define the trigger hierarchy.

#### `tabsize`

* **Type:** `int`
* **Meaning:** Tab expansion width for parsing.
* **Default:** `8`

### Outputs

* **Type:** `dict[str, Any]`
* **Meaning:** Nested dict describing the hierarchy, with leaves represented as `None`.

### Examples

#### Parse from an in-memory text block

```python
from summoner.protocol.triggers import parse_signal_tree_lines

text = """
OK
    acceptable
    all_good
error
    minor
    major
"""

tree = parse_signal_tree_lines(text.splitlines())
assert tree["OK"]["acceptable"] is None
assert tree["error"]["major"] is None
```

## `parse_signal_tree`

```python
def parse_signal_tree(filepath: str, tabsize: int = 8) -> dict[str, Any]
```

### Behavior

Reads a triggers file from disk and parses it into a nested dict tree using `parse_signal_tree_lines`.

### Inputs

#### `filepath`

* **Type:** `str`
* **Meaning:** Path to the triggers file.

#### `tabsize`

* **Type:** `int`
* **Meaning:** Tab expansion width.
* **Default:** `8`

### Outputs

* **Type:** `dict[str, Any]`
* **Meaning:** Nested dict describing the hierarchy.

### Examples

```python
from summoner.protocol.triggers import parse_signal_tree

tree = parse_signal_tree("TRIGGERS")
```

## `class Signal`

```python
class Signal
```

### Behavior

Represents a named signal with a stable hierarchical path:

* `path`: a tuple of integer indices describing the position in the trigger tree.
* `name`: the signal's name as written in the triggers definition.

Signals support ordering comparisons based on ancestry:

* `a > b` is true when `a` is a strict ancestor of `b` (prefix match on paths).
* `a >= b` includes equality.
* Hashing and equality are based on `path`.

### Inputs

#### `path`

* **Type:** `tuple[int, ...]`
* **Meaning:** Hierarchical path.

#### `name`

* **Type:** `str`
* **Meaning:** Signal name.

### Outputs

A `Signal` instance.

### Examples

```python
from summoner.protocol.triggers import Signal

root = Signal((0,), "OK")
child = Signal((0, 0), "acceptable")

assert root > child
assert child < root
assert root.name == "OK"
assert child.path == (0, 0)
```

## `build_triggers`

```python
def build_triggers(tree: dict[str, Any]) -> type
```

### Behavior

Builds and returns a dynamically-generated `Trigger` class.

The returned class:

* Exposes each signal name as a class attribute: `Trigger.OK`, `Trigger.acceptable`, etc.
* Assigns each attribute a `Signal` instance with a stable `path`.
* Provides `Trigger.name_of(*path)` to resolve a name from a path tuple.

Names that conflict with Python reserved keywords or common object attributes are rejected.

### Inputs

#### `tree`

* **Type:** `dict[str, Any]`
* **Meaning:** Nested trigger tree (as returned by `parse_signal_tree_lines` / `parse_signal_tree`).

### Outputs

* **Type:** `type`
* **Meaning:** A dynamically generated `Trigger` class.

### Examples

```python
from summoner.protocol.triggers import build_triggers

tree = {"OK": {"acceptable": None}, "error": {"major": None}}
Trigger = build_triggers(tree)

assert Trigger.OK.name == "OK"
assert Trigger.acceptable.path == (0, 0)
assert Trigger.name_of(1, 0) == "major"
```

## `class Event`

```python
class Event
```

### Behavior

Wraps a `Signal` as a typed protocol event. The module defines three event subclasses:

* `Move(signal)`
* `Stay(signal)`
* `Test(signal)`

`Test` is marked with `__test__ = False` to avoid certain test discovery behaviors.

### Inputs

#### `signal`

* **Type:** `Signal`
* **Meaning:** The underlying signal carried by the event.

### Outputs

An `Event` (or subclass) instance.

### Examples

```python
from summoner.protocol.triggers import Signal, Move, Stay, Test

s = Signal((0,), "OK")

e1 = Move(s)
e2 = Stay(s)
e3 = Test(s)

assert e1.signal is s
```

## `class Action`

```python
class Action
```

### Behavior

A simple container mapping action names to event classes:

* `Action.MOVE` is `Move`
* `Action.STAY` is `Stay`
* `Action.TEST` is `Test`

This is commonly used as a stable reference set when validating or resolving actions by name.

### Inputs

None.

### Outputs

Not instanced (used as a namespace container).

### Examples

```python
from summoner.protocol.triggers import Action, Signal

s = Signal((0,), "OK")
e = Action.MOVE(s)
assert type(e).__name__ == "Move"
```

## `extract_signal`

```python
def extract_signal(trigger: Any) -> Optional[Signal]
```

### Behavior

Normalizes an input into a `Signal`:

* If input is an `Event`, returns `event.signal`.
* If input is a `Signal`, returns it unchanged.
* If input is `None`, returns `None`.
* Otherwise raises `TypeError`.

### Inputs

#### `trigger`

* **Type:** `Any`
* **Meaning:** A `Signal`, an `Event`, or `None`.

### Outputs

* **Type:** `Optional[Signal]`
* **Meaning:** Extracted signal (or `None`).

### Examples

```python
from summoner.protocol.triggers import Signal, Move, extract_signal

s = Signal((0,), "OK")
e = Move(s)

assert extract_signal(s) is s
assert extract_signal(e) is s
assert extract_signal(None) is None
```

## `load_triggers`

```python
def load_triggers(
    triggers_file: Optional[str] = "TRIGGERS",
    text: Optional[str] = None,
    json_dict: Optional[dict[str, Any]] = None,
) -> type
```

### Behavior

Builds and returns a `Trigger` class from one of three inputs:

Priority:

1. If `text` is provided, parse it as trigger definitions.
2. Else if `json_dict` is provided, use it as the tree directly (shallow-copied).
3. Else, read and parse `triggers_file` relative to the process working directory used by the module.

If the triggers file cannot be found, raises `FileNotFoundError` with a clearer message.

### Inputs

#### `triggers_file`

* **Type:** `Optional[str]`
* **Meaning:** Filename/path to the triggers file used when `text` and `json_dict` are not provided.
* **Default:** `"TRIGGERS"`

#### `text`

* **Type:** `Optional[str]`
* **Meaning:** Inline trigger definitions. If provided, it is used instead of reading a file.

#### `json_dict`

* **Type:** `Optional[dict[str, Any]]`
* **Meaning:** Nested tree structure matching the output schema of `parse_signal_tree_lines`.

### Outputs

* **Type:** `type`
* **Meaning:** A dynamically generated `Trigger` class whose attributes are `Signal` instances.

### Examples

#### Load from the default `TRIGGERS` file

```python
from summoner.protocol.triggers import load_triggers

Trigger = load_triggers()
print(Trigger.OK)
```

#### Load from inline text

```python
from summoner.protocol.triggers import load_triggers

text = """
OK
    acceptable
error
    major
"""

Trigger = load_triggers(text=text)
assert Trigger.acceptable.path == (0, 0)
assert Trigger.name_of(1, 0) == "major"
```

#### Load from a prebuilt tree dict

```python
from summoner.protocol.triggers import load_triggers

tree = {"OK": {"acceptable": None}, "error": {"major": None}}
Trigger = load_triggers(json_dict=tree)

assert Trigger.OK.name == "OK"
assert Trigger.major.name == "major"
```


---

<p align="center">
  <a href="../proto.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.protocol</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="./process.md">Next: <code style="background: transparent;">Summoner<b>.protocol.process</b></code> &raquo;</a>
</p>