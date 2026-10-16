# API Documentation — SeqPredict REST API

Every response from the SeqPredict REST API follows a unified JSON envelope:
- **Success**: `{ "success": true, "data": { ... } }`
- **Failure**: `{ "success": false, "error": "Error message description.", "error_code": "ERROR_CODE_SNAKE_CASE" }`

---

## Authentication APIs

### 1. Register User
Create a new user account.
- **Endpoint**: `POST /api/auth/register`
- **Authentication**: None
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "username": "zeel",
    "email": "zeel@example.com",
    "password": "strongpassword123",
    "full_name": "Zeel Patel"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "message": "User registered successfully.",
      "user": {
        "id": 1,
        "username": "zeel",
        "email": "zeel@example.com",
        "full_name": "Zeel Patel",
        "role": "user"
      }
    }
  }
  ```
- **Error Status Codes**:
  - `400 Bad Request`: Body parameter missing.
  - `409 Conflict`: `USERNAME_TAKEN` or `EMAIL_TAKEN`.
  - `422 Unprocessable`: Password validation failed.

---

### 2. Login User
Authenticate credentials and obtain a JWT access token.
- **Endpoint**: `POST /api/auth/login`
- **Authentication**: None
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "username": "zeel",
    "password": "strongpassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": 1,
        "username": "zeel",
        "email": "zeel@example.com",
        "full_name": "Zeel Patel",
        "role": "user"
      }
    }
  }
  ```
- **Error Status Codes**:
  - `401 Unauthorized`: `INVALID_CREDENTIALS` (username or password incorrect).

---

### 3. Get Profile
Retrieve details of the logged-in user.
- **Endpoint**: `GET /api/user/profile`
- **Authentication**: Required (JWT Bearer Token)
- **Request Headers**: `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "username": "zeel",
      "email": "zeel@example.com",
      "full_name": "Zeel Patel",
      "role": "user",
      "is_active": true,
      "created_at": "2026-07-16 10:00:00.000000",
      "last_login_at": "2026-07-16 10:05:00.000000"
    }
  }
  ```

---

### 4. Update Profile
Modify email, full name, or password fields.
- **Endpoint**: `PUT /api/user/profile`
- **Authentication**: Required (JWT Bearer Token)
- **Request Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "full_name": "Zeel P. Patel",
    "email": "zeel.new@example.com",
    "password": "newsecurepassword456"
  }
  ```
- **Response (200 OK)**: Returns the updated user profile dict.

---

## Prediction APIs

### 1. Run Prediction
Submit a numerical sequence and receive a prediction.
- **Endpoint**: `POST /api/predict`
- **Authentication**: Optional (saves prediction to user history if token present, guest history if absent)
- **Request Headers**:
  - `Authorization: Bearer <token>` (Optional)
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "sequence": [3, 7, 11, 15, 19],
    "save_to_history": true
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "id": 12,
      "input_sequence": [3.0, 7.0, 11.0, 15.0, 19.0],
      "sequence_length": 5,
      "prediction": {
        "next_term": 23,
        "pattern_type": "arithmetic",
        "sequence_type_label": "Arithmetic Sequence",
        "method_used": "rule",
        "confidence": 1.0,
        "confidence_label": "Very High"
      },
      "explanation": {
        "formula": "t(n) = a + (n−1)d",
        "calculation": "Common difference d = 19.0 − 15.0 = 4.0. Next term = 19.0 + 4.0 = 23.",
        "summary": "The sequence [3.0, 7.0, 11.0, 15.0, 19.0] was deterministically identified as an Arithmetic Sequence by the rule engine."
      },
      "engine_trace": {
        "rule_engine": {
          "ran": true,
          "matched": true,
          "detector": "arithmetic",
          "confidence": 1.0,
          "detectors_tried": ["arithmetic"]
        },
        "ml_engine": {
          "ran": false,
          "reason": "Rule engine confidence ≥ 0.95 — ML not required."
        },
        "resolver": {
          "path_taken": "PATH A — Rule Only (confidence ≥ 0.95)",
          "final_method": "rule",
          "agreement": null
        }
      },
      "meta": {
        "prediction_id": 12,
        "model_version": "N/A",
        "served_from_cache": false,
        "latency_ms": 3,
        "created_at": "2026-07-16T10:10:00Z"
      }
    }
  }
  ```
- **Error Status Codes**:
  - `422 Unprocessable Entity`: `VALIDATION_ERROR` (less than 3 terms, NaN, or non-numeric values).

---

### 2. Submit Prediction Feedback
Submit correctness flag and notes on a prediction record.
- **Endpoint**: `POST /api/predict/<id>/feedback`
- **Authentication**: Optional
- **Request Body**:
  ```json
  {
    "is_correct": true,
    "feedback_notes": "Perfect arithmetic sequence check."
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "message": "Feedback recorded",
      "prediction_id": 12
    }
  }
  ```

---

## History APIs

### 1. Fetch History
Retrieve paginated, filterable prediction history records.
- **Endpoint**: `GET /api/history`
- **Authentication**: Optional
- **Query Parameters**:
  - `page`: Page number (default: `1`)
  - `limit`: Page size, max 200 (default: `20`)
  - `pattern`: Filter by sequence type (e.g. `geometric`)
  - `method`: Filter by prediction source (`rule` or `ml`)
  - `search`: General text query matching sequences or types
  - `sort_by`: Ordering (`newest`, `oldest`, `conf-high`, `conf-low`)
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "records": [
        {
          "id": 12,
          "input_sequence": [3.0, 7.0, 11.0, 15.0, 19.0],
          "predicted_next": 23,
          "pattern_type": "arithmetic",
          "method_used": "rule",
          "confidence": 1.0,
          "created_at": "2026-07-16 10:10:00.000000"
        }
      ],
      "total_records": 1,
      "page": 1,
      "limit": 20,
      "total_pages": 1
    }
  }
  ```

---

### 2. Delete History Item
Delete a single prediction history record.
- **Endpoint**: `DELETE /api/history/<prediction_id>`
- **Authentication**: Optional (respects owner isolation rules)
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "message": "Record deleted",
      "id": 12
    }
  }
  ```

---

### 3. Clear All History
Flush the entire history store.
- **Endpoint**: `DELETE /api/history`
- **Authentication**: Optional (clears current logged-in user records, or all guest records if unauthenticated)
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "message": "History cleared successfully.",
      "deleted_count": 15
    }
  }
  ```

---

## Status Codes & Error Handling

The application uses standard HTTP status codes in union with localized application-level error codes inside the JSON envelope:

| HTTP Status | Error Code | Description |
| :--- | :--- | :--- |
| **400 Bad Request** | `BAD_REQUEST` | Malformed JSON request body or syntax error. |
| **401 Unauthorized** | `UNAUTHORISED` | Authorization header missing or token expired. |
| **403 Forbidden** | `FORBIDDEN` | Admin-only role check or file permissions block. |
| **404 Not Found** | `NOT_FOUND` | URL endpoint or database ID not found. |
| **409 Conflict** | `CONFLICT` | Key constraint violation (e.g. username taken). |
| **422 Unprocessable** | `VALIDATION_ERROR` | Schema validation check failed (e.g. too few terms). |
| **500 Server Error** | `INTERNAL_ERROR` | Unhandled database or prediction engine runtime crash. |
