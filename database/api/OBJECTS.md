# Objects API Documentation - TAO Storage Substrate

## Overview

The Objects API provides a tenant-isolated graph storage system for managing objects and their associations. This forms the core TAO (Objects, Associations) substrate that powers the Summoner platform's data layer. Each user operates within their own isolated tenant space, ensuring data privacy and security.

## Core Concepts

### TAO Architecture

The TAO (pronounced "dao") system consists of two primary entities:

1. **Objects** - Typed entities with versioned data payloads
2. **Associations** - Directed edges between objects with typed relationships

### Tenant Isolation

Every user has their own tenant space identified by their unique user ID (bigint). All operations are strictly isolated to the authenticated user's tenant, preventing cross-tenant data access.

### Data Format

- All data payloads are transmitted as base64-encoded strings in the API
- Internally stored as binary buffers for efficiency
- Maximum object size: 1 MB
- Maximum association size: 128 KB

## API Endpoints

### 1. Get Object

Retrieves a specific object by its type and ID.

**Endpoint:** `GET /api/objects/{tenantId}/{otype}/{id}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenantId` - The tenant ID (must match authenticated user's ID)
- `otype` - Object type (integer)
- `id` - Object ID (bigint as string)

**Success Response (200 OK):**
```json
{
  "type": 100,
  "version": 2,
  "id": "123456789",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:35:00Z",
  "data_b64": "eyJuYW1lIjoiZXhhbXBsZSJ9"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameter format
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Attempting to access another tenant's data
- `404 Not Found` - Object does not exist
- `500 Internal Server Error` - Server error

### 2. Put Object (Create/Update)

Creates a new object or updates an existing one. Uses optimistic concurrency control via version numbers.

**Endpoint:** `PUT /api/objects/{tenantId}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenantId` - The tenant ID (must match authenticated user's ID)

**Request Body:**
```json
{
  "type": 100,
  "version": 1,
  "id": "123456789",
  "data": "eyJuYW1lIjoiZXhhbXBsZSJ9"
}
```

**Field Descriptions:**
- `type` - Object type (integer, max 1,000,000,000)
- `version` - Version number for optimistic concurrency control
- `id` - Object ID (optional, use "0" for auto-generation)
- `data` - Base64-encoded data payload (max 1 MB decoded)

**Success Response (201 Created):**
```json
{
  "success": true,
  "id": "123456789"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request body or data exceeds size limit
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Invalid tenant ID or object type exceeds limit
- `409 Conflict` - Version conflict (object was modified by another request)
- `500 Internal Server Error` - Server error

**Version Conflict Handling:**

When a 409 Conflict occurs:
```json
{
  "error": "Conflict: The object was modified by another request. Please refetch and try again.",
  "code": "VERSION_CLASH"
}
```

### 3. Delete Object

Removes an object from the system.

**Endpoint:** `DELETE /api/objects/{tenantId}/{otype}/{id}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenantId` - The tenant ID (must match authenticated user's ID)
- `otype` - Object type (integer)
- `id` - Object ID (bigint as string)

**Success Response (200 OK):**
```json
{
  "success": true
}
```

Or if object didn't exist:
```json
{
  "success": false,
  "message": "Object may not have existed"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameter format
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Attempting to delete another tenant's data
- `500 Internal Server Error` - Server error

### 4. Get Associations

Retrieves associations of a specific type from a source object.

**Endpoint:** `GET /api/objects/{tenantId}/associations/{type}/{sourceId}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenantId` - The tenant ID (must match authenticated user's ID)
- `type` - Association type (string, must be URL-safe)
- `sourceId` - Source object ID (bigint as string)

**Query Parameters:**
- `targetId` - Filter by target ID (optional, default: 0)
- `after` - Pagination cursor (optional, default: 0)
- `limit` - Maximum results to return (optional, default: 50, max: 1000)

**Success Response (200 OK):**
```json
{
  "count": 2,
  "associations": [
    {
      "type": "owns",
      "sourceId": "123456789",
      "targetId": "987654321",
      "time": "1705318200000",
      "position": "1705318200000",
      "data_b64": "eyJtZXRhIjoidGVzdCJ9"
    },
    {
      "type": "owns",
      "sourceId": "123456789",
      "targetId": "456789123",
      "time": "1705318300000",
      "position": "1705318300000",
      "data_b64": "eyJtZXRhIjoidGVzdDIifQ=="
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameters or limit exceeds 1000
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Attempting to query another tenant's data
- `500 Internal Server Error` - Server error

### 5. Create Association

Creates a new association between two objects.

**Endpoint:** `PUT /api/objects/{tenantId}/associations`

**Authentication Required:** Yes

**Path Parameters:**
- `tenantId` - The tenant ID (must match authenticated user's ID)

**Request Body:**
```json
{
  "type": "owns",
  "sourceId": "123456789",
  "targetId": "987654321",
  "time": "1705318200000",
  "position": "1705318200000",
  "data": "eyJtZXRhIjoidGVzdCJ9"
}
```

**Field Descriptions:**
- `type` - Association type (string, must be URL-safe)
- `sourceId` - Source object ID (bigint as string)
- `targetId` - Target object ID (bigint as string)
- `time` - Timestamp in milliseconds (bigint as string)
- `position` - Sort position (bigint as string)
- `data` - Base64-encoded data payload (max 128 KB decoded)

**Success Response (201 Created):**
```json
{
  "success": true
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request body or data exceeds size limit
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Attempting to write to another tenant
- `500 Internal Server Error` - Server error

### 6. Delete Association

Removes an association between two objects.

**Endpoint:** `DELETE /api/objects/{tenantId}/associations/{type}/{sourceId}/{targetId}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenantId` - The tenant ID (must match authenticated user's ID)
- `type` - Association type (string)
- `sourceId` - Source object ID (bigint as string)
- `targetId` - Target object ID (bigint as string)

**Success Response (200 OK):**
```json
{
  "success": true
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameter format
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Attempting to delete another tenant's data
- `500 Internal Server Error` - Server error

### 7. Get Tenant Statistics

Retrieves storage statistics for the authenticated user's tenant.

**Endpoint:** `GET /api/objects/stats/{tenantId}`

**Authentication Required:** Yes

**Path Parameters:**
- `tenantId` - The tenant ID (must match authenticated user's ID)

**Success Response (200 OK):**
```json
{
  "tenant": "123456789",
  "object_count": "1523",
  "association_count": "4892",
  "object_bytes": "1048576",
  "association_bytes": "524288",
  "total_bytes": "1572864",
  "avg_bytes_per_object": "688.45",
  "avg_bytes_per_association": "107.12",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid tenant ID format
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Attempting to access another tenant's stats
- `500 Internal Server Error` - Server error

## Data Validation

### URL-Safe Strings

Association types must be URL-safe, containing only:
- Alphanumeric characters: `a-z`, `A-Z`, `0-9`
- Special characters: `_`, `.`, `~`, `-`

### BigInt Handling

All IDs and numeric values that may exceed JavaScript's safe integer range are transmitted as strings and parsed as BigInts internally.

### Size Limits

- **Object data**: Maximum 1 MB
- **Association data**: Maximum 128 KB
- **Object type**: Maximum value 1,000,000,000
- **Query limit**: Maximum 1000 results per request

## Optimistic Concurrency Control

The system uses version numbers for optimistic concurrency control on objects:

1. Retrieve an object to get its current version
2. Increment the version number when updating
3. If another update occurred between read and write, a 409 Conflict is returned
4. Client should refetch the latest version and retry with updated data

## Usage Examples

### Creating an Object

```javascript
const createObject = async (tenantId, type, data) => {
  const response = await fetch(`/api/objects/${tenantId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: type,
      version: 0,
      id: "0", // Auto-generate ID
      data: btoa(JSON.stringify(data)) // Convert to base64
    })
  });
  
  const result = await response.json();
  return result.id;
};
```

### Updating with Version Control

```javascript
const updateObject = async (tenantId, otype, id, newData) => {
  // 1. Fetch current object
  const getResponse = await fetch(`/api/objects/${tenantId}/${otype}/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const current = await getResponse.json();
  
  // 2. Update with incremented version
  const updateResponse = await fetch(`/api/objects/${tenantId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: otype,
      version: current.version + 1,
      id: id,
      data: btoa(JSON.stringify(newData))
    })
  });
  
  if (updateResponse.status === 409) {
    console.log('Version conflict - retry needed');
    // Retry logic here
  }
  
  return updateResponse.json();
};
```

### Creating Associations

```javascript
const linkObjects = async (tenantId, sourceId, targetId, relationType) => {
  const response = await fetch(`/api/objects/${tenantId}/associations`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: relationType,
      sourceId: sourceId.toString(),
      targetId: targetId.toString(),
      time: Date.now().toString(),
      position: Date.now().toString(),
      data: btoa('{}') // Empty JSON object
    })
  });
  
  return response.json();
};
```

### Querying Associations

```javascript
const getRelatedObjects = async (tenantId, sourceId, relationType) => {
  const response = await fetch(
    `/api/objects/${tenantId}/associations/${relationType}/${sourceId}?limit=100`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  const result = await response.json();
  return result.associations.map(a => ({
    targetId: a.targetId,
    metadata: JSON.parse(atob(a.data_b64))
  }));
};
```

## Best Practices

### Data Encoding
- Always base64 encode data before sending to the API
- Decode base64 data when receiving from the API
- Use proper error handling for encoding/decoding operations

### Version Management
- Always increment version numbers when updating objects
- Implement retry logic for version conflicts
- Consider using exponential backoff for retries

### Performance Optimization
- Use appropriate limit values for association queries
- Implement pagination for large result sets
- Cache frequently accessed objects client-side

### Security
- Never expose tenant IDs in client-facing applications
- Validate all input data before sending to the API
- Use HTTPS for all API communications

## Error Handling

### Common Error Patterns

**Version Conflicts (409)**
- Indicates concurrent modification
- Refetch the object and retry with the new version
- Implement automatic retry with backoff

**Size Limit Exceeded (400)**
- Check data size before encoding
- Consider compression for large payloads
- Split large data across multiple objects if necessary

**Authentication Failures (401)**
- Refresh authentication tokens
- Redirect to login if session expired
- Implement token refresh logic

**Forbidden Access (403)**
- Verify tenant ID matches authenticated user
- Check object type limits
- Ensure proper permissions

## Performance Considerations

- Association lookups are optimized for forward traversal (from source)
- Use appropriate indexing strategies for your access patterns
- Batch operations when possible to reduce round trips
- Consider caching strategies for frequently accessed data

## Migration and Compatibility

The Objects API maintains backward compatibility with:
- All existing object types and associations
- Legacy data formats (automatic conversion)
- Previous API versions (deprecated endpoints still functional)

When migrating:
1. Update clients to use base64 encoding
2. Implement version control for critical objects
3. Test retry logic for version conflicts
4. Monitor size limits during transition