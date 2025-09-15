# Module: `summoner.protocol.triggers`

Builds a tree of named **signals** from a simple indented text source and exposes them as attributes on a dynamically generated `Trigger` class. Provides event types (`Move`, `Stay`, `Test`), a convenience `Action` namespace, and utilities for parsing a TRIGGERS file.

**Typical workflow**

```python
from summoner.protocol.triggers import load_triggers, Move, Action, extract_signal

Trigger = load_triggers(text="""
OK
    acceptable
    all_good
error
    minor
    major
""")

assert Trigger.OK > Trigger.acceptable       # parent > child
sig = extract_signal(Move(Trigger.error))     # -> <Signal 'error'>
assert isinstance(Move(Trigger.OK), Action.MOVE)
```

---

## Quick map

* `Signal` — comparable signal value with a stable path and name.
* `Event` — base event carrying a `Signal`.
* `Move`, `Stay`, `Test` — concrete event types.
* `Action` — namespace of event classes: `MOVE`, `STAY`, `TEST`.
* Parsing utilities: `parse_signal_tree_lines`, `parse_signal_tree`.
* Building a trigger namespace: `build_triggers`, `load_triggers`.
* Helpers and internals: `is_valid_varname`, `preprocess_line`, `update_hierarchy`, `simplify_leaves`, `extract_signal`.
* Constants: `_VARNAME_RE`, `WORKING_DIR`.

---

## Constants

### `_VARNAME_RE`

**Type**

`re.Pattern[str]`

**Description**

Compiled regex used by `is_valid_varname` to validate Python identifiers: `^[A-Za-z_][A-Za-z0-9_]*$`.

---

### `WORKING_DIR`

**Type**

`pathlib.Path`

**Default**

`Path(sys.argv[0]).resolve().parent`

**Description**

Base directory used by `load_triggers` when reading the TRIGGERS file by name.

---

## Classes and data types

### `Signal`

**Summary**

Comparable signal identified by a **path** tuple and a **name**. Ordering encodes ancestry in the trigger tree.

**Constructor**

```python
summoner.protocol.triggers.Signal(path: tuple[int, ...], name: str)
```

**Attributes**

| Name   | Type              | Access    | Description                                                            |
| ------ | ----------------- | --------- | ---------------------------------------------------------------------- |
| `path` | `tuple[int, ...]` | read-only | Position in the tree. Parent paths are strict prefixes of child paths. |
| `name` | `str`             | read-only | Canonical signal name.                                                 |

**Ordering semantics**

* `a > b` if and only if `a` is a **strict ancestor** of `b` in the tree.
* `a >= b` if `a` is the same node as `b` or an ancestor of `b`.
* Siblings are not comparable using `>` or `<`.

**Example**

```python
ok = Signal((0,), "OK")
acceptable = Signal((0, 0), "acceptable")
assert ok > acceptable
assert not (acceptable > ok)
```

**Invariants**

`hash(Signal) == hash(path)` and equality is by `path`.

---

### `Event`

**Summary**

Base class for events. Holds a single `Signal` and prints as `ClassName(<Signal 'name'>)`.

**Constructor**

```python
summoner.protocol.triggers.Event(signal: Signal)
```

**Attributes**

| Name     | Type     | Access    | Description        |
| -------- | -------- | --------- | ------------------ |
| `signal` | `Signal` | read-only | Associated signal. |

**Example**

```python
e = Event(Trigger.OK)
repr(e)  # 'Event(<Signal \"OK\">)'
```

---

### `Move` / `Stay` / `Test`

**Summary**

Concrete event subclasses of `Event` used to classify actions. `Test` sets `__test__ = False` for compatibility with pytest.

**Constructor**

```python
Move(signal: Signal)
Stay(signal: Signal)
Test(signal: Signal)
```

**Example**

```python
from summoner.protocol.triggers import Move, Stay, Test

Move(Trigger.error)
Stay(Trigger.OK)
Test(Trigger.minor)
```

---

### `Action`

**Summary**

Namespace that exposes event classes as attributes for ergonomic type checks.

**Attributes**

| Name   | Type         | Access    | Description       |
| ------ | ------------ | --------- | ----------------- |
| `MOVE` | `type[Move]` | read-only | The `Move` class. |
| `STAY` | `type[Stay]` | read-only | The `Stay` class. |
| `TEST` | `type[Test]` | read-only | The `Test` class. |

**Example**

```python
isinstance(Move(Trigger.OK), Action.MOVE)  # True
```

---

## Functions

### `is_valid_varname`

**Summary**

Return `True` if a string is a valid Python identifier for use as a trigger name.

**Signature**

```python
summoner.protocol.triggers.is_valid_varname(name: str) -> bool
```

**Parameters**

| Name   | Type  | Required | Default | Description           |
| ------ | ----- | -------- | ------- | --------------------- |
| `name` | `str` | yes      | —       | Candidate identifier. |

**Returns**

* `bool`: validity result.

**Examples**

```python
assert is_valid_varname("OK")
assert not is_valid_varname("bad-name")
```

---

### `preprocess_line`

**Summary**

Normalize a raw TRIGGERS line: strip newline, expand tabs, compute indentation, remove trailing comments, and skip blanks.

**Signature**

```python
summoner.protocol.triggers.preprocess_line(raw: str, lineno: int, tabsize: int) -> tuple[int, int, str] | None
```

**Parameters**

| Name      | Type  | Required | Default | Description                                                  |
| --------- | ----- | -------- | ------- | ------------------------------------------------------------ |
| `raw`     | `str` | yes      | —       | Raw input line including newline.                            |
| `lineno`  | `int` | yes      | —       | 1-based source line index. Returned unmodified in the tuple. |
| `tabsize` | `int` | yes      | —       | Tab expansion size in spaces.                                |

**Returns**

* `tuple[int, int, str]`: `(lineno, indent, name)` where `indent` is the count of leading spaces after tab expansion and `name` is the stripped content before `#`.
* `None` if the line is empty after comment removal.

**Example**

```python
preprocess_line("\tOK  # top", 1, 8)  # -> (1, 8, 'OK')
```

---

### `update_hierarchy`

**Summary**

Update the current indentation stack and return the new depth for a line.

**Signature**

```python
summoner.protocol.triggers.update_hierarchy(indent: int, indent_levels: list[int]) -> int
```

**Parameters**

| Name            | Type        | Required | Default | Description                                          |
| --------------- | ----------- | -------- | ------- | ---------------------------------------------------- |
| `indent`        | `int`       | yes      | —       | Leading space count for the current line.            |
| `indent_levels` | `list[int]` | yes      | —       | Stack of seen indentation levels. Modified in place. |

**Returns**

* `int`: depth index corresponding to the parent subtree in the tree-building algorithm.

**Raises**

* `ValueError` if the indent does not match any known level when dedenting.

**Example**

```python
levels = [0]
depth = update_hierarchy(0, levels)  # 0
# New child block
_ = update_hierarchy(4, levels)      # levels -> [0, 4]
```

---

### `simplify_leaves`

**Summary**

Convert empty dict leaves to `None` in a nested tree structure. Operates in place.

**Signature**

```python
summoner.protocol.triggers.simplify_leaves(tree: dict[str, Any]) -> None
```

**Parameters**

| Name   | Type             | Required | Default | Description                                             |
| ------ | ---------------- | -------- | ------- | ------------------------------------------------------- |
| `tree` | `dict[str, Any]` | yes      | —       | Nested mapping built during parsing. Modified in place. |

**Returns**

* `None`

**Example**

```python
t = {"OK": {}, "error": {"minor": {}}}
simplify_leaves(t)
assert t == {"OK": None, "error": {"minor": None}}
```

---

### `parse_signal_tree_lines`

**Summary**

Parse a list of TRIGGERS lines into a nested dictionary representing the signal tree. Entry point for testing.

**Signature**

```python
summoner.protocol.triggers.parse_signal_tree_lines(lines: list[str], tabsize: int = 8) -> dict[str, Any]
```

**Parameters**

| Name      | Type        | Required | Default | Description                    |
| --------- | ----------- | -------- | ------- | ------------------------------ |
| `lines`   | `list[str]` | yes      | —       | Lines of the TRIGGERS content. |
| `tabsize` | `int`       | no       | `8`     | Tab expansion size in spaces.  |

**Returns**

* `dict[str, Any]`: nested mapping where leaves are `None` and branches are dicts.

**Raises**

* `ValueError` for invalid names, duplicate names at the same depth, or inconsistent indentation.

**Example**

```python
lines = ["OK", "\tacceptable", "error", "\tmajor"]
tree = parse_signal_tree_lines(lines)
# {'OK': {'acceptable': None}, 'error': {'major': None}}
```

---

### `parse_signal_tree`

**Summary**

Read a TRIGGERS file from disk and parse it to a nested dictionary.

**Signature**

```python
summoner.protocol.triggers.parse_signal_tree(filepath: str, tabsize: int = 8) -> dict[str, Any]
```

**Parameters**

| Name       | Type  | Required | Default | Description                   |
| ---------- | ----- | -------- | ------- | ----------------------------- |
| `filepath` | `str` | yes      | —       | Path to the TRIGGERS file.    |
| `tabsize`  | `int` | no       | `8`     | Tab expansion size in spaces. |

**Returns**

* `dict[str, Any]`: nested mapping as in `parse_signal_tree_lines`.

**Raises**

* `FileNotFoundError` if the file does not exist.
* `ValueError` for parse errors as in `parse_signal_tree_lines`.

**Example**

```python
tree = parse_signal_tree("./TRIGGERS")
```

---

### `build_triggers`

**Summary**

Create a dynamic `Trigger` class from a nested dictionary tree. Each signal name becomes a `Signal` attribute on the class.

**Signature**

```python
summoner.protocol.triggers.build_triggers(tree: dict[str, Any]) -> type
```

**Parameters**

| Name   | Type             | Required | Default | Description                                              |
| ------ | ---------------- | -------- | ------- | -------------------------------------------------------- |
| `tree` | `dict[str, Any]` | yes      | —       | Nested mapping as returned by `parse_signal_tree_lines`. |

**Returns**

* `type`: a new `Trigger` class with a `Signal` attribute for each leaf or branch, and helper members.

**Class attributes on the returned `Trigger`**

| Name            | Type                         | Description                                  |                                                  |
| --------------- | ---------------------------- | -------------------------------------------- | ------------------------------------------------ |
| `<signal_name>` | `Signal`                     | One attribute per signal with the same name. |                                                  |
| `_path_to_name` | `dict[tuple[int, ...], str]` | Map from path to name.                       |                                                  |
| `name_of`       | \`Callable[..., str         | None]\`                                      | `staticmethod` that maps a path tuple to a name. |

**Raises**

* `ValueError` if any signal name conflicts with reserved names, Python keywords, or starts with `_`.

**Example**

```python
Trigger = build_triggers({"OK": {"acceptable": None}, "error": {"major": None}})
assert Trigger.name_of(1, 0) == "major"
```

---

### `extract_signal`

**Summary**

Return the underlying `Signal` from an `Event` or pass through a `Signal`. Accepts `None` and returns `None`.

**Signature**

```python
summoner.protocol.triggers.extract_signal(trigger: Event | Signal | None) -> Signal | None
```

**Parameters**

| Name      | Type    | Required | Default | Description |   |                                             |
| --------- | ------- | -------- | ------- | ----------- | - | ------------------------------------------- |
| `trigger` | \`Event | Signal   | None\`  | yes         | — | Event instance, signal instance, or `None`. |

**Returns**

* `Signal | None`: the extracted signal or `None`.

**Raises**

* `TypeError` if `trigger` is neither `Event`, `Signal`, nor `None`.

**Example**

```python
extract_signal(Move(Trigger.error))  # <Signal 'error'>
extract_signal(Trigger.OK)           # <Signal 'OK'>
extract_signal(None)                 # None
```

---

### `load_triggers`

**Summary**

Load and build a `Trigger` class from one of: inline text, a prebuilt nested dict, or a TRIGGERS file on disk. Text takes priority over dict, which takes priority over file.

**Signature**

```python
summoner.protocol.triggers.load_triggers(
    triggers_file: str | None = "TRIGGERS",
    text: str | None = None,
    json_dict: dict[str, Any] | None = None,
) -> type
```

**Parameters**

| Name            | Type              | Required | Default | Description  |                                                                  |
| --------------- | ----------------- | -------- | ------- | ------------ | ---------------------------------------------------------------- |
| `triggers_file` | \`str             | None\`   | no      | `"TRIGGERS"` | File name resolved relative to `WORKING_DIR` when used.          |
| `text`          | \`str             | None\`   | no      | `None`       | Inline TRIGGERS content. Highest priority when provided.         |
| `json_dict`     | \`dict[str, Any] | None\`   | no      | `None`       | Nested mapping already in parsed form. Used if `text` is `None`. |

**Returns**

* `type`: the generated `Trigger` class.

**Raises**

* `FileNotFoundError` with a clear message if the file path cannot be resolved when needed.
* `ValueError` for parse errors in the provided content or dict.

**Examples**

*Minimal inline text*

```python
Trigger = load_triggers(text="OK\n    acceptable\nerror\n    major")
assert Trigger.OK > Trigger.acceptable
```

*From a dict*

```python
Trigger = load_triggers(json_dict={"OK": {"all_good": None}, "error": {"minor": None}})
```

*From a file*

```python
Trigger = load_triggers(triggers_file="TRIGGERS")
```

---

## See also

* `sdk_doc/proto.md` for how signals and events link to routing and processing.
* `summoner.protocol.flow` for route parsing and normalization.
* `summoner.protocol.process` for `Node`, `Receiver`, `Sender`, and `StateTape`.


<p align="center">
  <a href="../proto.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.protocol</b></code> </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="./process.md">Next: <code style="background: transparent;">Summoner<b>.protocol.process</b></code> &raquo;</a>
</p>