# Data Privacy & Storage Architecture

## Zero Browser Storage Policy

**VoiceForward does NOT store any data in the browser.**

### What We DON'T Use:
- ❌ `localStorage` - Never used
- ❌ `sessionStorage` - Never used  
- ❌ `IndexedDB` - Never used
- ❌ Cookies (except session cookies for authentication if implemented)
- ❌ Service Workers with caching
- ❌ Browser cache for sensitive data

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│  • In-memory state only (cleared on page refresh)          │
│  • Session data cleared when call ends                     │
│  • All persistent data fetched from backend API            │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                         │
│  • Real-time analysis via Socket.io                        │
│  • REST API for historical data                            │
│  • Logs all calls to MongoDB/in-memory store               │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│              STORAGE (MongoDB Atlas)                        │
│  • Call logs with full audit trail                         │
│  • AI reasoning chains (Layer 5 compliance)                │
│  • Operator actions (accept/modify/reject)                 │
│  • No caller PII beyond session                            │
└─────────────────────────────────────────────────────────────┘
```

## Session Data Lifecycle

### During Active Call:
1. **Transcript** - Stored in React state, streamed from backend via WebSocket
2. **Analysis** - Updated in real-time, stored in React state
3. **Audit Log** - Operator actions logged to backend immediately

### When Call Ends:
1. All React state is cleared
2. Socket connection closed
3. No data remains in browser memory
4. Historical data must be fetched from backend

### Page Refresh:
- All session data is lost (by design)
- User must start a new call
- Historical data fetched from backend API

## DPDPA 2023 Compliance

### Privacy by Design:
- **No PII in browser**: Caller information never stored client-side
- **Session-only data**: Transcript exists only during active call
- **Right to erasure**: Backend can purge all call data on request
- **Audit trail**: All AI decisions logged immutably in backend

### Data Minimization:
- Frontend only holds data needed for current session
- No caching of historical calls in browser
- No predictive pre-loading of sensitive data

## Developer Guidelines

### ✅ DO:
- Use React state for current session data
- Fetch historical data from backend API on demand
- Clear state when call ends
- Send operator actions to backend immediately

### ❌ DON'T:
- Use `localStorage.setItem()` for any data
- Cache sensitive data in browser
- Store transcript or analysis results locally
- Implement offline mode with local storage

## Verification

To verify no browser storage is used:

```bash
# Search for localStorage usage
grep -r "localStorage" frontend/src/

# Search for sessionStorage usage  
grep -r "sessionStorage" frontend/src/

# Search for IndexedDB usage
grep -r "IndexedDB\|indexedDB" frontend/src/
```

All searches should return no results (except this documentation file).

## Backend API Endpoints

### Real-time (WebSocket):
- `ws://localhost:8000` - Live transcript and analysis

### REST API:
- `GET /calls` - Fetch call history
- `GET /calls/{id}` - Get specific call details
- `DELETE /calls/{id}` - Delete call log
- `DELETE /calls` - Delete all calls (admin only)
- `POST /calls/{id}/action` - Update operator action

## Security Considerations

1. **No XSS risk from stored data**: Since we don't store data in browser, XSS attacks can't access historical sensitive data
2. **No CSRF on storage**: No client-side storage means no CSRF attacks on stored data
3. **Session hijacking limited**: Even if session is hijacked, attacker only gets current call data, not historical
4. **Compliance audit trail**: All data access logged in backend, not client

## Future Considerations

If offline mode is ever required:
1. Use encrypted IndexedDB with user consent
2. Implement automatic purge on session end
3. Add explicit "Clear All Data" button
4. Document in privacy policy
5. Require explicit user opt-in

**Current status: Offline mode NOT implemented. All data is server-side.**
