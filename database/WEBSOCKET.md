# Fathom: Transactional WebSocket API

The Fathom WebSocket API provides a stateful, session-based interface for executing multiple database operations within a single, atomic transaction. It is designed for workflows requiring strong consistency across sequences of reads and writes. It complements the stateless REST APIs by offering compound operations with transactional guarantees.

---

## Core Concepts

### 1. Transactional Atomicity

* **Isolation**: Each WebSocket connection maps to a single database transaction at `SERIALIZABLE` isolation level.
* **All or Nothing**: On connect, a `BEGIN TRANSACTION` is issued. Operations (`putObject`, `incrementCounter`, etc.) execute inside the transaction.
* **Finalization**: Only `commit` or `rollback` ends the transaction.
* **Consistency**: If the connection is lost, the server crashes, or rollback occurs, no changes persist.

### 2. Session Lifecycle

1. **Connect & Authenticate**: WebSocket handshake with authentication.
2. **Transaction Begins**: Server starts a `SERIALIZABLE` transaction.
3. **Execute Operations**: Client sends JSON-RPC commands. Results remain session-local.
4. **Finalize Transaction**:

   * `commit`: Makes all changes durable and visible.
   * `rollback`: Aborts and discards all changes.
5. **Connection Close**: Server finalizes and closes connection after commit or rollback.

### 3. Shared Transaction Context

* Objects, Journals, and Counters APIs share the same underlying database connection.
* Example: A `putObject` followed by `incrementCounter` are part of the same atomic unit.

### 4. Binary Protocol

* **Message Structure**:

  1. **4-byte header**: Big-endian uint32 length of JSON part.
  2. **JSON-RPC Payload**: UTF-8 encoded method call.
  3. **Optional Binary Payload**: Raw data for methods like `putObject` or `append`.

---

## Available Methods

### Objects & Associations

* `putObject`: Create or update an object.
* `getObject`: Retrieve an object.
* `removeObject`: Delete an object.
* `putAssociation`: Create a relationship between two objects.
* `getAssociations`: Retrieve associations from a source object.
* `removeAssociation`: Delete an association.

### Journals

* `append`: Add message to end of journal.
* `prepend`: Add message to beginning of journal.

### Counters

* `incrementCounter`: Increment a time-bucketed counter.
* `decrementCounter`: Decrement counter, fails if negative.
* `setCounter`: Set counter to a non-negative value.
* `getCounter`: Read current value of a bucket.
* `sumRangeCounter`: Aggregate counter values over a time range.

### Transaction Control

* `commit`: Atomically commit all operations.
* `rollback`: Abort and discard all changes.

---

## Failure Modes & Guarantees

### Connection Loss

* If connection ends before commit completes, transaction is rolled back.
* Client must retry entire transaction.

### Version Conflicts & Serialization Failures (`-32002`)

* Caused by concurrent modifications under `SERIALIZABLE`.
* Transaction becomes poisoned. Must rollback and retry.

### Constraint Violations (`-32003`)

* Business logic failures (e.g., decrement below zero, overflow).
* Do not poison transaction. Client can continue, retry operation, or rollback.

---

## Example Workflow: Metered Update

**Goal**: Atomically read an object, log an update, meter API call, and update the object.

1. Client connects → Server starts transaction.
2. Client sends `getObject` for `/objects/1/123`, receives `version: 42`.
3. Client sends `append` to audit journal:

   ```json
   {"action": "update", "objectId": 123, "user": "alice"}
   ```
4. Client sends `incrementCounter` for `api_calls:object_write`.
5. Client sends `putObject` for `/objects/1/123` with `expectedVersion: 42`.
6. Client sends `commit`.

**Outcome**: Object update, journal append, and counter increment commit atomically.

**Failure Case**: If another client modifies object `123` between steps 2–5, step 5 fails with `VERSION_CONFLICT`. Client must rollback and retry the workflow.
