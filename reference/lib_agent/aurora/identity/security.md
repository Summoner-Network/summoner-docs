# Security Notes (<code style="background: transparent;">Summoner<b>.aurora.identity</b></code>)

This page is the **public-facing security summary** for the identity API exposed from this module.

It is meant for SDK users, enterprise reviewers, and compliance readers who need to understand what this identity layer protects, what it assumes, and what it does not claim. It is not a formal certification artifact and it does not replace deployment-specific threat modeling.

## Threat model

### In scope

This identity layer is designed to defend against:

* passive eavesdroppers observing traffic,
* active network attackers who tamper with or replay messages,
* malicious peers attempting forgery or continuity abuse,
* storage corruption or key mismatches in the serialized identity/session state.

### Out of scope

This identity layer does not, by itself, solve:

* local host compromise or private-key theft,
* physical or side-channel attacks against cryptographic primitives,
* organizational identity proof such as PKI, HR directory proof, or legal-entity verification.

### Assumptions

This identity layer assumes:

* the underlying `cryptography` primitives are trustworthy,
* randomness sources are secure,
* private keys are stored with appropriate filesystem or password protection,
* clocks are not grossly wrong, or skew bounds are enforced in configuration.

## Security properties this identity layer provides

The table below summarizes the main protections this identity layer is designed to provide.

| Property | What the protocol does |
| --- | --- |
| Message integrity and authenticity | Envelopes are Ed25519-signed, so only the signing-key holder can produce a valid envelope for that identity. |
| Optional confidentiality | When `to` is present, payloads are AES-GCM encrypted using a symmetric key derived from X25519 plus identity-specific binding data. |
| Replay resistance | Session continuity plus replay-state checks reject duplicate or stale message use within the accepted policy window. |
| Continuity across sessions | `history_proof` can bind a new session start to prior conversation history. |
| Fingerprint-keyed peer tracking | Peer cache and built-in local session state are keyed by the signing-key fingerprint rather than display metadata. |

### Important scope note

`to=None` discovery envelopes are signed but not confidential. They are intended for public discovery or broadcast semantics, not for durable private peer continuity.

## What this identity layer does not claim

The limits below are just as important as the guarantees above, especially for security reviews and deployment planning.

| Non-goal or residual limit | Meaning |
| --- | --- |
| Real-world identity proof | A self-signed identity record proves internal consistency, not that the peer is the real-world entity named in `meta`. |
| Forward secrecy | Static identity keys are used by default, so later key compromise can expose previously recorded ciphertexts. |
| Safety after key theft | If an attacker steals the private identity file, they can act as that identity. |
| Transport-layer denial-of-service (DoS) resistance | Malformed or expensive traffic can still consume CPU and I/O before rejection. |
| Ordering-agnostic concurrency | Out-of-order or parallel replies are handled fail-closed for continuity, which preserves safety but can drop one side of a race. |

## Residual risks and recommended controls

The next table pairs common risks with the default protocol behavior and the control most users should add around it.

| Risk | Native behavior | Recommended control |
| --- | --- | --- |
| Real-world identity impersonation | Self-signatures verify but do not bind to an external authority. | Use a registry, trust on first use (TOFU), allowlists, public key infrastructure (PKI), or another external trust process. |
| Key compromise and no forward secrecy | Stolen static keys can decrypt past traffic and sign future envelopes. | Encrypt identity files, rotate keys, and use operational revocation workflows. |
| Reset abuse | Valid start-form messages can replace incomplete active state under accepted policy. | Monitor `replaced_active_incomplete`, add stricter verify/reset policy, and quarantine abusive peers. |
| Replay across restart | Replays may be re-accepted if replay state is not durable and the acceptance window is long. | Use `persist_replay=True` or a custom durable replay store, and keep TTLs bounded. |
| Concurrency or out-of-order delivery | The built-in verification preserves integrity by failing closed when continuity diverges. | Serialize per-peer turn usage or add application ordering discipline. |
| Invalid-envelope denial-of-service (DoS) | The runtime still performs parsing and validation work before rejection. | Add transport rate limits and use `validation_stage` telemetry to tune pre-crypto throttling. |

## Recommended deployment controls

If you are deciding what to do first in production, start with the controls below.

* Encrypt identity files in production and protect the decryption secret appropriately.
* Choose `ttl`, `margin`, and `max_clock_skew_seconds` for your real network conditions.
* Persist replay state for long-lived or restart-prone receivers.
* Treat fingerprint or pinned key identity as the trust anchor, not free-form `meta`.
* Feed [Policy Events](policy_events.md) into rate limits, reputation, and quarantine logic.
* Use [Streaming](streaming.md) limits if your deployment allows long-lived stream turns.

<details>
<summary>Streaming-specific security notes</summary>

Streaming adds stateful availability concerns on top of the base protocol. The table below highlights the most common ones.

| Stream abuse class | Native behavior | Recommended policy control |
| --- | --- | --- |
| Valid chunk keepalive without `end` | Valid chunks continue while continuity and `stream_ttl` remain valid. | Cap frames and wall-clock duration per `(peer_fingerprint, stream_id)`. |
| Gap-state pressure | The built-in verification is contiguous and rejects jumps. | Keep contiguous default, or tightly bound any custom gap tolerance. |
| Expensive-but-valid stream denial-of-service (DoS) | Valid stream frames still go through verify, decrypt, and commit work. | Add per-peer and per-stream rate limits. |
| Timeout or restart thrash | Closed streams move into interrupted state and later frames are rejected. | Add cooldowns and timeout counters in policy logic. |
| Post-timeout delayed frames | Old frames on closed streams return `stream_interrupted`. | Maintain closed-stream deny state when your storage is distributed. |
| Boolean-only verify hooks | Loss of structured stream error detail reduces observability. | Prefer structured verify results with explicit stream `code` and `reason`. |

</details>

## Related pages

* [Metadata and Continuity](metadata.md) explains why metadata changes do not equal key rotation.
* [Policy Events](policy_events.md) documents the telemetry you can use for detection and response.
* [Streaming](streaming.md) documents the stream-specific continuity and timeout rules.

<p align="center">
  <a href="streaming.md">&laquo; Previous: Streaming</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="metadata.md">Next: Metadata and Continuity &raquo;</a>
</p>
