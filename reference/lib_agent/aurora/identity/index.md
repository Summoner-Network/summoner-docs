# <code style="background: transparent;">Summoner<b>.aurora.identity</b></code> (Aurora v1.0.0)

This page introduces the **`SummonerIdentity` and `SummonerIdentityControls` API, along with the related helper functions collected under `Summoner.aurora.identity`**. Start here when you want the big picture before moving into the class and helper references for sessions, envelopes, controls, telemetry, streaming, security, and metadata continuity.

If you want the identity model itself before the runtime API, start with [Summoner Agent Identity](../agent_identity.md). That page explains what the portable agent ID is, how it differs from a fingerprint or local identity file, and which changes do or do not preserve continuity.

This identity API is easiest to read in three layers:

* `SummonerIdentity` is the runtime engine for identity files, sessions, envelopes, replay checks, and peer tracking.
* `SummonerIdentityControls` is the reusable per-identity hook package for custom storage or trust rules.
* `summoner.aurora.identity` exports public primitives for signatures, identity files, continuity hashing, and key derivation.

## Import paths

Typical imports from the composed SDK are:

```python
from summoner.aurora import SummonerIdentity, SummonerIdentityControls
from summoner.aurora.identity import (
    ID_VERSION,
    id_fingerprint,
    load_identity,
    save_identity,
    verify_public_id,
)
```

`SummonerIdentity` and `SummonerIdentityControls` are also re-exported from `summoner.aurora`, but this page groups the related API under `summoner.aurora.identity` so the identity material stays together.

## Identity model at a glance

Before diving into methods, separate the three identity artifacts that this module keeps distinct. This makes the session, metadata, and review pages much easier to read.

| Artifact | What it is | Where you see it |
| --- | --- | --- |
| Public identity record | Self-signed JSON identity exchanged between peers | `public_id`, envelopes, peer caches |
| Fingerprint | Short local identifier derived from `pub_sig_b64` | `id_fingerprint(...)`, peer/session keys, audit references |
| Local identity file | Private file that stores the public record plus private keys | `id(...)`, `save_identity(...)`, `load_identity(...)` |

The public identity record is the portable identity. The fingerprint is a convenient local index, and the local identity file is the private container that lets the same identity survive restarts.

The self-signature proves that the public record is internally consistent. It does not, by itself, prove real-world identity or external directory authority. For that layer, pair the identity layer with your own trust process or registry.

## Typical Workflow

Most applications use the identity workflow in this order:

1. Create or load a local identity with `SummonerIdentity.id(...)`.
2. Optionally attach reusable controls with `SummonerIdentity.attach_controls(...)`.
3. Start or continue a session, then build signed envelopes.
4. Open inbound envelopes and let the runtime update replay and peer state.
5. Add policy telemetry, streaming, or metadata-specific rules only where needed.

## Pick the right page

If you are learning this identity API for the first time, this table is the fastest way to find the right starting point.

| You want to… | Go to |
| --- | --- |
| Understand what the portable agent identity actually is | [Summoner Agent Identity](../agent_identity.md) |
| Use the main identity/session/envelope engine | [`SummonerIdentity`](identity.md) |
| Attach reusable per-identity hooks | [`SummonerIdentityControls`](controls.md) |
| Use low-level helpers or inspect public version constants | [Primitives and Version Constants](primitives.md) |
| Observe lifecycle outcomes through structured telemetry | [Policy Events](policy_events.md) |
| Work with multi-frame stream continuity | [Streaming](streaming.md) |
| Review user-facing security guarantees and limits | [Security Notes](security.md) |
| Understand how `meta` affects continuity and fingerprints | [Metadata and Continuity](metadata.md) |

## What Each Identity Page Covers

The list below gives a little more context about the role of each page in the identity reference.

* [Summoner Agent Identity](../agent_identity.md) explains the current `id.v1` identity profile, including the public identity record, the fingerprint, the local identity file, and the main continuity rules.
* [SummonerIdentity](identity.md) documents the public class used to load identities, track continuity, and seal/open envelopes.
* [SummonerIdentityControls](controls.md) documents the per-identity controls API for custom session, replay, and peer-key handling.
* [Primitives and Version Constants](primitives.md) documents the exported helper functions and compatibility constants.
* [Policy Events](policy_events.md) is the dedicated page for lifecycle telemetry emitted from identity methods.
* [Streaming](streaming.md) is the dedicated page for stream-mode session proofs and `advance_stream_session(...)`.
* [Security Notes](security.md) is the dedicated page for the front-facing security model and operational cautions.
* [Metadata and Continuity](metadata.md) is the dedicated page for how `meta` changes affect signatures, fingerprints, and continuity.

This reference intentionally excludes maintainer-only material such as version-bump policy, migration playbooks, internal test scaffolding, and low-level implementation notes that are useful for the Summoner team but not necessary for SDK users or external reviewers.

<p align="center">
  <a href="../agent_identity.md">&laquo; Previous: Summoner Agent Identity</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="identity.md">Next: <code>SummonerIdentity</code> &raquo;</a>
</p>
