# Project Architecture

## Overview

The AI Agentic Honeypot System is designed with a modular architecture to detect scams, engage scammers autonomously, and extract intelligence.

```
┌─────────────────────────────────────────────────────────────┐
│                      External Systems                       │
│  ┌──────────────┐      ┌──────────────┐   ┌──────────────┐│
│  │   Platform   │      │     LLM      │   │     GUVI     ││
│  │ (sends msgs) │      │ (OpenAI/     │   │  (receives   ││
│  │              │      │  Anthropic)  │   │   results)   ││
│  └──────────────┘      └──────────────┘   └──────────────┘│
└─────────────────────────────────────────────────────────────┘
         │                       │                    ▲
         │ POST /api/message     │ API Calls          │ POST callback
         │                       │                    │
         ▼                       ▼                    │
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                           │
│  ┌────────────────────────────────────────────────────────┐│
│  │              FastAPI Application (main.py)             ││
│  │  - Authentication (API Key)                            ││
│  │  - Request/Response handling                           ││
│  │  - CORS middleware                                     ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Session Manager  │  │ Scam Detector│  │    AI Agent      │
│                  │  │              │  │                  │
│ - Track sessions │  │ - LLM-based  │  │ - Persona        │
│ - State mgmt     │  │   detection  │  │   selection      │
│ - Timeouts       │  │ - Confidence │  │ - Response gen   │
│ - Cleanup        │  │   scoring    │  │ - Multi-turn     │
└──────────────────┘  └──────────────┘  └──────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                         │
         ▼                                         ▼
┌──────────────────────┐                ┌──────────────────┐
│ Intelligence         │                │ GUVI Callback    │
│ Extractor            │                │                  │
│                      │                │ - Format data    │
│ - Regex patterns     │                │ - Send results   │
│ - Bank accounts      │                │ - Error handling │
│ - UPI IDs            │                │                  │
│ - Phone numbers      │                └──────────────────┘
│ - URLs               │
│ - Keywords           │
└──────────────────────┘
```

## Component Details

### 1. API Layer (main.py)

**Responsibilities:**

- Handle HTTP requests/responses
- API key authentication
- Route incoming messages
- Orchestrate services
- Error handling

**Key Endpoints:**

- `POST /api/message` - Main message handling
- `GET /health` - Health check
- `GET /api/session/{id}` - Session info
- `DELETE /api/session/{id}` - Delete session
- `POST /api/cleanup` - Cleanup expired sessions

### 2. Session Manager

**Responsibilities:**

- Track conversation state across multiple messages
- Store session metadata
- Handle timeouts
- Cleanup expired sessions

**Data Stored:**

- Session ID
- Message history
- Scam detection status
- Extracted intelligence
- Agent persona
- Timestamps

### 3. Scam Detector

**Responsibilities:**

- Analyze messages for scam indicators
- Determine scam type
- Calculate confidence score
- Provide reasoning

**Detection Methods:**

1. **LLM-based** (primary): Uses GPT-4 or Claude for intelligent detection
2. **Keyword-based** (fallback): Pattern matching for reliability

**Scam Types Detected:**

- Bank fraud
- UPI fraud
- Phishing
- Fake offers
- Other

### 4. AI Agent

**Responsibilities:**

- Select appropriate persona
- Generate human-like responses
- Maintain believable conversation
- Extract intelligence through questions
- Decide when to end conversation

**Personas:**

1. **Cautious User**: Asks many questions, tech-unsavvy
2. **Eager Victim**: Willing but needs guidance
3. **Confused Elderly**: Needs simple explanations
4. **Busy Professional**: Wants quick solutions

**Conversation Stages:**

1. **Early** (1-5 msgs): Express concern, ask questions
2. **Middle** (6-15 msgs): Show willingness, gather details
3. **Late** (16+ msgs): Final extraction or disengage

### 5. Intelligence Extractor

**Responsibilities:**

- Extract structured data from messages
- Use regex patterns for detection
- Merge intelligence across messages
- Deduplicate results

**Extraction Patterns:**

- **Bank Accounts**: `\b\d{9,18}\b`
- **UPI IDs**: `[\w\.-]+@[\w\.-]+` (filtered for UPI providers)
- **Phone Numbers**: `\+?\d{10,15}`
- **URLs**: Standard HTTP/HTTPS pattern
- **Keywords**: Predefined scam indicator list

### 6. GUVI Callback

**Responsibilities:**

- Format final results
- Send to GUVI endpoint
- Handle errors and retries
- Log callback status

**When Triggered:**

- Scam confirmed
- Conversation ends (timeout, max messages, or sufficient intel)
- Intelligence extraction complete

## Data Flow

### Message Processing Flow

```
1. Message arrives → POST /api/message
                     │
2. Authenticate   → Check API key
                     │
3. Get/Create     → Session Manager
   Session           │
                     │
4. Extract Intel  → Intelligence Extractor
                     │
5. Detect Scam    → Scam Detector (LLM)
   (if needed)       │
                     │
6. Generate       → AI Agent
   Response          │
   (if scam)         │
                     │
7. Update         → Session Manager
   Session           │
                     │
8. Check End      → Should conversation end?
   Condition         │
                     ├─ No → Return response
                     │
                     └─ Yes → Send GUVI callback
                               │
                               └─ Return final response
```

### Session Lifecycle

```
Create Session
     │
     ▼
┌─────────────────────┐
│  Initial Message    │
│  - Detect scam      │
│  - Activate agent   │
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  Engagement Phase   │◄──┐
│  - Agent responds   │   │
│  - Extract intel    │   │
│  - Update session   │   │
└─────────────────────┘   │
     │                    │
     ├─ More messages ────┘
     │
     ▼
┌─────────────────────┐
│   End Conditions    │
│  - Max messages     │
│  - Sufficient intel │
│  - Timeout          │
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  GUVI Callback      │
│  - Send results     │
│  - Mark complete    │
└─────────────────────┘
```

## Configuration

### Environment Variables

```
API_KEY              → System authentication
OPENAI_API_KEY       → LLM provider (option 1)
ANTHROPIC_API_KEY    → LLM provider (option 2)
LLM_PROVIDER         → Choose: openai or anthropic
PORT                 → Server port
SESSION_TIMEOUT      → Session expiry time
MAX_MESSAGES         → Max messages per session
GUVI_CALLBACK_URL    → Results endpoint
```

### Settings Hierarchy

```
.env file → config.py → Services
```

## Error Handling

### Fallback Mechanisms

1. **LLM Failure**
   - Scam Detector → Keyword-based detection
   - AI Agent → Predefined responses

2. **Network Failure**
   - GUVI Callback → Retry logic + logging

3. **Session Issues**
   - Auto-cleanup on timeout
   - Graceful degradation

### Logging

```
INFO  → Normal operations
WARN  → Recoverable issues
ERROR → Critical failures
DEBUG → Detailed tracing
```

## Performance Considerations

### Optimization Strategies

1. **Caching**: Cache similar scam detections
2. **Rate Limiting**: Prevent abuse
3. **Concurrent Processing**: Multiple sessions in parallel
4. **Session Cleanup**: Regular cleanup of expired sessions
5. **Connection Pooling**: Reuse HTTP connections

### Scalability

**Horizontal Scaling:**

- Stateless API design
- Redis for shared sessions
- Load balancer distribution

**Vertical Scaling:**

- More CPU for concurrent LLM calls
- More RAM for session storage

## Security

### Authentication

- API key in header: `x-api-key`
- Secret key in environment variables

### Data Protection

- No persistence of sensitive data
- Session cleanup after timeout
- Secure communication (HTTPS in prod)

### Rate Limiting

- Per-IP limits
- Per-session limits
- API key validation

## Testing Strategy

### Unit Tests

- Individual component testing
- Mock LLM responses
- Pattern matching validation

### Integration Tests

- End-to-end message flow
- Session lifecycle
- GUVI callback

### Scenario Tests

- Bank fraud scenario
- Phishing scenario
- Multi-turn conversation

## Deployment Architecture

### Development

```
Local Machine
├── Python app
├── In-memory sessions
└── Direct LLM calls
```

### Production

```
Load Balancer
    │
    ├─ App Instance 1 ─┐
    ├─ App Instance 2 ─┼─→ Redis (sessions)
    └─ App Instance 3 ─┘
         │
         └─→ LLM API (OpenAI/Anthropic)
```

## Future Enhancements

1. **Database Integration**: PostgreSQL for persistence
2. **Advanced Analytics**: Track scam patterns
3. **Machine Learning**: Custom scam detection models
4. **Real-time Dashboard**: Monitor active sessions
5. **Multi-language Support**: Detect scams in multiple languages
6. **Webhook Support**: Notify external systems
7. **Advanced Personas**: More sophisticated role-playing
8. **Conversation Summarization**: Auto-generate reports
