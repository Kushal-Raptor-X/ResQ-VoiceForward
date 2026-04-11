"""Context agent for session-based memory management."""

from collections import defaultdict, deque

# In-memory session storage (fast for MVP)
memory = defaultdict(lambda: deque(maxlen=5))

def update(session_id: str, text: str):
    """Update context with new text for session."""
    memory[session_id].append(text)

def get(session_id: str):
    """Retrieve context history for session."""
    return list(memory[session_id])
