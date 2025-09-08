# Fathom: Summoner Database API Docs

The Summoner database API (Fathom) is an enterprise financial-grade storage solution capable of supporting end-to-end encryption of data contents. While it is simple to reason about, it is also **low-level**. It is likely that you will build layers of abstraction on top of it. The good thing is that it is designed for this!

## Fundamental Concepts

---

### Objects

Objects are the primary entities in the Fathom storage system. They represent discrete units of data that can be created, retrieved, updated, and deleted within a tenant's isolated namespace.

#### Design Philosophy

Objects in Fathom are intentionally simple and unopinionated. The system doesn't impose any schema on the data payload - that's your application's responsibility. This design allows you to:

- Store encrypted data where the database has no knowledge of the plaintext
- Use any serialization format that suits your needs
- Evolve your data schemas without database migrations
- Build domain-specific abstractions on top of the simple object model

The combination of tenant isolation, type categorization, versioned updates, and binary payloads provides a foundation that's both secure and flexible enough to support a wide range of applications, from simple key-value stores to complex multi-tenant SaaS platforms.

#### Core Properties

Every object has the following essential properties:

- **Tenant**: A 64-bit integer that provides complete data isolation. All operations are scoped to a single tenant, ensuring that data from different tenants never intermingles. This is enforced at the database level.

- **Type**: A 32-bit integer that categorizes the object. Types are application-defined and allow you to distinguish between different kinds of entities (users, posts, configurations, etc.) within your system.

- **ID**: A 64-bit unsigned integer that uniquely identifies the object within its tenant and type. When creating a new object, you can let the system generate this ID automatically by passing 0 or null.

- **Version**: A 32-bit integer that tracks the number of updates to the object. This starts at 0 for new objects and increments with each update. The version number enables optimistic concurrency control.

- **Data**: A binary payload (stored as BYTEA in PostgreSQL) containing the actual content of the object. This can be any serialized data - JSON, Protocol Buffers, encrypted blobs, etc. The system treats this as opaque bytes, giving you complete flexibility in how you structure your data. There's a practical limit of 1MB per object.

- **Timestamps**: Both `created_at` and `updated_at` timestamps are automatically maintained by the system. The `updated_at` timestamp is guaranteed to advance monotonically with each update, even in rapid succession.

#### Optimistic Concurrency Control

Objects use optimistic locking through version numbers to prevent lost updates in concurrent scenarios. When updating an object, you must provide the expected version number. If another transaction has modified the object since you read it, your update will fail with a version conflict error (SQL state 40001), allowing you to retry with fresh data.

This pattern ensures data consistency without the overhead of pessimistic locking for most operations, while still providing the option to use `FOR UPDATE` locks when needed for critical read-modify-write cycles.

#### Lifecycle and Cascading Deletes

When an object is deleted, the system automatically removes all associations where that object appears as either the source or target. This cascade deletion happens atomically within the same transaction, ensuring referential integrity without leaving orphaned relationships.

---

### Associations

Associations represent directed relationships between objects, forming the graph structure that connects your data. They enable you to model complex relationships like social graphs, dependency trees, activity feeds, and any other connected data patterns.

#### Design Philosophy

Associations in Fathom provide a minimal but complete graph abstraction:

- **Flexibility**: The combination of typed relationships and data payloads supports any graph structure
- **Performance**: Optimized for the common pattern of scanning relationships from a source
- **Simplicity**: No complex graph query language - just straightforward relationship retrieval
- **Reliability**: Automatic cleanup and transactional consistency ensure data integrity

This design supports building everything from simple following relationships to complex knowledge graphs, while maintaining the same tenant isolation and storage accounting guarantees as objects.

#### Core Properties

Every association consists of:

- **Tenant**: Like objects, associations are completely isolated by tenant. An association can only connect objects within the same tenant.

- **Type**: A string identifier that describes the nature of the relationship (e.g., "likes", "follows", "owns", "replies_to"). Unlike object types which are integers, association types are strings to provide more semantic clarity when modeling relationships.

- **Source ID**: The 64-bit ID of the object that originates the relationship. This is the "subject" in a subject-verb-object triple.

- **Target ID**: The 64-bit ID of the object that receives the relationship. This is the "object" in a subject-verb-object triple.

- **Position**: A 64-bit monotonically increasing value that provides a stable ordering for associations. This is crucial for pagination and ensures associations can be retrieved in a consistent order even when created with identical timestamps.

- **Time**: A 64-bit epoch millisecond timestamp representing when the relationship was established. While position provides ordering, time provides temporal context that applications can use for features like "posts from the last week."

- **Data**: Like objects, associations can carry a binary payload of up to 128KB. This allows you to attach metadata to relationships - for example, the text of a comment, the reason for a follow, or encrypted relationship-specific data.

#### Unique Constraints and Upsert Semantics

The system enforces uniqueness on the combination of (tenant, type, source_id, target_id, position). This means:

- You can have multiple associations of the same type between the same two objects, as long as they have different positions
- This enables modeling temporal relationships (e.g., multiple "views" of a post by the same user at different times)
- When upserting with the same position, the existing association's data and time can be updated in place

#### Directional Nature

Associations are inherently directional. An association from A to B does not imply an association from B to A. This directional nature allows precise modeling of asymmetric relationships:

- User A follows User B (doesn't mean B follows A)
- Comment C replies to Post P (P doesn't reply to C)
- Order O contains Product P (P doesn't contain O)

If you need bidirectional relationships, you must create two associations, one in each direction.

#### Querying Patterns

The system is optimized for retrieving associations from a source object:

- **Forward scanning**: Find all objects that a given object relates to ("Who does Alice follow?")
- **Filtered scanning**: Find specific types of relationships ("What posts has Bob liked?")
- **Targeted queries**: Check specific relationships ("Does Alice follow Bob?")
- **Pagination**: Use position-based cursors for efficient pagination through large relationship sets

The default retrieval order is reverse chronological (newest first by position), which aligns with common patterns like activity feeds and recent interactions.

#### Automatic Cleanup

When an object is deleted, all associations where it appears as either source or target are automatically removed. This cascading delete ensures you never have dangling references to non-existent objects, maintaining referential integrity without manual cleanup.

#### Storage and Performance

Associations are indexed on (tenant, type, source_id, position DESC) for optimal retrieval performance. The system tracks storage usage per tenant, with association bytes counted separately from object bytes, enabling fine-grained storage accounting and potential quota policies.

---

### Journals

Journals provide an immutable, append/prepend-only log structure for recording sequences of events or messages. They implement a sequence-of-blocks structure that maintains cryptographic integrity while allowing both forward and backward traversal.

#### Design Philosophy

Journals in Fathom provide a robust event streaming foundation:

- **Reliability**: Transactional consistency with automatic retry on conflicts
- **Performance**: Batching and array storage minimize database overhead
- **Flexibility**: Support for both real-time streaming and batch processing
- **Scalability**: Sharding support for horizontal scaling
- **Simplicity**: No complex consensus protocols - just reliable, ordered storage

This design is ideal for:
- Command Query Request Separation
- Event sourcing architectures
- Audit and compliance logging
- Message streaming between services
- Time-series data storage
- Blockchain-like immutable records

The combination of immutability, batching, and bidirectional access provides a powerful primitive for building event-driven systems while maintaining the same strong consistency guarantees as the rest of Fathom.

#### Core Properties

Every journal consists of:

- **Shard ID**: A 32-bit integer that allows horizontal partitioning of journals across database instances. This enables scaling by distributing journals across multiple shards.

- **Tenant**: A string identifier (up to 255 characters) that provides namespace isolation. Unlike objects and associations which use numeric tenant IDs, journals use string tenant identifiers for more flexible multi-tenancy patterns.

- **Name**: A string identifier (up to 255 characters) that uniquely identifies the journal within its tenant and shard. This allows organizing multiple event streams per tenant.

- **Blocks**: The fundamental storage unit of a journal. Each block contains:
  - **Block Index**: A 64-bit integer providing the sequential position in the chain
  - **Payloads**: An array of binary messages (Buffers) batched together for efficiency
  - **System Metadata**: An array of JSON objects corresponding to each payload, containing metadata like timestamps, event IDs, and source information
  - **Metrics**: Message count and total payload bytes for the block

#### Bidirectional Structure

Journals maintain both head (oldest) and tail (newest) pointers, enabling efficient access from either end:

- **Append**: Add new blocks to the tail (end) of the journal
- **Prepend**: Add new blocks to the head (beginning) of the journal
- **Traversal**: Navigate forward from head to tail or backward from tail to head

This bidirectional nature supports use cases like:
- Event sourcing (append new events, replay from the beginning)
- Audit logs (append new entries, read recent activity)
- Message queues (prepend priority messages, append normal messages)

#### Batching and Performance

The journal system implements sophisticated batching to optimize write performance:

- **Automatic Batching**: Individual writes are automatically aggregated into blocks containing multiple messages
- **Native Array Storage**: Payloads are stored as PostgreSQL arrays (BYTEA[]), reducing overhead
- **Configurable Limits**: 
  - Maximum 5,000 messages per block
  - Maximum 64MB per block
  - Per-chain queue limits to prevent memory exhaustion
  - Global queue limits for system stability

#### Immutability and Integrity

Once written, journal blocks are immutable:

- **No Updates**: Blocks cannot be modified after creation
- **No Selective Deletes**: Individual blocks cannot be removed
- **Chain Deletion**: Only entire journals can be deleted as an atomic operation
- **Validation**: Built-in integrity checking ensures the chain structure remains consistent

The system provides validation functions that verify:
- Block sequence continuity (no gaps)
- Metadata consistency
- Message count and byte count accuracy

#### System Metadata

Each message in a journal carries system-generated metadata:

- **Event ID**: A UUID for message deduplication and tracing
- **Timestamp**: ISO-8601 timestamp of message creation
- **Source Agent**: Identifier of the entity that wrote the message
- **User Metadata**: Optional custom metadata provided via headers

#### Storage Metrics

Journals track comprehensive metrics at multiple levels:

- **Block Level**: Message count and payload bytes per block
- **Chain Level**: Total blocks, messages, and bytes
- **Tenant Level**: Aggregate statistics across all chains
- **Performance Metrics**: Average bytes per message, messages per block

---

### Counters

A tenant-scoped, time-bucketed accumulator for metering, quotas, and rate economics. Designed for high write throughput, canonical ordering, and strict non-negativity.

#### Data model

* **Key**: `(tenant BIGINT, name TEXT, duration_seconds INT, time_start TIMESTAMPTZ)`
* **Values**: `added BIGINT, subbed BIGINT, expires_at TIMESTAMPTZ NULL`
* **Derived**: `net = added − subbed`
* **Name rules**: URL-safe, 1–255 chars, per-tenant isolation
* **Granularity**: `0` perpetual, `60` minute, `3600` hour, `86400` day

#### Time normalization

* All timestamps normalize to bucket starts
* `duration_seconds = 0` maps to Unix epoch start
* Normalization guarantees idempotent addressing and stable locking keys

#### Operations surface

* **Increment** and **Decrement** mutate `added` and `subbed`
* **Set** assigns an exact non-negative `net` for a bucket
* **Get** returns one bucket
* **SumRange** aggregates across an inclusive time range at a chosen granularity
* Amounts are strictly positive for inc/dec, non-negative for set targets

#### Invariants and constraints

* **Non-negativity**: atomic check prevents updates that would produce `net < 0`
* **Monotone accounting**: `added` and `subbed` never decrease
* **Isolation**: all writes run at serializable isolation with automatic retry
* **Overflow safety**: BIGINT arithmetic enforced, overflow rejected
* **Auth**: user ID must equal tenant ID to eliminate cross-tenant access

#### Expiration

* Optional `expires_at` on a bucket
* For batched writes, expiration resolves by `MAX(expires_at)` among coalesced items
* Decrements do not advance expiration

#### Batching and throughput

* Writes batch across tenants and names
* Canonical sort `(tenant, name, duration_seconds, time_start)` prevents deadlocks
* Queue limits provide backpressure
* Batched API resolves to the durable post-batch `CounterResult` to preserve economic clarity

#### Read semantics

* Single-bucket reads return `net, added, subbed` or not-found if no row
* Range sums fold bucketed values within the given window
* Clients should treat responses as non-cacheable unless explicitly controlled

#### Error model

* Constraint violation yields a conflict when the resulting `net` would be negative
* Serialization and deadlock errors retried with exponential backoff
* Statement timeouts bound long operations and are surfaced as server errors
* Overflow returns a clear client error

#### Determinism and auditability

* Bucket addressing is deterministic after normalization
* Batches aggregate identically regardless of arrival order
* Structured logs capture inputs, normalized keys, and resulting `CounterResult`

#### Typical uses

* Per-agent request metering and fee debiting
* Quota windows and leaky-bucket style control with explicit economics
* Rollups for billing periods using `SumRange` at hour or day granularity
