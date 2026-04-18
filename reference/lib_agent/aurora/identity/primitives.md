# Primitives and Version Constants (<code style="background: transparent;">Summoner<b>.aurora.identity</b></code> )

This page documents the **public helper functions and version constants** exported by `summoner.aurora.identity`.

For most SDK users, these helpers sit behind `SummonerIdentity.id(...)`, `seal_envelope(...)`, and `open_envelope(...)`. They are still part of the public API when you need low-level control over identity files, signatures, continuity hashes, or compatibility checks.

## Import path

```python
from summoner.aurora.identity import (
    ENV_VERSION,
    HISTORY_PROOF_VERSION,
    ID_VERSION,
    IDENTITY_CONTROLS_VERSION,
    PAYLOAD_ENC_VERSION,
    PEER_KEYS_STORE_VERSION,
    REPLAY_STORE_VERSION,
    SESSIONS_STORE_VERSION,
    b64_decode,
    b64_encode,
    derive_history_proof_key,
    derive_payload_key,
    derive_sym_key,
    hist_next,
    id_fingerprint,
    load_identity,
    save_identity,
    serialize_public_key,
    session_summary,
    sign_bytes,
    sign_public_id,
    verify_bytes,
    verify_public_id,
)
```

## When to use these helpers directly

Most applications should prefer the higher-level class methods on `SummonerIdentity`.

Reach for the low-level helpers when you need to:

* assert public format versions at an API boundary,
* inspect or manage identity files outside the normal class lifecycle,
* validate or fingerprint a public identity record before binding it into another system,
* build tooling around continuity hashes or key derivation.

## Version constants

If you need to audit compatibility or inspect stored data, start with the constants below. They identify the format/version markers that appear on the wire or in the built-in local store files exposed by this module.

| Constant | Current value | Identifies |
| --- | --- | --- |
| `ID_VERSION` | `"id.v1"` | Signed public identity record format |
| `ENV_VERSION` | `"env.v1"` | Envelope format produced by `seal_envelope(...)` and consumed by `open_envelope(...)` |
| `PAYLOAD_ENC_VERSION` | `"payload.enc.v1"` | Payload encryption object format |
| `HISTORY_PROOF_VERSION` | `"histproof.v1"` | `history_proof` encryption object format |
| `SESSIONS_STORE_VERSION` | `"sessions.store.v1"` | Wrapped built-in local session-store document format |
| `PEER_KEYS_STORE_VERSION` | `"peer_keys.store.v1"` | Wrapped built-in local peer-key-store document format |
| `REPLAY_STORE_VERSION` | `"replay.store.v1"` | Wrapped built-in local replay-store document format |
| `IDENTITY_CONTROLS_VERSION` | `"aurora.identity.controls.v1"` | Public controls API version |

In normal application code, prefer `SummonerIdentity.store_versions()` and `SummonerIdentity.controls_version()` when you want a compact runtime compatibility report.

## Public identity record

If you exchange or verify public identity records outside `SummonerIdentity`, keep the public record contract below in mind.

| Field | Meaning |
| --- | --- |
| `created_at` | Identity creation timestamp |
| `pub_enc_b64` | X25519 public key used for key agreement |
| `pub_sig_b64` | Ed25519 public key used for signatures |
| `meta` | Optional signed metadata claims |
| `sig` | Ed25519 signature over the canonical public core |
| `v` | Identity format version, currently `id.v1` |

`sign_public_id(...)` signs the public core and then adds `sig` and `v`. `id_fingerprint(...)` is not the full identity; it is a short local index derived from `pub_sig_b64`.

### Interoperability notes

The identity format uses Ed25519 for signatures and X25519 for key agreement. Public and private keys are serialized in raw 32-byte form before standard base64 encoding. The signed public core is canonicalized as sorted, compact JSON, and `meta` participates in the signature only when it is present and non-null.

## `b64_encode`

```python
def b64_encode(data: bytes) -> str
```

### Behavior

Encodes raw bytes using standard base64 and returns a UTF-8 string.

This helper is used for portable storage of keys, nonces, ciphertexts, and signatures.

### Inputs

#### `data`

* **Type:** `bytes`
* **Meaning:** Raw bytes to encode.

### Outputs

Returns the base64-encoded UTF-8 string.

## `b64_decode`

```python
def b64_decode(data: str) -> bytes
```

### Behavior

Decodes a standard base64 string into raw bytes.

This is the inverse of `b64_encode(...)`.

### Inputs

#### `data`

* **Type:** `str`
* **Meaning:** Base64 string to decode.

### Outputs

Returns the decoded raw bytes.

## `serialize_public_key`

```python
def serialize_public_key(key: Any) -> str
```

### Behavior

Serializes an X25519 or Ed25519 public key to raw bytes and base64-encodes the result.

This helper is used for the public key fields stored inside signed public identity records.

### Inputs

#### `key`

* **Type:** `Any`
* **Meaning:** Public key object to serialize.

### Outputs

Returns the raw public key bytes encoded as standard base64.

## `sign_bytes`

```python
def sign_bytes(
    priv_sign: ed25519.Ed25519PrivateKey,
    data: bytes,
) -> str
```

### Behavior

Signs raw bytes with Ed25519 and returns a base64 signature.

When you are signing structured identity objects, prefer the higher-level helpers such as `sign_public_id(...)` or the envelope methods on `SummonerIdentity` rather than re-creating the canonicalization rules by hand.

### Inputs

#### `priv_sign`

* **Type:** `ed25519.Ed25519PrivateKey`
* **Meaning:** Private signing key used to generate the signature.

#### `data`

* **Type:** `bytes`
* **Meaning:** Exact bytes to sign.

### Outputs

Returns the Ed25519 signature encoded as standard base64.

## `verify_bytes`

```python
def verify_bytes(
    pub_sign_b64: str,
    data: bytes,
    sig_b64: str,
) -> None
```

### Behavior

Verifies an Ed25519 signature against the exact bytes that were signed.

Returns `None` on success and raises on failure.

### Inputs

#### `pub_sign_b64`

* **Type:** `str`
* **Meaning:** Base64-encoded Ed25519 public key.

#### `data`

* **Type:** `bytes`
* **Meaning:** Exact bytes that should have been signed.

#### `sig_b64`

* **Type:** `str`
* **Meaning:** Base64-encoded signature to verify.

### Outputs

Returns `None` when the signature is valid.

### Error handling

Raises if the public key or signature is invalid, or if the signature does not match `data`.

## `sign_public_id`

```python
def sign_public_id(
    priv_sig: ed25519.Ed25519PrivateKey,
    pub: dict,
) -> dict
```

### Behavior

Builds a self-signed public identity record.

The input `pub` should contain the public identity core:

* `created_at`
* `pub_enc_b64`
* `pub_sig_b64`
* optional `meta`

The function returns a signed record that includes:

* `v: ID_VERSION`
* `sig`

If `meta` is present and non-null, it is part of the signed public claim set.

### Inputs

#### `priv_sig`

* **Type:** `ed25519.Ed25519PrivateKey`
* **Meaning:** Private signing key used to sign the public identity record.

#### `pub`

* **Type:** `dict`
* **Meaning:** Public identity core to sign.

### Outputs

Returns the signed public identity record.

## `verify_public_id`

```python
def verify_public_id(pub: dict) -> None
```

### Behavior

Verifies a self-signed public identity record created by `sign_public_id(...)`.

Use this before trusting the peer's:

* `pub_enc_b64` for key agreement,
* `pub_sig_b64` for signature verification,
* signed `meta` claims.

Returns `None` on success and raises on failure.

### Inputs

#### `pub`

* **Type:** `dict`
* **Meaning:** Signed public identity record to validate.

### Outputs

Returns `None` when the record is valid.

### Error handling

Raises if the record shape, version, or self-signature is invalid.

## `id_fingerprint`

```python
def id_fingerprint(pub_sig_b64: str) -> str
```

### Behavior

Returns a short stable identifier derived from the Ed25519 signing public key.

This value is used as the stable local identity key for peer caches and built-in local session storage.

### Important note

`id_fingerprint(...)` is a local indexing primitive, not a cryptographic proof of who the peer is. It is derived from `pub_sig_b64` only, so metadata changes do not change the fingerprint.

### Inputs

#### `pub_sig_b64`

* **Type:** `str`
* **Meaning:** Base64-encoded Ed25519 signing public key.

### Outputs

Returns the short fingerprint string derived from that signing key.

## `save_identity`

```python
def save_identity(
    path: str,
    *,
    priv_enc: x25519.X25519PrivateKey,
    priv_sig: ed25519.Ed25519PrivateKey,
    meta: Optional[Any] = None,
    password: Optional[bytes] = None,
    scrypt_n: int = 2**14,
    scrypt_r: int = 8,
    scrypt_p: int = 1,
) -> dict
```

### Behavior

Writes an identity file containing:

* a self-signed public identity record,
* the private encryption key,
* the private signing key.

If `password is None`, the function stores the private section as plaintext base64. If `password` is provided, it encrypts the private section with scrypt plus AES-GCM.

Writes are atomic, and the function returns the signed public identity record.

### Inputs

#### `path`

* **Type:** `str`
* **Meaning:** File path where the identity document should be written.

#### `priv_enc`

* **Type:** `x25519.X25519PrivateKey`
* **Meaning:** Private key used for key agreement.

#### `priv_sig`

* **Type:** `ed25519.Ed25519PrivateKey`
* **Meaning:** Private key used for signatures.

#### `meta`

* **Type:** `Optional[Any]`
* **Meaning:** Optional metadata to include in the signed public identity record.
* **Default:** `None`

#### `password`

* **Type:** `Optional[bytes]`
* **Meaning:** Optional password used to encrypt the private section.
* **Default:** `None`

#### `scrypt_n`

* **Type:** `int`
* **Meaning:** Scrypt work factor `n` when password-based encryption is used.
* **Default:** `2**14`

#### `scrypt_r`

* **Type:** `int`
* **Meaning:** Scrypt block size parameter `r`.
* **Default:** `8`

#### `scrypt_p`

* **Type:** `int`
* **Meaning:** Scrypt parallelization parameter `p`.
* **Default:** `1`

### Outputs

Returns the signed public identity record written to disk.

## `load_identity`

```python
def load_identity(
    path: str,
    *,
    password: Optional[bytes] = None,
) -> tuple[dict, x25519.X25519PrivateKey, ed25519.Ed25519PrivateKey]
```

### Behavior

Loads an identity file produced by `save_identity(...)`, validates the signed public identity record, and returns:

* `public_id`
* `priv_enc`
* `priv_sig`

If the private section is encrypted, the correct password is required.

### Inputs

#### `path`

* **Type:** `str`
* **Meaning:** Identity-file path to load.

#### `password`

* **Type:** `Optional[bytes]`
* **Meaning:** Optional password required when the private section is encrypted.
* **Default:** `None`

### Outputs

Returns a tuple of:

* `public_id`
* `priv_enc`
* `priv_sig`

### Error handling

Raises if the file format is unsupported, the public identity record is invalid, or an encrypted file requires a missing or incorrect password.

## `session_summary`

```python
def session_summary(lnk: dict) -> bytes
```

### Behavior

Computes the domain-separated digest for one completed continuity link.

This digest is used when completed exchanges are finalized into the rolling history chain.

### Inputs

#### `lnk`

* **Type:** `dict`
* **Meaning:** Completed continuity link to summarize.

### Outputs

Returns the domain-separated summary digest as raw bytes.

### Error handling

Raises `ValueError` if the link does not contain the required nonce and timing fields.

## `hist_next`

```python
def hist_next(
    prev_hash_hex: Optional[str],
    summary: bytes,
) -> str
```

### Behavior

Advances the continuity history hash chain.

If `prev_hash_hex is None`, the next value is derived from the summary alone. Otherwise, the function hashes the previous value together with the new summary.

### Inputs

#### `prev_hash_hex`

* **Type:** `Optional[str]`
* **Meaning:** Previous history hash in hexadecimal form, or `None` for the first entry.

#### `summary`

* **Type:** `bytes`
* **Meaning:** Summary digest produced by `session_summary(...)`.

### Outputs

Returns the next history hash as a hexadecimal string.

## `derive_sym_key`

```python
def derive_sym_key(
    *,
    priv_enc: x25519.X25519PrivateKey,
    peer_pub_enc_b64: str,
    from_pub_sig_b64: str,
    to_pub_sig_b64: str,
    session: dict,
) -> bytes
```

### Behavior

Derives the 32-byte symmetric session key used for peer-to-peer encrypted envelopes.

The derivation binds together:

* the X25519 shared secret,
* message direction (`from` and `to` signing identities),
* session proof fields such as role, nonces, timestamp, and TTL,
* the envelope version domain.

### Inputs

#### `priv_enc`

* **Type:** `x25519.X25519PrivateKey`
* **Meaning:** Local private key used for X25519 key agreement.

#### `peer_pub_enc_b64`

* **Type:** `str`
* **Meaning:** Base64-encoded peer X25519 public key.

#### `from_pub_sig_b64`

* **Type:** `str`
* **Meaning:** Base64-encoded sender signing public key used for direction binding.

#### `to_pub_sig_b64`

* **Type:** `str`
* **Meaning:** Base64-encoded receiver signing public key used for direction binding.

#### `session`

* **Type:** `dict`
* **Meaning:** Session proof whose fields bind the derived key.

### Outputs

Returns the 32-byte derived symmetric session key.

## `derive_history_proof_key`

```python
def derive_history_proof_key(
    sym_key: bytes,
    aad_bytes: bytes,
) -> bytes
```

### Behavior

Derives the domain-separated authenticated-encryption (AEAD) key used for encrypting or decrypting `history_proof`.

This key is intentionally separated from both the base session key and the payload-encryption key.

### Inputs

#### `sym_key`

* **Type:** `bytes`
* **Meaning:** Base session key produced by `derive_sym_key(...)`.

#### `aad_bytes`

* **Type:** `bytes`
* **Meaning:** Authenticated additional data bytes that should bind this derived key.

### Outputs

Returns the derived 32-byte AEAD key for `history_proof`.

## `derive_payload_key`

```python
def derive_payload_key(
    sym_key: bytes,
    aad_bytes: bytes,
) -> bytes
```

### Behavior

Derives the domain-separated authenticated-encryption (AEAD) key used for payload encryption and decryption.

This key is separate from both the base session key and the history-proof key.

### Inputs

#### `sym_key`

* **Type:** `bytes`
* **Meaning:** Base session key produced by `derive_sym_key(...)`.

#### `aad_bytes`

* **Type:** `bytes`
* **Meaning:** Authenticated additional data bytes that should bind this derived key.

### Outputs

Returns the derived 32-byte AEAD key for payload encryption.

<p align="center">
  <a href="controls.md">&laquo; Previous: SummonerIdentityControls</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="policy_events.md">Next: Policy Events &raquo;</a>
</p>
