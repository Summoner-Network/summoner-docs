# Summoner Agent Identity

This page defines the current **`id.v1` agent identity profile** used by `SummonerIdentity` and currently shipped in `summoner.aurora`.

If you only keep one idea from this page, keep this one:

> In this model, the portable agent ID is the signed public identity record itself. It is not a separate application label.

This companion page is meant to help three kinds of readers at once:

* SDK users who want to understand what an agent identity actually is,
* reviewers who need to know what is signed and what changes continuity,
* implementers who need the compatibility rules without reading the whole Aurora source tree.

For the runtime API, see [`SummonerIdentity`](identity/identity.md). For helper functions and version constants, see [Primitives and Version Constants](identity/primitives.md).

## What an agent ID is

In the current profile, an agent introduces itself with a signed public identity record like this:

```json
{
  "created_at": "2026-04-16T17:45:03+00:00",
  "pub_enc_b64": "<standard Base64 raw X25519 public key>",
  "pub_sig_b64": "<standard Base64 raw Ed25519 public key>",
  "meta": "<optional signed JSON value>",
  "sig": "<standard Base64 Ed25519 signature>",
  "v": "id.v1"
}
```

This object is the portable identity boundary for the current profile. It is the object exchanged between peers, embedded in envelopes, cached locally, and verified independently by another runtime.

The record tells a peer:

* when the identity was created,
* which public key is used for signatures,
* which public key is used for key agreement,
* which optional signed claims are attached in `meta`,
* and that the holder of the Ed25519 private key signed that claim set.

## Three related identity surfaces

The identity model is easiest to reason about when you separate these three surfaces.

| Surface | Purpose | Stable across `meta` changes? | Stable across signing-key rotation? |
| --- | --- | --- | --- |
| Public identity record | Portable identity exchanged between peers | No | No |
| Fingerprint | Short local index derived from `pub_sig_b64` | Yes | No |
| Local identity file | Private persistence container that stores the public record plus private keys | Usually yes | No |

The public identity record is the identity that travels between systems. The fingerprint is a local handle derived from that identity, and the local identity file is the private container that lets the same identity survive restarts.

## Current cryptographic profile

The current profile is intentionally small and explicit. Another implementation should treat the table below as a compatibility contract, not as an interchangeable recommendation.

| Purpose | Algorithm or format |
| --- | --- |
| Signing | Ed25519 |
| Key agreement | X25519 |
| Identity-file encryption | AES-256-GCM |
| Password-based key derivation | scrypt |
| Fingerprint hashing | SHA-256 |
| Text encoding | UTF-8 |
| Binary-to-text encoding | Standard Base64 with padding |

### Raw key format

Public and private keys are serialized in **raw 32-byte form** before Base64 encoding.

That detail matters for interoperability. A compatible implementation should not substitute PEM, DER, or other container formats when producing the fields below.

| Field or value | Raw length | Encoded form |
| --- | --- | --- |
| X25519 public key | 32 bytes | standard Base64 |
| X25519 private key | 32 bytes | standard Base64 |
| Ed25519 public key | 32 bytes | standard Base64 |
| Ed25519 private key | 32 bytes | standard Base64 |
| Ed25519 signature | 64 bytes | standard Base64 |

## What gets signed

The signature does **not** cover the final object verbatim. It covers the canonical JSON encoding of the public core:

```json
{
  "created_at": "...",
  "pub_enc_b64": "...",
  "pub_sig_b64": "...",
  "meta": "..."
}
```

Two rules are especially important:

* `sig` and `v` are added **after** signing.
* `meta` is included in the signed core only when it is present and non-null.

That means:

* omitting `meta` and setting `meta` to `null` are treated the same for signing,
* changing `meta` changes the signed public identity record,
* and another implementation must reconstruct the same public core to verify the record successfully.

### Canonical JSON rules

The signing bytes are the UTF-8 encoding of JSON serialized with:

* lexicographically sorted object keys,
* compact separators with no extra whitespace,
* standard JSON escaping,
* and the equivalent of `json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")` in the current Python reference.

For cross-language compatibility, avoid floats, non-string keys, implementation-specific map ordering, and other JSON forms that can serialize differently across runtimes.

## Fingerprint meaning

The current profile also defines a short fingerprint derived from `pub_sig_b64`.

It is computed by:

1. Base64-decoding `pub_sig_b64`,
2. hashing the raw Ed25519 public key with SHA-256,
3. Base64url-encoding the hash,
4. removing trailing `=`,
5. and taking the first 22 characters.

The fingerprint is useful for:

* peer and session indexing,
* local storage keys,
* audit references,
* and UI-sized identifiers.

It is **not** the full identity. A peer should still verify the signed public identity record, not just compare fingerprints.

For the public helper used by the SDK, see [`id_fingerprint(...)`](identity/primitives.md).

## Local identity file

The public identity record is portable. The local identity file is the private persistence artifact used by `id(...)`, `save_identity(...)`, and `load_identity(...)`.

The outer file version is also `id.v1`. Two storage modes exist:

| Mode | Shape | Typical use |
| --- | --- | --- |
| Plaintext private section | `{"v", "public", "private"}` | Development convenience only |
| Encrypted private section | `{"v", "public", "private_enc"}` | Preferred operational form |

### Plaintext private section

In plaintext mode, the file stores:

```json
{
  "v": "id.v1",
  "public": { "...": "public identity record" },
  "private": {
    "priv_enc_b64": "<standard Base64 raw X25519 private key>",
    "priv_sig_b64": "<standard Base64 raw Ed25519 private key>"
  }
}
```

### Encrypted private section

In encrypted mode, the file stores the public record in the clear and encrypts only the private payload:

```json
{
  "v": "id.v1",
  "public": { "...": "public identity record" },
  "private_enc": {
    "kdf": "scrypt",
    "kdf_params": { "n": 16384, "r": 8, "p": 1 },
    "salt": "<standard Base64 16-byte salt>",
    "nonce": "<standard Base64 12-byte AES-GCM nonce>",
    "aad": "c3VtbW9uZXIvaWRlbnRpdHlfZmlsZS92MQ==",
    "ciphertext": "<standard Base64 AES-GCM ciphertext>"
  }
}
```

The `aad` value above is the Base64 encoding of the literal UTF-8 bytes:

```text
summoner/identity_file/v1
```

For the SDK helpers that write and read these files, see [`save_identity(...)`](identity/primitives.md) and [`load_identity(...)`](identity/primitives.md).

## Identity change semantics

This table is the quickest way to understand which changes preserve continuity and which ones create a new identity boundary.

| Change | Same fingerprint? | Same public identity record? | Same continuity boundary? |
| --- | --- | --- | --- |
| Update `meta` only | Yes | No | Yes |
| Update `created_at` only | Yes | No | No; this should not happen for a stable identity |
| Rotate Ed25519 signing key | No | No | No |
| Rotate X25519 encryption key only | Yes | No | No |
| Rotate both keys | No | No | No |

For stable identity lifecycle:

* `created_at` should be written once and then preserved,
* `meta` may evolve over time,
* key rotation should be treated as a deliberate identity-boundary event unless you have a higher-level migration story around it.

For the longer explanation of how `meta` affects continuity without changing the fingerprint, see [Metadata and Continuity](identity/metadata.md).

## Minimum compatibility checklist

An implementation is compatible with the current profile only if it does all of the following:

* generates raw 32-byte X25519 and Ed25519 key material,
* serializes public keys as standard Base64 of raw bytes,
* signs only the canonical public core,
* uses `id.v1` exactly as the public identity record version,
* omits `meta` from the signed core when it is absent or null,
* verifies the Ed25519 signature against the canonical public core,
* derives fingerprints from `pub_sig_b64` exactly as specified,
* reads and writes local identity files with outer `v == "id.v1"`,
* uses the same AES-GCM associated-data literal for encrypted identity files,
* and rejects unsupported versions rather than silently accepting them.

## Related pages

* [SummonerIdentity](identity/identity.md) documents the runtime API that loads identities and uses them for sessions and envelopes.
* [Primitives and Version Constants](identity/primitives.md) documents the helper functions and compatibility constants behind the profile.
* [Metadata and Continuity](identity/metadata.md) explains why metadata updates do not change the fingerprint or continuity boundary by themselves.
* [Security Notes](identity/security.md) explains the security guarantees and limits of the broader identity runtime.

<p align="center">
  <a href="../aurora.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.aurora</b></code></a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="identity/index.md">Next: <code style="background: transparent;">Summoner<b>.aurora.identity</b></code> &raquo;</a>
</p>
