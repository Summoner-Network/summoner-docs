# Authentication API Documentation

## Overview

The Summoner authentication system provides secure user registration, login, and account management capabilities. The API uses JWT tokens for authentication and implements multiple authentication factors including password-based and API key authentication.

## Base URL

All authentication endpoints are available under the `/api/auth` prefix:

```
https://your-domain.com/api/auth
```

## Authentication Flow

The system supports two authentication methods:
1. **Password-based authentication** - Traditional username/password login
2. **API Key authentication** - Token-based authentication for programmatic access

Both methods result in a JWT token that must be included in subsequent API requests.

## Data Types

### Account Types
- `ElmType.Account` - Main user account object
- `ElmType.AccountFactorNormal` - Password authentication factor
- `ElmType.SecretWords` - Recovery words for account recovery

## API Endpoints

### 1. Register New Account

Creates a new user account with password and recovery words.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Validation Rules:**
- Username must be URL-safe (alphanumeric plus `_`, `.`, `~`, `-`)
- Username must be unique in the system
- Both username and password are required

**Success Response (201 Created):**
```json
{
  "jwt": "eyJhbGciOiJIUzI1NiIs...",
  "words": ["word1", "word2", "word3"]
}
```

**Error Responses:**
- `400 Bad Request` - Missing username or password
- `409 Conflict` - Username already exists
- `500 Internal Server Error` - Server error

**Important:** Store the recovery words securely. They are shown only once during registration.

### 2. Login

Authenticates a user and returns a JWT token.

**Endpoint:** `POST /api/auth/login`

**Request Body (Password Login):**
```json
{
  "username": "string",
  "password": "string"
}
```

**Request Body (API Key Login):**
```json
{
  "key": "string"
}
```

**Success Response (200 OK):**
```json
{
  "jwt": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Invalid credentials
- `500 Internal Server Error` - Server error

**Notes:**
- JWT tokens expire after 1 hour for password login
- API key tokens may have different expiration rules
- Include the JWT in the `Authorization` header for authenticated requests: `Bearer <token>`

### 3. Precheck Account

Retrieves recovery words for an existing account. Requires CSRF protection.

**Endpoint:** `POST /api/auth/precheck`

**Headers Required:**
```
X-CSRF-Token: <csrf-token-value>
```

**Request Body:**
```json
{
  "username": "string"
}
```

**Success Response (200 OK):**
```json
{
  "words": ["word1", "word2", "word3"]
}
```

**Error Responses:**
- `400 Bad Request` - Invalid username format
- `404 Not Found` - Account not found
- `500 Internal Server Error` - Server error

### 4. Get Current User

Retrieves the authenticated user's account information.

**Endpoint:** `GET /api/account/me`

**Headers Required:**
```
Authorization: Bearer <jwt-token>
```

**Success Response (200 OK):**
```json
{
  "account": {
    "type": 1,
    "id": "123456789",
    "version": 0,
    "attrs": {
      "username": "johndoe"
    }
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid JWT token
- `404 Not Found` - Account not found
- `500 Internal Server Error` - Server error

## CSRF Protection

### Get CSRF Token

Retrieves a CSRF token for protected endpoints.

**Endpoint:** `GET /api/auth/csrf/token`

**Success Response (200 OK):**
```json
{
  "token": "csrf-token-value"
}
```

Use this token in the `X-CSRF-Token` header for endpoints requiring CSRF protection.

## Security Features

### Password Storage
- Passwords are salted and hashed before storage
- Salt is generated uniquely for each password
- Raw passwords are never stored in the database

### Username Requirements
- Must contain only URL-safe characters: `a-z`, `A-Z`, `0-9`, `_`, `.`, `~`, `-`
- Cannot be empty
- Must be unique across the system

### JWT Token Structure
Tokens include:
- Account ID
- Username  
- Authentication method (user/api)
- Expiration time
- Session information

### Recovery Words
- Three secure random words generated during registration
- Used for account recovery processes
- Stored separately from password credentials

## Database Schema

The authentication system uses the following database relationships:

1. **Account Object** - Core user account
2. **Password Factor** - Stores hashed password and salt
3. **Secret Words** - Stores recovery words
4. **Associations:**
   - Username → Account (via username edge)
   - Account → Password Factor (via "secured_by" edge)
   - Account → Secret Words (via "personated_by" edge)

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "error": "error-description"
}
```

Common error codes:
- `unauthorized` - Authentication required or failed
- `username-taken` - Username already exists
- `invalid credentials` - Wrong username/password
- `internal-error` - Server-side error
- `not found` - Resource doesn't exist

## Rate Limiting

The API implements connection-level authentication via the `requireCellToken` middleware. Ensure your client includes the appropriate cell token for all requests.

## Example Usage

### Registration Flow
```javascript
// 1. Register new account
const response = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'johndoe',
    password: 'SecurePassword123!'
  })
});

const { jwt, words } = await response.json();
// Store JWT for authenticated requests
// Securely save recovery words
```

### Login Flow
```javascript
// 2. Login with password
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'johndoe',
    password: 'SecurePassword123!'
  })
});

const { jwt } = await response.json();
```

### Authenticated Request
```javascript
// 3. Make authenticated request
const response = await fetch('/api/account/me', {
  headers: {
    'Authorization': `Bearer ${jwt}`
  }
});

const { account } = await response.json();
```

## Migration Notes

- The system supports BigInt for IDs, ensure your client can handle large numeric values
- JSON payloads have a 50MB limit to support large data transfers
- All timestamps are stored as BigInt milliseconds since epoch

## Best Practices

1. **Token Management**
   - Store JWT tokens securely (httpOnly cookies recommended for web apps)
   - Refresh tokens before expiration
   - Clear tokens on logout

2. **Password Requirements**
   - Enforce strong password policies on the client side
   - Consider implementing password strength meters
   - Support password managers

3. **Recovery Words**
   - Display recovery words only once during registration
   - Prompt users to write them down securely
   - Never transmit recovery words over insecure channels

4. **Error Handling**
   - Don't expose sensitive information in error messages
   - Log errors server-side for debugging
   - Implement retry logic for network failures

## Support

For additional support or to report issues, use the `/api/contact` endpoint or refer to the main documentation at `/api/docs`.