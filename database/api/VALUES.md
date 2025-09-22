# Counters API Documentation - Time-Series Counting Service v1.1.0

## Overview

The Counters API provides a high-throughput, time-series counting service with support for multiple granularities and batched operations. It's designed for tracking metrics, events, and statistics with automatic time bucketing and expiration support. Version 1.1.0 includes deadlock prevention and asynchronous result handling for batched operations.

## Core Concepts

### Time-Series Architecture

- **Counter** - A named metric tracked over time with tenant isolation
- **Time Bucket** - Automatic normalization of timestamps to interval boundaries
- **Granularity** - Predefined or custom time intervals (perpetual, minute, hour, day, etc.)
- **Net Value** - The current value calculated as `added - subbed`

### Key Features

- **High-throughput batching** for efficient bulk operations
- **Atomic operations** preventing negative counters
- **Time normalization** for consistent bucketing
- **Expiration support** for automatic cleanup
- **Deadlock prevention** through canonical ordering
- **Asynchronous results** for batched operations (v1.1.0)

### Data Model

Each counter is uniquely identified by:
- `tenant` - User ID for isolation
- `name` - Counter name (URL-safe, 1-255 chars)
- `duration_seconds` - Granularity in seconds
- `time_start` - Normalized timestamp for the bucket

## Common Granularities

```javascript
const Granularity = {
    PERPETUAL: 0,    // Single value for all time
    MINUTE: 60,      // Per-minute buckets
    HOUR: 3600,      // Per-hour buckets
    DAY: 86400       // Per-day buckets
}
```

## API Endpoints

### Write Operations - Batched (High Throughput)

Batched operations queue writes for efficient processing and return results asynchronously once durable.

#### 1. Increment (Batched)

Increments a counter with automatic batching for high throughput.

**Endpoint:** `POST /api/counters/{tenantId}/{name}/increment`

**Authentication Required:** Yes

**Path Parameters:**
- `tenantId` - Must match authenticated user's ID
- `name` - Counter name (URL-safe, 1-255 chars)

**Request Body:**
```json
{
  "durationSeconds": 3600,
  "timestamp": "2024-03-15T10:30:00Z",
  "amount": 5,
  "expiresAt": "2024-04-15T10:30:00Z"
}
```

**Field Descriptions:**
- `durationSeconds` - Time bucket size (required, non-negative)
- `timestamp` - Event time (required, ISO 8601 or epoch)
- `amount` - Increment value (optional, default: 1, must be positive)
- `expiresAt` - Auto-cleanup time (optional)

**Success Response (200 OK):**
```json
{
  "net": "105",
  "added": "110",
  "subbed": "5"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Missing authentication
- `404 Not Found` - Tenant mismatch (security)
- `409 Conflict` - Constraint violation
- `429 Too Many Requests` - Queue full
- `500 Internal Server Error` - Server error

#### 2. Decrement (Batched)

Decrements a counter with automatic batching.

**Endpoint:** `POST /api/counters/{tenantId}/{name}/decrement`

**Authentication Required:** Yes

Same parameters as increment, except:
- `expiresAt` is ignored (decrements don't update expiration)
- Operation fails if result would be negative

### Write Operations - Synchronous (Immediate Results)

Synchronous operations bypass batching for immediate results but have lower throughput.

#### 3. Increment Sync

Increments a counter and immediately returns the result.

**Endpoint:** `POST /api/counters/{tenantId}/{name}/incrementSync`

**Authentication Required:** Yes

Same parameters and responses as batched increment, but:
- Bypasses batching queue
- Lower throughput
- Immediate result

#### 4. Decrement Sync

Decrements a counter and immediately returns the result.

**Endpoint:** `POST /api/counters/{tenantId}/{name}/decrementSync`

**Authentication Required:** Yes

Same parameters and responses as batched decrement, but with immediate execution.

#### 5. Set Value

Atomically sets a counter to a specific value.

**Endpoint:** `PUT /api/counters/{tenantId}/{name}/set`

**Authentication Required:** Yes

**Request Body:**
```json
{
  "durationSeconds": 3600,
  "timestamp": "2024-03-15T10:30:00Z",
  "targetValue": "100",
  "expiresAt": "2024-04-15T10:30:00Z"
}
```

**Field Descriptions:**
- `targetValue` - Desired counter value (required, non-negative)
- Other fields same as increment

**Notes:**
- Always synchronous (no batching)
- Calculates delta internally
- Idempotent for the same time bucket

### Read Operations

#### 6. Get Counter Value

Retrieves the current state of a specific counter bucket.

**Endpoint:** `GET /api/counters/{tenantId}/{name}/get`

**Authentication Required:** Yes

**Query Parameters:**
- `durationSeconds` - Time bucket size (required)
- `timestamp` - Time to query (required)

**Success Response (200 OK):**
```json
{
  "net": "100",
  "added": "150",
  "subbed": "50"
}
```

**Error Response (404 Not Found):**
Counter doesn't exist for the specified bucket.

#### 7. Sum Range

Aggregates counter values across a time range.

**Endpoint:** `GET /api/counters/{tenantId}/{name}/sumRange`

**Authentication Required:** Yes

**Query Parameters:**
- `durationSeconds` - Time bucket size (required)
- `startTime` - Range start (required, inclusive)
- `endTime` - Range end (required, inclusive)

**Success Response (200 OK):**
```json
{
  "net": "1500",
  "added": "2000",
  "subbed": "500"
}
```

**Notes:**
- Returns zeros if no data in range
- Timestamps don't need normalization
- Efficient aggregation at database level

## Time Normalization

The system automatically normalizes timestamps to bucket boundaries:

```javascript
// Examples of normalization
// For 60-second buckets (MINUTE):
// 10:30:45 → 10:30:00
// 10:31:15 → 10:31:00

// For 3600-second buckets (HOUR):
// 10:30:45 → 10:00:00
// 11:45:00 → 11:00:00

// For 0-second buckets (PERPETUAL):
// Any timestamp → 1970-01-01 00:00:00 (epoch)
```

## Response Format

All counter responses include three values:
- `net` - Current value (added - subbed)
- `added` - Total increments
- `subbed` - Total decrements

Values are returned as strings to handle BigInt precision.

## Error Handling

### Constraint Violations (409)

Operations fail atomically if they would violate constraints:
```json
{
  "error": "Operation failed due to constraint violation (e.g., counter cannot be negative)"
}
```

### Queue Overload (429)

When the batching queue is full:
```json
{
  "error": "Service overloaded (Queue Full). Please retry later."
}
```

Implement exponential backoff for retries.

### Overflow Protection (400)

Operations that would exceed BIGINT capacity:
```json
{
  "error": "Operation resulted in an overflow (exceeded BIGINT capacity)"
}
```

## Usage Examples

### Basic Counting

```javascript
// Track page views per hour
const trackPageView = async (userId) => {
  await fetch(`/api/counters/${userId}/page_views/increment`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      durationSeconds: 3600, // Hour granularity
      timestamp: new Date().toISOString(),
      amount: 1
    })
  });
};
```

### Rate Limiting

```javascript
// Check API usage in current minute
const checkRateLimit = async (userId, limit = 100) => {
  const now = new Date();
  const response = await fetch(
    `/api/counters/${userId}/api_calls/get?` +
    `durationSeconds=60&timestamp=${now.toISOString()}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  if (response.status === 404) {
    return { allowed: true, used: 0 };
  }
  
  const { net } = await response.json();
  return {
    allowed: parseInt(net) < limit,
    used: parseInt(net)
  };
};
```

### Time-Series Aggregation

```javascript
// Get daily active users for a week
const getDailyActiveUsers = async (startDate, endDate) => {
  const response = await fetch(
    `/api/counters/${tenantId}/daily_active_users/sumRange?` +
    `durationSeconds=86400&` +
    `startTime=${startDate.toISOString()}&` +
    `endTime=${endDate.toISOString()}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  const { net } = await response.json();
  return parseInt(net);
};
```

### Setting Quotas

```javascript
// Set monthly quota
const setMonthlyQuota = async (userId, resource, quota) => {
  const firstOfMonth = new Date();
  firstOfMonth.setDate(1);
  firstOfMonth.setHours(0, 0, 0, 0);
  
  await fetch(`/api/counters/${userId}/${resource}_quota/set`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      durationSeconds: 2592000, // ~30 days
      timestamp: firstOfMonth.toISOString(),
      targetValue: quota.toString(),
      expiresAt: new Date(Date.now() + 90 * 86400000).toISOString()
    })
  });
};
```

## Performance Considerations

### Batching Strategy

- **High-throughput operations**: Use batched endpoints (default)
- **Critical operations**: Use sync endpoints for immediate feedback
- **Queue management**: Monitor 429 responses and implement backoff

### Optimization Tips

1. **Choose appropriate granularity**: Smaller buckets = more storage
2. **Set expiration**: Automatic cleanup reduces storage
3. **Batch related operations**: Group increments when possible
4. **Use perpetual counters**: For totals that don't need time-series

### Database Design

- **Partitioning**: 16 hash partitions by tenant for scalability
- **HOT updates**: FILLFACTOR 75% for efficient in-place updates
- **Deadlock prevention**: Canonical ordering in bulk operations
- **Pre-aggregation**: Duplicate keys automatically summed

## Best Practices

### Naming Conventions

```javascript
// Good counter names (URL-safe, descriptive)
"user_logins"
"api_calls_v2"
"payment_success"
"cache_hits"

// Bad counter names
"user logins"     // Space not URL-safe
"api/calls"       // Slash not URL-safe
"🔥"              // Emoji not URL-safe
"a"               // Too vague
```

### Error Recovery

```javascript
// Implement retry with exponential backoff
const incrementWithRetry = async (params, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await increment(params);
    } catch (error) {
      if (error.status === 429 && i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000);
        continue;
      }
      throw error;
    }
  }
};
```

### Monitoring

Track these metrics:
- 429 response rates (queue pressure)
- 409 response rates (negative counter attempts)
- Response times (batched vs sync)
- Queue depths (if exposed)

## Migration Notes

### v1.0.0 to v1.1.0

Key changes:
- Batched operations now return results asynchronously
- Deadlock prevention through canonical ordering
- Better error differentiation for constraint violations

Migration steps:
1. Update client code to handle returned results from batched operations
2. Remove any custom result polling logic (no longer needed)
3. Update error handlers for new 409 responses

## Limitations

- **Counter names**: Maximum 255 characters
- **Value range**: -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 (BIGINT)
- **Queue size**: 500,000 operations globally
- **Batch size**: 5,000 operations per database call
- **Negative values**: Not allowed (enforced atomically)

## Troubleshooting

### Common Issues

**"Counter cannot be negative" errors**
- Check for race conditions in decrement logic
- Ensure proper initialization of counters
- Consider using conditional decrements

**Queue full (429) errors**
- Implement proper backoff
- Consider reducing operation frequency
- Monitor for traffic spikes

**Overflow errors**
- Check for infinite loops in increment logic
- Validate amount parameters
- Consider resetting counters periodically

**Time bucket confusion**
- Remember timestamps are auto-normalized
- Use consistent granularity for related counters
- Test with known timestamps first