# NANDA Index MCP Servers API Documentation

## Base URL
```
https://join39.org/api/mcp-servers
```

## Table of Contents
- [Overview](#overview)
- [API Endpoints](#api-endpoints)
  - [List All Servers](#list-all-servers)
  - [Create Server](#create-server)
  - [Update Server](#update-server)
  - [Delete Server](#delete-server)
- [Data Schema](#data-schema)
- [Validation Rules](#validation-rules)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Overview

This API provides a simple interface to manage MCP servers in a public registry. It supports full CRUD operations without requiring authentication or API keys, making it easy for developers to integrate MCP servers into their applications.

### Key Features
- ✅ **No Authentication Required** - Public API for easy integration
- ✅ **Full CRUD Operations** - Create, Read, Update, Delete
- ✅ **Input Validation** - Ensures data quality and security
- ✅ **Duplicate Prevention** - Prevents duplicate endpoint submissions
- ✅ **JSON API** - Standard REST API with JSON responses
- ✅ **Error Handling** - Clear error messages and HTTP status codes

---

## API Endpoints

### List All Servers

**GET** `/api/mcp-servers`

Retrieves all publicly available MCP servers.

**Request:**
```bash
curl https://join39.org/api/mcp-servers
```

**Response:**
```json
{
  "success": true,
  "servers": [
    {
      "id": "687472d4476f071042eb5dfd",
      "name": "Weather Agent",
      "endpoint": "https://api.weather.com/mcp",
      "description": "Provides real-time weather data",
      "created_at": "2025-07-14T01:15:23.000Z",
      "registry_provider": "nanda"
    },
    {
      "id": "687472e8476f071042eb5dfe",
      "name": "File Manager",
      "endpoint": "https://files.example.com/mcp",
      "description": "File operations and management",
      "created_at": "2025-07-14T01:16:45.000Z",
      "registry_provider": "nanda"
    }
  ]
}
```

---

### Create Server

**POST** `/api/mcp-servers`

Creates a new MCP server entry.

**Request:**
```bash
curl -X POST https://join39.org/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Awesome Agent",
    "endpoint": "https://my-server.com/mcp",
    "description": "Does amazing things with data"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "MCP server submitted successfully",
  "server_id": "687472d4476f071042eb5dfd",
  "name": "My Awesome Agent",
  "endpoint": "https://my-server.com/mcp"
}
```

---

### Update Server

**PUT** `/api/mcp-servers`

Updates an existing MCP server.

**Request:**
```bash
curl -X PUT https://join39.org/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "687472d4476f071042eb5dfd",
    "name": "My Updated Agent",
    "endpoint": "https://my-server.com/v2/mcp",
    "description": "Updated with new features"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "MCP server updated successfully",
  "server_id": "687472d4476f071042eb5dfd",
  "name": "My Updated Agent",
  "endpoint": "https://my-server.com/v2/mcp"
}
```

---

### Delete Server

**DELETE** `/api/mcp-servers?id={server_id}`

Removes an MCP server from the registry.

**Request:**
```bash
curl -X DELETE "https://join39.org/api/mcp-servers?id=687472d4476f071042eb5dfd"
```

**Response:**
```json
{
  "success": true,
  "message": "MCP server deleted successfully",
  "server_id": "687472d4476f071042eb5dfd"
}
```

---

## Data Schema

### MCP Server Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ (for updates/deletes) | Unique server identifier |
| `name` | string | ✅ | Server display name (1-100 characters) |
| `endpoint` | string | ✅ | HTTP/HTTPS URL to the MCP server |
| `description` | string | ❌ | Optional description of the server |
| `created_at` | string | ❌ (auto-generated) | ISO timestamp of creation |
| `registry_provider` | string | ❌ (auto-set) | Registry provider (always "nanda") |

### Request Format

**Create/Update Request:**
```json
{
  "name": "string",
  "endpoint": "string",
  "description": "string (optional)"
}
```

**Update Request (additional field):**
```json
{
  "id": "string",
  "name": "string",
  "endpoint": "string", 
  "description": "string (optional)"
}
```

---

## Validation Rules

### Name Validation
- **Required**: Yes
- **Length**: 1-100 characters
- **Pattern**: Letters, numbers, spaces, hyphens, underscores only
- **Regex**: `/^[a-zA-Z0-9\s\-_]+$/`

### Endpoint Validation
- **Required**: Yes
- **Format**: Valid HTTP or HTTPS URL
- **Examples**: 
  - ✅ `https://my-server.com/mcp`
  - ✅ `http://localhost:3000/mcp`
  - ❌ `my-server.com/mcp` (missing protocol)
  - ❌ `ftp://server.com/mcp` (invalid protocol)

### Description Validation
- **Required**: No
- **Type**: String
- **Length**: No specific limit (reasonable length recommended)

---

## Error Handling

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Server created successfully |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Server not found |
| 409 | Conflict | Duplicate endpoint exists |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "error": "Error message",
  "details": ["Detailed error 1", "Detailed error 2"]
}
```

### Common Errors

**Validation Error (400):**
```json
{
  "error": "Validation failed",
  "details": [
    "Name must be between 1 and 100 characters",
    "Endpoint must be a valid URL"
  ]
}
```

**Duplicate Endpoint (409):**
```json
{
  "error": "A server with this endpoint already exists"
}
```

**Server Not Found (404):**
```json
{
  "error": "Server not found"
}
```

**Missing Required Fields (400):**
```json
{
  "error": "Server ID is required"
}
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Create a new server
RESPONSE=$(curl -X POST https://join39.org/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "endpoint": "https://test.com/mcp",
    "description": "Testing the API"
  }')

echo $RESPONSE
# Output: {"success":true,"message":"MCP server submitted successfully","server_id":"687472d4476f071042eb5dfd","name":"Test Agent","endpoint":"https://test.com/mcp"}

# 2. Extract server ID (in a real script, you'd parse JSON)
SERVER_ID="687472d4476f071042eb5dfd"

# 3. Update the server
curl -X PUT https://join39.org/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "'$SERVER_ID'",
    "name": "Updated Test Agent",
    "endpoint": "https://test.com/v2/mcp",
    "description": "Updated via API"
  }'

# 4. List all servers to verify
curl https://join39.org/api/mcp-servers

# 5. Delete the server
curl -X DELETE "https://join39.org/api/mcp-servers?id=$SERVER_ID"
```

### Error Handling Example

```bash
# Try to create with invalid data
curl -X POST https://join39.org/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "",
    "endpoint": "not-a-url"
  }'

# Response:
# {
#   "error": "Validation failed",
#   "details": [
#     "Name must be between 1 and 100 characters",
#     "Endpoint must be a valid URL"
#   ]
# }
```

### Duplicate Prevention Example

```bash
# First submission - succeeds
curl -X POST https://join39.org/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "First Agent",
    "endpoint": "https://example.com/mcp"
  }'

# Second submission with same endpoint - fails
curl -X POST https://join39.org/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Second Agent",
    "endpoint": "https://example.com/mcp"
  }'

# Response: {"error":"A server with this endpoint already exists"}
```

---

## Integration Tips

### Using with JavaScript/Node.js
```javascript
const API_BASE = 'https://join39.org/api/mcp-servers';

async function createServer(name, endpoint, description) {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, endpoint, description })
  });
  return response.json();
}

async function listServers() {
  const response = await fetch(API_BASE);
  return response.json();
}
```

### Using with Python
```python
import requests

API_BASE = 'https://join39.org/api/mcp-servers'

def create_server(name, endpoint, description=None):
    data = {'name': name, 'endpoint': endpoint}
    if description:
        data['description'] = description
    
    response = requests.post(API_BASE, json=data)
    return response.json()

def list_servers():
    response = requests.get(API_BASE)
    return response.json()
```

---

## Support

- **Live API**: https://join39.org/api/mcp-servers
- **Web Interface**: https://join39.org/servers
- **Issues**: Report API issues or request features

---

**Last Updated**: July 2025  
**API Version**: 1.0  
**License**: MIT 
