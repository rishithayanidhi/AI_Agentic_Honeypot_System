"""
Example curl commands for testing the API
"""

# 1. Health Check
curl -X GET http://localhost:8000/health

# 2. First Message - Bank Fraud Scam
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately by clicking this link: http://fake-bank.com/verify",
      "timestamp": "2026-01-26T10:15:30Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'

# 3. Follow-up Message
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-001",
    "message": {
      "sender": "scammer",
      "text": "Send money to UPI: scammer@paytm to verify your account",
      "timestamp": "2026-01-26T10:17:30Z"
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately.",
        "timestamp": "2026-01-26T10:15:30Z"
      },
      {
        "sender": "user",
        "text": "Why will my account be blocked?",
        "timestamp": "2026-01-26T10:16:30Z"
      }
    ],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'

# 4. Get Session Info
curl -X GET http://localhost:8000/api/session/test-session-001 \
  -H "x-api-key: your-secret-api-key-here"

# 5. Delete Session
curl -X DELETE http://localhost:8000/api/session/test-session-001 \
  -H "x-api-key: your-secret-api-key-here"

# 6. Cleanup Expired Sessions
curl -X POST http://localhost:8000/api/cleanup \
  -H "x-api-key: your-secret-api-key-here"
