# Chains API Documentation - Fathom Blockchain v8.0.0+

## Overview

The Chains API provides a high-performance blockchain substrate for append-only data storage with strong ordering guarantees. This v8.0.0+ implementation features unified buffer handling, batched writes, and comprehensive metrics. The system is designed for multi-tenant operation with per-user chain isolation.

## Core Concepts

### Chain Architecture

- **Chain** - An ordered sequence of blocks identified by (shardId, tenant, chainName)
- **Block** - A container for one or more messages with system metadata
- **Shard** - A logical partition for distributing chains (Int32 range)
- **Tenant** - User-based isolation boundary (matches authenticated username)

### Key Features

- **Append-only structure** with optional prepend capability
- **Batched writes** for improved throughput
- **Buffer-native design** - all payloads handled as raw buffers
- **Strong ordering guarantees** within a chain
- **Comprehensive metrics** (message count, payload bytes)
- **System metadata** tracking for audit trails

### Data Flow

1. **Write Operations** - Accept raw buffer payloads, batch them, and commit as blocks
2. **Read Operations** - Return JSON with base64-encoded payloads for clean transport
3. **Metadata Operations** - Provide chain statistics and validation

## API Endpoints

### Write Operations

Write operations accept raw binary payloads and are tenant-permissive (users can write to any tenant's chains).

#### 1. Append to Chain

Adds data to the end of a chain (creates chain if it doesn't exist).

**Endpoint:** `POST /api/chains/append/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenant` - Target tenant (URL-safe string, max 255 chars)
- `chainName` - Chain name (URL-safe string, max 255 chars)
- `shardIdx` - Shard ID (Int32)

**Request Headers:**
- `Authorization: Bearer <token>` (required)
- `Content-Type: */*` (any type accepted)
- `X-System-Overrides: {...}` (optional JSON object for custom metadata)

**Request Body:**
- Raw binary data (max 50 MB)
- Must be non-empty

**Success Response (201 Created):**
```json
{
  "success": true,
  "blockIdx": "123",
  "eventId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameters or empty payload
- `401 Unauthorized` - Missing or invalid authentication
- `429 Too Many Requests` - Queue full (includes retry metrics)
- `500 Internal Server Error` - Server error

#### 2. Prepend to Chain

Adds data to the beginning of a chain.

**Endpoint:** `POST /api/chains/prepend/{tenant}/{chainName}/{shardIdx}`

Same parameters and responses as Append operation.

### Read Operations

Read operations are owner-gated (users can only read their own chains) and return JSON with base64-encoded payloads.

#### 3. Get Specific Block

Retrieves a block by its index.

**Endpoint:** `GET /api/chains/{tenant}/{chainName}/{shardIdx}/{blockIdx}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenant` - Must match authenticated user
- `chainName` - Chain name
- `shardIdx` - Shard ID
- `blockIdx` - Block index (BigInt as string)

**Success Response (200 OK):**
```json
{
  "block": {
    "shardId": 0,
    "tenant": "johndoe",
    "name": "events",
    "blockIdx": "123",
    "payloads_b64": [
      "SGVsbG8gV29ybGQ=",
      "VGVzdCBNZXNzYWdl"
    ],
    "system": [
      {
        "eventId": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2024-03-15T10:30:00Z",
        "sourceAgent": "johndoe",
        "user": {
          "customField": "value"
        }
      }
    ],
    "createdAt": "2024-03-15T10:30:00Z",
    "messageCount": 2,
    "payloadBytes": "23"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Missing authentication
- `404 Not Found` - Block not found or not owned
- `500 Internal Server Error` - Server error

#### 4. Get First Block

Retrieves the first (oldest) block in a chain.

**Endpoint:** `GET /api/chains/first/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

Response format same as Get Specific Block.

#### 5. Get Last Block

Retrieves the last (newest) block in a chain.

**Endpoint:** `GET /api/chains/last/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

Response format same as Get Specific Block.

#### 6. Get Block Range

Retrieves multiple blocks within an index range.

**Endpoint:** `GET /api/chains/range/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

**Query Parameters:**
- `startIdx` - Starting block index (required, BigInt as string)
- `endIdx` - Ending block index (required, BigInt as string)
- `order` - Sort order: "ASC" or "DESC" (default: "ASC")

**Validation:**
- `startIdx` must be ≤ `endIdx`

**Success Response (200 OK):**
```json
{
  "blocks": [...],
  "count": 10,
  "requestedRange": {
    "startIdx": "100",
    "endIdx": "109",
    "order": "ASC"
  }
}
```

#### 7. Get Recent Blocks

Retrieves the N most recent blocks.

**Endpoint:** `GET /api/chains/recent/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

**Query Parameters:**
- `count` - Number of blocks to retrieve (default: 10, max: 1000)

**Success Response (200 OK):**
```json
{
  "blocks": [...],
  "count": 5
}
```

### Metadata Operations

#### 8. Get Chain Metadata

Retrieves metadata about a specific chain.

**Endpoint:** `GET /api/chains/metadata/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

**Success Response (200 OK):**
```json
{
  "chain": {
    "shardId": 0,
    "tenant": "johndoe",
    "name": "events",
    "currentHead": "0",
    "currentTail": "999",
    "blockCount": "1000",
    "messageCount": "5432",
    "payloadBytes": "1048576",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-03-15T10:30:00Z",
    "isDeleting": false
  }
}
```

#### 9. Get Block Metadata (No Payload)

Retrieves metadata for a specific block without payload data.

**Endpoint:** `GET /api/chains/metadata/{tenant}/{chainName}/{shardIdx}/{blockIdx}`

**Authentication Required:** Yes

**Success Response (200 OK):**
```json
{
  "metadata": {
    "shardId": 0,
    "tenant": "johndoe",
    "name": "events",
    "blockIdx": "123",
    "system": [...],
    "createdAt": "2024-03-15T10:30:00Z",
    "messageCount": 2,
    "payloadBytes": "23"
  }
}
```

#### 10. Get Range Metadata

Retrieves metadata for multiple blocks without payloads.

**Endpoint:** `GET /api/chains/metadata/range/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

Query parameters same as Get Block Range.

#### 11. Validate Chain Integrity

Performs integrity validation on a chain.

**Endpoint:** `GET /api/chains/validate/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

**Success Response (200 OK):**
```json
{
  "validation": {
    "isValid": true,
    "errorMessage": null,
    "hasGaps": false,
    "expectedHead": "0",
    "actualHead": "0",
    "expectedTail": "999",
    "actualTail": "999",
    "expectedBlockCount": "1000",
    "actualBlockCount": "1000",
    "expectedMessageCount": "5432",
    "actualMessageCount": "5432",
    "expectedPayloadBytes": "1048576",
    "actualPayloadBytes": "1048576"
  }
}
```

#### 12. Get Tenant Statistics

Retrieves statistics for all chains owned by a tenant.

**Endpoint:** `GET /api/chains/stats/{tenant}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenant` - Must match authenticated user

**Success Response (200 OK):**
```json
{
  "stats": [
    {
      "shardId": 0,
      "tenant": "johndoe",
      "name": "events",
      "blockCount": "1000",
      "messageCount": "5432",
      "payloadBytes": "1048576",
      "avgBytesPerMsg": 193.21,
      "avgMsgsPerBlock": 5.43,
      "headIdx": "0",
      "tailIdx": "999",
      "chainSpan": "999",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-03-15T10:30:00Z",
      "lastActivityAge": "5 minutes"
    }
  ],
  "count": 1
}
```

### Delete Operations

#### 13. Delete Chain

Marks a chain for deletion (soft delete with cleanup).

**Endpoint:** `DELETE /api/chains/{tenant}/{chainName}/{shardIdx}`

**Authentication Required:** Yes

**Success Response (200 OK):**
```json
{
  "success": true,
  "deletedChain": {
    "shardId": 0,
    "tenant": "johndoe",
    "name": "events",
    "blockCount": "1000",
    "isDeleting": true,
    ...
  }
}
```

**Error Responses:**
- `423 Locked` - Chain is already locked for deletion
- Other standard errors

## Data Formats

### URL-Safe Strings

Tenant and chain names must be URL-safe:
- Alphanumeric: `a-z`, `A-Z`, `0-9`
- Special: `_`, `.`, `~`, `-`
- Maximum 255 characters

### System Metadata

Each block includes system metadata:
```json
{
  "eventId": "UUID",
  "timestamp": "ISO 8601 timestamp",
  "sourceAgent": "username",
  "user": {
    // Optional custom fields from X-System-Overrides
  }
}
```

### Payload Encoding

- **Writes**: Accept raw binary data (any content type)
- **Reads**: Return base64-encoded strings in JSON
- **Maximum size**: 50 MB per request

## Performance Features

### Batching System

The v8.0.0+ implementation includes intelligent batching:
- Multiple writes to the same chain are batched together
- Reduces database round trips
- Improves throughput under load

### Queue Management

- Per-chain write queues with configurable limits
- Returns 429 status with metrics when queue is full
- Automatic retry guidance in error responses

### Caching

Response headers include `Cache-Control: no-store` to prevent stale reads.

## Security & Access Control

### Authentication

All endpoints require JWT authentication via Bearer token.

### Tenant Isolation

- **Reads**: Strictly limited to chains owned by authenticated user
- **Writes**: Permissive across tenants (by design for cross-user messaging)
- **Deletes**: Only owner can delete their chains

### Error Masking

404 responses are used consistently to prevent tenant enumeration attacks.

## Usage Examples

### Writing Data

```javascript
// Append raw data to a chain
const appendData = async (tenant, chainName, shardId, data) => {
  const response = await fetch(
    `/api/chains/append/${tenant}/${chainName}/${shardId}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-System-Overrides': JSON.stringify({
          source: 'api-client',
          version: '1.0.0'
        })
      },
      body: data // Raw buffer or string
    }
  );
  
  return response.json();
};
```

### Reading Data

```javascript
// Get recent blocks and decode payloads
const getRecentMessages = async (chainName, shardId, count = 10) => {
  const response = await fetch(
    `/api/chains/recent/${username}/${chainName}/${shardId}?count=${count}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  const { blocks } = await response.json();
  
  // Decode base64 payloads
  return blocks.map(block => ({
    ...block,
    payloads: block.payloads_b64.map(p => atob(p))
  }));
};
```

### Range Queries

```javascript
// Get blocks in a specific range
const getBlockRange = async (chainName, shardId, start, end) => {
  const response = await fetch(
    `/api/chains/range/${username}/${chainName}/${shardId}?` +
    `startIdx=${start}&endIdx=${end}&order=ASC`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.json();
};
```

### Chain Validation

```javascript
// Validate chain integrity
const validateChain = async (chainName, shardId) => {
  const response = await fetch(
    `/api/chains/validate/${username}/${chainName}/${shardId}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  const { validation } = await response.json();
  if (!validation.isValid) {
    console.error('Chain validation failed:', validation.errorMessage);
  }
  return validation;
};
```

## Best Practices

### Writing

1. **Batch Operations**: Group related writes together for better performance
2. **Handle 429 Errors**: Implement exponential backoff when queue is full
3. **Use System Metadata**: Include tracking information via X-System-Overrides
4. **Size Limits**: Keep individual payloads under 50 MB

### Reading

1. **Use Appropriate Endpoints**: 
   - Use `/recent` for latest data
   - Use `/range` for historical queries
   - Use metadata endpoints when payloads aren't needed
2. **Decode Base64**: Remember to decode payloads from base64
3. **Pagination**: Use range queries for large datasets

### Performance

1. **Minimize Round Trips**: Use range queries instead of individual block fetches
2. **Cache Appropriately**: Implement client-side caching for immutable blocks
3. **Monitor Metrics**: Track message counts and payload sizes

### Error Handling

1. **Retry Logic**: Implement intelligent retry for 429 and 500 errors
2. **Validation**: Always validate parameters before sending requests
3. **Graceful Degradation**: Handle missing chains appropriately

## Migration from Previous Versions

### v7 to v8 Migration

Key changes in v8.0.0+:
- Unified buffer handling (no more `/raw` prefix)
- All endpoints now handle raw buffers for writes
- JSON responses include base64-encoded payloads
- New metrics in responses (messageCount, payloadBytes)
- Improved batching system

Migration steps:
1. Update write endpoints (remove `/raw` prefix)
2. Update payload encoding/decoding logic
3. Adapt to new response formats with metrics
4. Test queue limit handling (429 responses)

## Troubleshooting

### Common Issues

**"Queue full" errors (429)**
- Implement exponential backoff
- Consider reducing write frequency
- Monitor queue metrics in error response

**"Chain not found" errors (404)**
- Verify tenant matches authenticated user
- Check chain exists with metadata endpoint
- Ensure correct shard ID

**Invalid parameter errors (400)**
- Verify all IDs are valid integers/BigInts
- Check tenant/chain names are URL-safe
- Ensure date ranges are valid

**Large payload issues**
- Keep payloads under 50 MB
- Consider chunking large data
- Use compression if appropriate

## Performance Considerations

- Block creation is optimized for sequential writes
- Range queries are efficient for ordered access
- Validation operations may be expensive on large chains
- Statistics are cached and updated asynchronously