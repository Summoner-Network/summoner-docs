# Metadata and Continuity (<code style="background: transparent;">Summoner<b>.aurora.identity</b></code>)

This page explains how **`meta`** interacts with the public identity record, fingerprints, and continuity.

The short version is:

* `meta` is part of the signed public identity record,
* `meta` does not affect `id_fingerprint(...)`,
* metadata changes do not break continuity as long as the same keys remain in use.

That distinction is especially important for enterprise integrations where directory or governance data needs to evolve without forcing a new cryptographic identity every time a label changes.

## Import path

```python
from summoner.aurora import SummonerIdentity
from summoner.aurora.identity import id_fingerprint
```

## What `meta` is

A public identity record contains:

* `created_at`
* `pub_enc_b64`
* `pub_sig_b64`
* optional `meta`
* `sig`
* `v`

`meta` is an optional **signed metadata field**. It is intended for application or enterprise claims that should travel with the public identity record.

Typical examples:

* tenant or environment labels,
* directory identifiers,
* workload class labels,
* governance or policy profile references,
* human-readable agent labels.

## What `meta` changes and what it does not change

The table below is the quickest way to understand which parts of the identity model are affected by metadata changes and which parts are not.

| Surface | Affected by `meta`? | Why |
| --- | --- | --- |
| `verify_public_id(...)` | Yes | `meta` is part of the signed public claim set when present. |
| `sig` on the public identity record | Yes | Changing `meta` requires re-signing the public identity. |
| `id_fingerprint(pub_sig_b64)` | No | The fingerprint is derived from the signing public key only. |
| Fallback peer-cache key | No | Peer records are keyed by the signing-key fingerprint. |
| Fallback session-store key | No | Session lanes are keyed by the same fingerprint identity. |
| Payload and history-proof direction binding | No | Those bindings use identity fingerprints, not `meta`. |
| Session key agreement | No | Session derivation is bound to keys and direction data, not metadata text. |
| Continuity history | No | Continuity is anchored to the same peer fingerprint and lane state. |
| Envelope signature | Indirectly yes | The `from` identity object changes, so the signed envelope content changes too. |

## Why `id_fingerprint(...)` stays stable

The fingerprint is derived from the Ed25519 signing public key bytes only.

That means:

* changing `meta` does not change the fingerprint,
* changing the self-signature does not change the fingerprint,
* changing `created_at` does not change the fingerprint,
* changing the signing key does change the fingerprint.

In practice, the fingerprint is the stable local identifier for the cryptographic signer, not for the entire JSON shape of the public record.

## Why continuity is preserved when `meta` changes

Continuity is bound to keys and fingerprinted direction, not to the current contents of `meta`.

The important anchors are:

* peer caches keyed by `id_fingerprint(pub_sig_b64)`,
* session lanes keyed by the same fingerprint,
* payload authenticated additional data (AAD) bound to `from` and `to` fingerprints,
* `history_proof` authenticated additional data (AAD) bound to the same directional fingerprints,
* session-key derivation bound to key material plus direction and session fields.

So when an agent keeps the same `pub_sig_b64` and `pub_enc_b64` but updates only `meta`, peers can keep treating it as the same cryptographic identity with refreshed signed claims.

## What peers observe after a metadata change

Peers will usually observe:

1. the `from` identity object in later envelopes contains the updated `meta`,
2. the self-signature on that public identity record changes,
3. the peer cache entry keyed by fingerprint can be refreshed in place,
4. the fingerprint itself stays the same.

So a peer that tracks whole `public_id` objects sees the record change, while a peer that tracks by fingerprint still sees the same underlying identity.

## Enterprise meaning and limits

The right mental model is:

> `meta` is a signed claim set attached to an identity, not the root identity itself.

That is useful because it allows a stable key-based identity to carry evolving external references such as:

* IAM subject identifiers,
* tenant or region labels,
* compliance profile references,
* deployment channel information.

But `meta` alone does **not** prove that an external directory, tenant, or governance system agrees with that claim. If you need authoritative enterprise binding, validate signed identities through your own registry or trust process.

## Practical scenarios

### Add an enterprise identifier

Adding a tenant id or directory id changes the signed public record, but not the fingerprint or continuity boundary.

### Remove or revise metadata

Removing a display label or changing governance fields still preserves continuity as long as the same keys remain in use.

### Per-process override during send

`seal_envelope(..., id_meta=...)` lets one running process update the in-memory public identity used for that process without immediately rewriting the identity file on disk.

```python
envelope = await identity.seal_envelope(
    payload,
    session,
    to=peer_public_id,
    id_meta={"tenant_id": "contoso-eu-prod", "deployment_channel": "blue"},
)
```

For a durable metadata change, use `update_id_meta(...)` or call `id(..., meta=...)` when initializing the identity file.

### Key rotation contrast

If `pub_sig_b64` or `pub_enc_b64` changes, that is not a metadata update anymore. It is a new cryptographic identity boundary and should be treated as rotation.

## Recommended enterprise patterns

* Use the fingerprint or pinned signing key as the primary key in registries and audit systems.
* Treat `meta` as signed enrichment that can be refreshed over time.
* Allow metadata refresh without forcing continuity reset when the underlying keys are unchanged.
* Treat signing-key change as a new identity boundary, even if the human-readable metadata looks familiar.
* Combine the identity layer with registry, allowlist, or directory validation if `meta` must be authoritative.

<p align="center">
  <a href="security.md">&laquo; Previous: Security Notes</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="index.md">Next: <code style="background: transparent;">Summoner<b>.aurora.identity</b></code> &raquo;</a>
</p>
