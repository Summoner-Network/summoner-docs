# Agent API Documentation - Principal Secrets Management

## Overview

The Agent API implements a "Valet Key" pattern for delegated authentication, allowing users to create and manage API keys (called "principal secrets") that automated processes can use to act on their behalf. This system enables secure, revocable access for bots, services, and other automated agents.

## Core Concepts

### The Valet Key Pattern

Similar to how a valet key gives limited access to your car, principal secrets allow automated processes to perform actions on behalf of a user without exposing the user's primary credentials. The system uses three main operations:

1. **PROVISION** - Users create new secrets for their agents
2. **VERIFY** - Services validate that a secret is authorized
3. **REVOKE** - Users remove secrets to terminate access

### Data Model

- **AgentCollection** - A user's "keyring" that holds all their agent secrets
- **Agent** - An individual automated process or service with delegated access
- **Principal Secret** - A 32-byte hex string that serves as the API key

### Structural Storage

The elegance of this system comes from storing secrets structurally in the knowledge graph. The secret itself becomes the TYPE of the association between the AgentCollection and Agent objects, making verification extremely fast.

## API Key Format

API keys use a composite format:
```
{username}%{secret_hex}
```

Example:
```
johndoe%a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890
```

## API Endpoints

### 1. Associate a New Secret

Creates a new principal secret for automated agent access.

**Endpoint:** `POST /api/agent/associate`

**Authentication Required:** Yes (user JWT token)

**Request Headers:**
```
Authorization: Bearer <jwt-token>
```

**Request Body:**
```json
{
  "secret": "string (32-byte hex)"
}
```

**Secret Format:**
- Must be exactly 32 bytes (64 hex characters)
- Can optionally include "0x" prefix
- Example: `"0xa1b2c3d4e5f6789012345678901234567890123456789012345678901234567890"`

**Success Response (200 OK):**
```json
{
  "ok": true,
  "collection": "123456789",
  "agent": "987654321",
  "secret": "0xa1b2c3d4e5f6789012345678901234567890123456789012345678901234567890"
}
```

**Error Responses:**
- `400 Bad Request` - Missing or invalid secret format
- `401 Unauthorized` - Invalid or missing JWT token
- `409 Conflict` - Secret already exists for this account
- `500 Internal Server Error` - Server error

### 2. Revoke a Secret

Removes a principal secret and its associated agent.

**Endpoint:** `POST /api/agent/revoke`

**Authentication Required:** Yes (user JWT token)

**Request Headers:**
```
Authorization: Bearer <jwt-token>
```

**Request Body:**
```json
{
  "secret": "string (32-byte hex)"
}
```

**Success Response (200 OK):**
```json
{
  "ok": true,
  "message": "Secret revoked successfully."
}
```

**Error Responses:**
- `400 Bad Request` - Missing or invalid secret format
- `401 Unauthorized` - Invalid or missing JWT token
- `404 Not Found` - Secret not found for this account
- `500 Internal Server Error` - Server error

### 3. Check Secret Association

Verifies if a secret is associated with a specific account (public endpoint).

**Endpoint:** `POST /api/agent/check?account={accountId}`

**Authentication Required:** No

**Query Parameters:**
- `account` - The numeric account ID to check against

**Request Body:**
```json
{
  "secret": "string (32-byte hex)"
}
```

**Success Response (200 OK):**
```json
{
  "associated": true,
  "agent": "987654321"
}
```

Or if not associated:
```json
{
  "associated": false,
  "agent": null
}
```

**Error Responses:**
- `400 Bad Request` - Missing parameters or invalid format
- `500 Internal Server Error` - Server error

### 4. Verify API Key

Validates a complete API key (username + secret combination).

**Endpoint:** `POST /api/agent/verify`

**Authentication Required:** No

**Request Body:**
```json
{
  "key": "username%secret"
}
```

**Success Response (200 OK):**
```json
{
  "valid": true
}
```

Or if invalid:
```json
{
  "valid": false
}
```

**Error Responses:**
- `400 Bad Request` - Missing key parameter
- `500 Internal Server Error` - Server error

## Helper Functions

### resolveApiKey(apiKey: string): Promise<User | null>

Internal function for resolving an API key to a user identity.

**Parameters:**
- `apiKey` - Composite key in format `username%secret`

**Returns:**
- User object with `{id, username, source}` if valid
- `null` if invalid

### isApiKeyValid(apiKey: string): Promise<boolean>

Validates whether an API key is properly formatted and associated.

**Parameters:**
- `apiKey` - Composite key in format `username%secret`

**Returns:**
- `true` if valid and associated
- `false` otherwise

## Security Considerations

### Secret Requirements
- Must be exactly 32 bytes (256 bits) of entropy
- Should be generated using cryptographically secure random number generators
- Never reuse secrets across different services

### Username Validation
- Usernames must be URL-safe (alphanumeric plus `_`, `.`, `~`, `-`)
- This ensures API keys can be safely transmitted in headers and URLs

### Access Control
- Only authenticated users can create or revoke secrets
- Secret checking can be done publicly (for service verification)
- Each secret is tied to exactly one user account

### Revocation
- Revocation is immediate and atomic
- Once revoked, a secret cannot be reused
- Revocation removes both the association and the agent object

## Implementation Details

### Graph Structure

```
Account
  └─[is_principal]→ AgentCollection
                        └─[secret_hex]→ Agent
```

The secret itself becomes the edge type, making lookups O(1).

### Transaction Safety
All operations are wrapped in database transactions to ensure consistency.

### Case Sensitivity
Hex secrets are normalized to lowercase for consistent storage and comparison.

## Usage Examples

### Creating a New API Key

```javascript
// 1. Generate a secure random secret
const secret = crypto.randomBytes(32).toString('hex');

// 2. Associate it with your account
const response = await fetch('/api/agent/associate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userJwt}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ secret: `0x${secret}` })
});

const result = await response.json();
// Save the composite key for the agent to use
const apiKey = `${username}%${secret}`;
```

### Using an API Key in Services

```javascript
// Agent/service code
const apiKey = process.env.SUMMONER_API_KEY; // "username%secret"

// Make authenticated requests
const response = await fetch('/api/some-protected-endpoint', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ /* request data */ })
});
```

### Verifying an API Key

```javascript
// Service-side verification
const isValid = await fetch('/api/agent/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key: receivedApiKey })
}).then(r => r.json()).then(data => data.valid);

if (!isValid) {
  throw new Error('Invalid API key');
}
```

### Revoking Access

```javascript
// User revokes a compromised key
await fetch('/api/agent/revoke', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userJwt}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ secret: compromisedSecret })
});
```

## Best Practices

### For Users

1. **Generate Strong Secrets**
   - Use cryptographically secure random number generators
   - Never use predictable values or patterns
   - Generate unique secrets for each service

2. **Secret Management**
   - Store secrets securely (use environment variables, secret managers)
   - Rotate secrets periodically
   - Revoke immediately if compromised

3. **Principle of Least Privilege**
   - Create separate secrets for different services
   - Revoke unused secrets promptly

### For Developers

1. **Secret Validation**
   - Always validate secret format before processing
   - Use the provided helper functions for consistency
   - Handle validation errors gracefully

2. **Error Handling**
   - Don't expose secret values in error messages
   - Log security events for monitoring
   - Implement rate limiting on verification endpoints

3. **Integration Patterns**
   - Cache validation results appropriately
   - Use connection pooling for database efficiency
   - Implement retry logic with exponential backoff

## Migration and Compatibility

### From Traditional API Keys

If migrating from a traditional API key system:

1. Generate new principal secrets for existing integrations
2. Update services to use the composite key format
3. Implement parallel validation during transition
4. Revoke old credentials after migration

### Version Compatibility

The current implementation (v2.3) maintains backward compatibility with:
- All secret formats (with or without "0x" prefix)
- Both authentication methods (JWT and API key)
- Existing database structures

## Troubleshooting

### Common Issues

**"secret-exists" Error**
- The secret is already associated with your account
- Generate a new random secret instead

**"unauthorized" Error**
- JWT token is missing, expired, or invalid
- API key authentication is not supported for this endpoint

**"secret must be 32-byte hex" Error**
- Secret is not exactly 64 hex characters
- Check for extra spaces or invalid characters

### Debugging Tips

1. Verify secret format: `/^(?:0x)?[0-9a-fA-F]{64}$/`
2. Check username is URL-safe
3. Ensure JWT token hasn't expired
4. Verify account has necessary permissions

## Performance Considerations

- Secret verification is O(1) due to structural storage
- AgentCollection creation is lazy (on first secret)
- Revocation is atomic and immediate
- No cascade deletions required due to graph structure

## Future Enhancements

Potential improvements under consideration:
- Secret expiration dates
- Usage analytics and audit logs
- Scoped permissions per secret
- Multi-factor authentication for sensitive operations
- Rate limiting per API key