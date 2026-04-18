# Policy Events (<code style="background: transparent;">Summoner<b>.aurora.identity</b></code>)

This page documents **`SummonerIdentity.on_policy_event(...)`** and the structured event format emitted by identity lifecycle methods.

Policy events do not change protocol outcome by themselves. Their purpose is to expose stable lifecycle outcomes so application code, registries, and review tooling can observe replay pressure, validation failures, reset-like behavior, and stream events without scraping logs or guessing from `None` returns.

## Import path

```python
from summoner.aurora import SummonerIdentity
```

## `SummonerIdentity.on_policy_event`

```python
def on_policy_event(
    self,
    phase: str,
) -> Callable[[Callable[[str, dict], Any]], Callable[[str, dict], Any]]
```

### Behavior

Registers a per-instance telemetry handler for one lifecycle phase.

Handlers receive:

* `event_name: str`
* `context: dict`

`event_name` is the same value as the lifecycle status `code`.

### Allowed phases

Use one of the phase names below when registering a handler.

* `start_session`
* `continue_session`
* `advance_stream_session`
* `seal_envelope`
* `open_envelope`
* `verify_discovery_envelope`

### Registration semantics

* Invalid phases raise `ValueError`.
* Multiple handlers may be registered for the same phase.
* Handlers run in registration order.
* Handlers are instance-scoped, so one `SummonerIdentity` does not inherit another identity's policy handlers.
* Handlers may be synchronous or async.

### Inputs

#### `phase`

* **Type:** `str`
* **Meaning:** Lifecycle phase to observe.
* **Allowed values:** `start_session`, `continue_session`, `advance_stream_session`, `seal_envelope`, `open_envelope`, `verify_discovery_envelope`

### Outputs

Returns a decorator that registers one handler for the chosen phase and then returns that same handler unchanged.

### Error handling

Raises `ValueError` if `phase` is not one of the allowed lifecycle phases.

### Example

```python
from summoner.aurora import SummonerIdentity

identity = SummonerIdentity()

@identity.on_policy_event(phase="open_envelope")
def on_open(event_name, ctx):
    if event_name != "ok":
        print(ctx.get("validation_stage"), ctx.get("peer_fingerprint"))
```

## Emission model

The identity runtime emits policy events from the shared lifecycle return path used by the methods below.

| Method | Emitted phase |
| --- | --- |
| `start_session(...)` | `start_session` |
| `continue_session(...)` | `continue_session` |
| `advance_stream_session(...)` | `advance_stream_session` |
| `seal_envelope(...)` | `seal_envelope` |
| `open_envelope(...)` | `open_envelope` |
| `verify_discovery_envelope(...)` | `verify_discovery_envelope` |

Because the lifecycle methods are async, the event is emitted on the awaited completion path of that method.

### Important note

`continue_session(...)` may internally recover through a `start_session(...)` branch, so the emitted phase can reflect that recovery path rather than the original caller intent.

`verify_discovery_envelope(...)` is discovery-only. It can emit identity, signature, replay, and peer-learning outcomes, but it does not emit session-commit replacement semantics such as `replaced_active_incomplete`.

## Event context

### Base fields

Every policy event contains the small set of required fields below.

| Key | Type | Meaning |
| --- | --- | --- |
| `schema_version` | `int` | Event schema version. Currently `1`. |
| `ts` | `int` | Unix timestamp when the event was emitted. |
| `phase` | `str` | Lifecycle phase that emitted the event. |
| `ok` | `bool` | Success flag for the lifecycle result. |
| `code` | `str` | Outcome code. This is also passed as `event_name`. |
| `has_data` | `bool` | Whether the lifecycle method returned non-`None` data. |

### Optional fields

Some events add more detail. The event schema limits optional context fields to the set below so the event format stays stable and compact.

| Field | Meaning |
| --- | --- |
| `peer_fingerprint` | Stable per-peer identifier when a peer identity is known. |
| `session_form` | `start` or `continue` classification for the session proof. |
| `sender_role` | Sender-side protocol role from the session proof. |
| `local_role` | Receiver-side role derived from the session proof. |
| `replaced_active_incomplete` | `True` when a committed `open_envelope(...)` accepted a start-form that replaced an incomplete active lane. |
| `validation_stage` | Failure stage inside the `open_envelope(...)` or `verify_discovery_envelope(...)` pipeline. |
| `replay_store_mode` | Replay posture in effect on replay events: `memory`, `disk`, or `custom`. |
| `persist_replay` | Whether replay state is durable across restart. |
| `stream_mode` | Parsed stream mode, typically `single` or `stream`. |
| `stream_id` | Stream identifier from the session proof when present. |
| `stream_phase` | Stream phase such as `start`, `chunk`, or `end`. |
| `stream_seq` | Stream sequence number when present. |
| `stream_policy` | Stream verifier policy label. The built-in verifier currently uses `contiguous`. |
| `stream_reason` | Structured reason from stream interruption or verify logic. |
| `stream_ttl` | Stream TTL from the session proof when present. |
| `stream_expired` | Record-local expiry indicator derived from stream classification. |
| `stream_started_ts` | Known stream start timestamp when derivable at the emitter. |
| `stream_last_ts` | Most recent stream timestamp when derivable at the emitter. |
| `stream_frame_count` | Derived stream frame count when the runtime can infer it. |

Any optional key outside this whitelist is ignored by the event-merging logic.

### Practical rule

Treat the base keys as the stable decoding contract, and read optional keys defensively with `ctx.get(...)`.

## `open_envelope(...)` validation stages

`open_envelope(...)` carries the richest security signal, so the runtime also emits a `validation_stage` when relevant. The table below explains those stage names.

| Stage | Meaning |
| --- | --- |
| `structure` | Envelope shape or version failed before deeper validation. |
| `identity` | Sender or receiver identity validation failed. |
| `session` | Session continuity, TTL, or policy checks failed. |
| `signature` | Envelope signature verification failed. |
| `decrypt` | Payload decryption or decrypt preconditions failed. |
| `replay` | Replay detection rejected the message. |
| `commit` | State commit failed after validation succeeded. |

### Operational interpretation

* `structure` spikes usually indicate cheap malformed traffic.
* `signature` or `decrypt` spikes usually indicate more expensive invalid traffic.
* `commit` spikes often point to local storage or custom controls instability.

## Failure isolation

The runtime executes policy handlers inside a protected emission path.

If a handler raises:

* the runtime logs a warning,
* the lifecycle method's return value does not change,
* later handlers for the same phase still continue.

This keeps telemetry-plane bugs from breaking the data plane.

## Connecting telemetry to enforcement

Policy events are most useful when they feed your own verify or reset policy.

The usual pattern is:

1. update counters or reputation state in `on_policy_event(...)`,
2. key that state by `peer_fingerprint`,
3. read that state in a custom `verify_session`, `register_session`, or `reset_session` hook.

When you are inside a custom hook and still want baseline built-in behavior, use the public default delegates documented in [SummonerIdentity](identity.md) instead of re-entering the hook-aware runtime methods.

## What this API intentionally does not do

The policy event API does not:

* provide a registry or trust database by itself,
* guarantee that every optional field is always present,
* replace custom verify/reset policy,
* change core cryptographic semantics.

It is a structured observability API, not a standalone trust engine.

<p align="center">
  <a href="primitives.md">&laquo; Previous: Primitives and Version Constants</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="streaming.md">Next: Streaming &raquo;</a>
</p>
