# Streaming (<code style="background: transparent;">Summoner<b>.aurora.identity</b></code>)

This page explains **stream mode** in the identity API.

Streaming extends the normal session proof model so one sender can emit multiple frames during the same turn without giving up the continuity and replay guarantees of the base protocol.

This page focuses only on the stream-specific layer. For the general identity API, see [SummonerIdentity](identity.md).

## Import path

```python
from summoner.aurora import SummonerIdentity
```

## Stream model

Stream mode is turn-owned and phase-based:

1. a stream starts with `phase="start"` and `seq=0`,
2. zero or more `chunk` frames extend the same sender turn,
3. an `end` frame closes the stream and hands control back to the normal session TTL contract.

### Timing model

* Non-end stream frames are governed by `stream_ttl`.
* End frames are governed by normal session `ttl`.
* Stream mode is not supported for public discovery flows such as `to=None`.

## Stream-specific session fields

Stream mode extends the normal `session_proof` with three extra fields. The table below shows the role of each one.

| Field | Rule |
| --- | --- |
| `mode` | `single` or `stream` |
| `stream` | Required when `mode="stream"` and must contain `id`, `seq`, and `phase` |
| `stream_ttl` | Required on non-end stream frames; omitted on stream end; forbidden in single mode |

Representative shape:

```json
{
  "sender_role": 1,
  "0_nonce": "<hex>",
  "1_nonce": "<hex>",
  "ts": 1730000000,
  "ttl": 120,
  "history_proof": null,
  "age": 0,
  "mode": "stream",
  "stream": {
    "id": "a1b2c3d4e5f6a7b8",
    "seq": 0,
    "phase": "start"
  },
  "stream_ttl": 60
}
```

The method that interprets these fields for you is `classify_session_record(...)`.

## `SummonerIdentity.start_session`

```python
async def start_session(
    self,
    peer_public_id: Optional[dict] = None,
    ttl: Optional[int] = None,
    stream: bool = False,
    stream_ttl: Optional[int] = None,
    *,
    force_reset: bool = False,
    return_status: bool = False,
) -> Any
```

### Stream-specific behavior

When `stream=True`, `start_session(...)` creates a stream-start proof:

* `mode="stream"`
* `stream={"id": <generated>, "seq": 0, "phase": "start"}`
* `stream_ttl=<positive int>`

### Important rules

* Stream start requires `peer_public_id`.
* Missing or invalid `stream_ttl` returns `stream_ttl_invalid`.
* Requesting stream mode on a discovery/public boundary returns `stream_mode_unsupported`.

### Inputs

* `peer_public_id`: required for stream mode.
* `stream`: must be `True` to enter stream mode.
* `stream_ttl`: required positive timeout for the start frame.
* `return_status`: when `True`, returns the structured lifecycle status instead of the created session record.

### Outputs

* Default return: the created stream-start session record on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* May propagate public-identity validation errors when `peer_public_id` is malformed.
* Common failure codes include `stream_mode_unsupported`, `stream_ttl_invalid`, `active_session_exists`, `force_reset_failed`, and `register_session_failed`.

## `SummonerIdentity.continue_session`

```python
async def continue_session(
    self,
    peer_public_id: Optional[dict],
    peer_session: dict,
    ttl: Optional[int] = None,
    use_margin: bool = True,
    *,
    stream: bool = False,
    stream_ttl: Optional[int] = None,
    return_status: bool = False,
) -> Any
```

### Stream-specific behavior

When `stream=True`, `continue_session(...)` starts a responder-owned stream turn:

* `mode="stream"`
* `phase="start"`
* `seq=0`

### Important rules

* If a local stream is already active, non-stream `continue_session(...)` is blocked with `stream_active_continue_blocked`.
* Stream start requires a positive `stream_ttl`.
* Stream mode on a public/discovery boundary returns `stream_mode_unsupported`.
* If the current link is stale or missing, role `0` may recover through `start_session(...)`, while role `1` fails closed.

### Inputs

* `peer_public_id`: required for durable per-peer stream continuity.
* `peer_session`: inbound session proof being answered.
* `stream`: must be `True` to begin a responder-owned stream turn.
* `stream_ttl`: required positive timeout for the start frame.
* `return_status`: when `True`, returns the structured lifecycle status instead of the reply session record.

### Outputs

* Default return: the next stream-start session record on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* May propagate public-identity validation errors when `peer_public_id` is malformed.
* Common failure codes include `invalid_peer_session`, `stream_mode_unsupported`, `stream_ttl_invalid`, `stream_active_continue_blocked`, `missing_or_expired_current_link`, `peer_session_mismatch`, `peer_sender_role_mismatch`, and `register_session_failed`.

## `SummonerIdentity.advance_stream_session`

```python
async def advance_stream_session(
    self,
    peer_public_id: Optional[dict],
    session: dict,
    *,
    end_stream: bool = False,
    ttl: Optional[int] = None,
    stream_ttl: Optional[int] = None,
    return_status: bool = False,
) -> Any
```

### Behavior

Advances an active stream for the same sender role.

The method requires:

* a valid stream-mode input session,
* a peer identity,
* an active matching stream in store.

### Progression rules

* The runtime increments `seq` by exactly `+1`.
* `end_stream=False` emits a `chunk` frame and requires a positive `stream_ttl`.
* `end_stream=True` emits an `end` frame, applies the normal handoff `ttl`, and stores `stream_ttl=None` in the generated end frame.

### Inputs

* `peer_public_id`: required and must match the active stream lane.
* `session`: current stream-mode session record being advanced.
* `end_stream`: selects `chunk` versus `end`.
* `stream_ttl`: required for non-end frames.
* `ttl`: normal handoff TTL used when `end_stream=True`.
* `return_status`: when `True`, returns the structured lifecycle status instead of the next session record.

### Outputs

* Default return: the next stream session record on success, otherwise `None`.
* With `return_status=True`: a structured status object containing `ok`, `code`, `phase`, and optional `data`.

### Error handling

* Raises `ValueError` if `id(...)` has not been called yet.
* May propagate public-identity validation errors when `peer_public_id` is malformed.
* Common failure codes include `stream_mode_unsupported`, `invalid_stream_session`, `stream_ttl_invalid`, `stream_not_active`, `stream_interrupted`, and `register_session_failed`.

## Stream guards in `seal_envelope(...)` and `open_envelope(...)`

### `seal_envelope(...)`

Before signing or encrypting, `seal_envelope(...)` validates:

* `mode` is one of the supported values,
* stream objects are structurally valid,
* non-end stream frames carry valid `stream_ttl`,
* stream mode is not used on unsupported boundaries such as `to=None`.

### `open_envelope(...)`

On receive, `open_envelope(...)` preserves the normal validation order and adds stream-aware rules:

* continuity verification understands `stream_id`, `stream_phase`, and `stream_seq`,
* the first responder boundary still respects the requester's `ttl`,
* later `chunk` frames are governed by `stream_ttl`,
* timeout or interruption closes the local stream state.

## Stream invariants

The built-in verification follows a strict contiguous stream policy. The table below shows which transitions are accepted.

| Current state | Next frame | Allowed | Failure code on reject |
| --- | --- | --- | --- |
| no active stream | `start(seq=0)` | Yes | - |
| no active stream | `chunk` or `end` | No | `stream_not_active` or `stream_interrupted` |
| active `start(seq=n)` | `chunk` or `end(seq=n+1)` | Yes | - |
| active `chunk(seq=n)` | `chunk` or `end(seq=n+1)` | Yes | - |
| active stream | repeated `start` | No | `stream_already_active` |
| active stream `id=A` | frame with `id=B` | No | `stream_state_conflict` |
| active stream | invalid phase progression | No | `stream_phase_invalid` |
| active stream | non-contiguous sequence | No | `stream_seq_invalid` |

Minimal valid progression:

```python
# inside an async function / handler
s1 = await bob.continue_session(pub_a, env0["session_proof"], stream=True, stream_ttl=30)
s2 = await bob.advance_stream_session(pub_a, s1, end_stream=False, stream_ttl=30)
s3 = await bob.advance_stream_session(pub_a, s2, end_stream=True, ttl=120)
```

## Timeout and persistence behavior

The table below summarizes the timing rules that matter most when you run stream mode in production.

| Rule | Meaning |
| --- | --- |
| Progress window | Non-end stream frames must satisfy `now <= ts + stream_ttl`. |
| Handoff window | End frames use normal session `ttl`. |
| Receiver margin | Stream timeout verification does not use `margin` for non-end frames. |
| First responder boundary | The requester TTL is enforced at the first stream boundary, not on every later chunk. |
| Closed stream behavior | Timeout or interruption closes the local stream and later frames on that stream return `stream_interrupted`. |

<details>
<summary>Built-in local store fields to preserve in custom storage hooks</summary>

If you replace the built-in local store with custom hooks, the safest path is to preserve these current-link stream fields:

| Field | Purpose |
| --- | --- |
| `stream_mode` | Tracks whether the current link is single-message or stream-mode. |
| `stream_id` | Active or closed stream identifier. |
| `stream_phase` | Last accepted stream phase. |
| `expected_next_seq` | Contiguous sequence validator state. |
| `stream_active` | Active vs closed marker. |
| `stream_last_ts` | Timestamp of the last accepted stream frame. |
| `stream_ttl` | Last accepted stream timeout value. |
| `missing_ranges` | Reserved field for optional gap-tolerant policies. |
| `stream_reason` | Optional interruption or closure reason. |

</details>

## Stream status codes

When a stream-specific check fails, the runtime returns one of the status codes below.

| Code | Typical method/phase | Meaning |
| --- | --- | --- |
| `invalid_stream_mode` | `seal_envelope`, `open_envelope` | Unsupported `mode` value. |
| `invalid_stream_fields` | `seal_envelope`, `open_envelope` | Stream object or shape is invalid. |
| `invalid_stream_session` | `advance_stream_session` | Input session is not valid stream context. |
| `stream_mode_unsupported` | `start_session`, `continue_session`, `advance_stream_session`, `seal_envelope`, `open_envelope` | Stream requested or received on an unsupported boundary. |
| `stream_ttl_invalid` | multiple phases | Missing or invalid non-end `stream_ttl`. |
| `stream_ttl_expired` | `open_envelope` | Inbound non-end frame exceeded `ts + stream_ttl`. |
| `stream_phase_invalid` | `open_envelope` | Invalid phase transition for the current stream state. |
| `stream_seq_invalid` | `open_envelope` | Sequence is not contiguous with the expected next state. |
| `stream_state_conflict` | `open_envelope` | Stream id conflicts with persisted active state. |
| `stream_not_active` | `open_envelope`, `advance_stream_session` | Non-start progression attempted without an active stream. |
| `stream_already_active` | `open_envelope` | New stream start conflicts with an already active stream. |
| `stream_active_continue_blocked` | `continue_session` | Non-stream continue was attempted while a local stream is active. |
| `stream_interrupted` | `open_envelope`, `advance_stream_session` | Frame targets a closed or interrupted stream, or advance used mismatched stream state. |

## Stream telemetry

Streaming adds the extra policy-event fields below on top of the general event format documented in [Policy Events](policy_events.md).

| Field | Meaning |
| --- | --- |
| `stream_mode` | Parsed mode, usually `single` or `stream`. |
| `stream_id` | Stream identifier from the session proof. |
| `stream_phase` | Stream phase from the session proof. |
| `stream_seq` | Stream sequence number. |
| `stream_policy` | Verifier policy label. The built-in verifier currently emits `contiguous`. |
| `stream_reason` | Structured stream interruption or verify reason. |
| `stream_ttl` | Stream timeout value when present. |
| `stream_expired` | Record-local expiry hint. |
| `stream_started_ts` | Start timestamp when derivable. |
| `stream_last_ts` | Most recent frame timestamp when derivable. |
| `stream_frame_count` | Derived frame count when the runtime can infer it. |

### Practical note

If you write a custom `verify_session` hook and want precise stream telemetry, prefer structured verify results such as `{"ok": False, "code": "stream_ttl_expired", "reason": "..."}`. A plain boolean `False` collapses to the generic `session_verify_failed`.

<p align="center">
  <a href="policy_events.md">&laquo; Previous: Policy Events</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="security.md">Next: Security Notes &raquo;</a>
</p>
