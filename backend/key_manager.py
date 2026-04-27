"""
Sarvam API Key Rotation Manager

Automatically rotates through API keys:
1. First uses SARVAM_API_KEY_1 (new key 1)
2. Then SARVAM_API_KEY_2 (new key 2)
3. Finally SARVAM_API_KEY_3 (current key as fallback)

Seamlessly switches when a key is rate-limited or exhausted.
"""
import logging
import os
from typing import Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class KeyStatus(Enum):
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    RATE_LIMITED = "rate_limited"
    INVALID = "invalid"


@dataclass
class APIKey:
    key: str
    name: str
    status: KeyStatus = KeyStatus.ACTIVE
    usage_count: int = 0
    last_error: Optional[str] = None


class KeyManager:
    """
    Manages multiple API keys with automatic rotation and fallback.
    
    Priority order: key1 → key2 → key3
    Keys are marked as exhausted after rate limit (429) errors.
    """
    
    def __init__(self):
        self.keys: list[APIKey] = []
        self.current_index: int = 0
        self._initialize_keys()
    
    def _initialize_keys(self):
        """Load and validate all API keys from environment."""
        # Priority order: new keys first, current key as fallback
        key_configs = [
            ("SARVAM_API_KEY_1", "Key 1 (New)"),
            ("SARVAM_API_KEY_2", "Key 2 (New)"),
            ("SARVAM_API_KEY_3", "Key 3 (Current)"),
        ]
        
        for env_var, name in key_configs:
            key_value = os.getenv(env_var, "").strip()
            
            if key_value and not key_value.startswith("PASTE_"):
                api_key = APIKey(
                    key=key_value,
                    name=name,
                    status=KeyStatus.ACTIVE
                )
                self.keys.append(api_key)
                logger.info(f"Loaded {name}: ...{key_value[-8:]}")
            else:
                logger.info(f"Skipping {name}: not configured or placeholder")
        
        if not self.keys:
            logger.warning("No valid Sarvam API keys found!")
        else:
            logger.info(f"KeyManager initialized with {len(self.keys)} active keys")
    
    def get_current_key(self) -> Optional[APIKey]:
        """Get the current active API key."""
        if not self.keys:
            return None
        
        # Find next active key starting from current index
        for i in range(len(self.keys)):
            idx = (self.current_index + i) % len(self.keys)
            if self.keys[idx].status == KeyStatus.ACTIVE:
                self.current_index = idx
                return self.keys[idx]
        
        # All keys exhausted, return current anyway (will fail gracefully)
        return self.keys[self.current_index] if self.keys else None
    
    def get_current_key_value(self) -> Optional[str]:
        """Get the current API key value for API calls."""
        key = self.get_current_key()
        return key.key if key else None
    
    def mark_error(self, error_type: KeyStatus, error_message: str = ""):
        """Mark the current key with an error status."""
        if not self.keys:
            return
        
        current_key = self.keys[self.current_index]
        current_key.status = error_type
        current_key.last_error = error_message
        current_key.usage_count += 1
        
        logger.warning(
            f"{current_key.name} marked as {error_type.value}: {error_message}"
        )
        
        # Move to next key if this one is exhausted or rate-limited
        if error_type in (KeyStatus.EXHAUSTED, KeyStatus.RATE_LIMITED):
            self._move_to_next_key()
    
    def mark_success(self):
        """Mark current key usage as successful."""
        if not self.keys:
            return
        
        current_key = self.keys[self.current_index]
        current_key.usage_count += 1
        current_key.last_error = None
    
    def _move_to_next_key(self):
        """Move to the next available key."""
        if not self.keys:
            return
        
        # Try to find next active key
        original_index = self.current_index
        found = False
        
        for i in range(1, len(self.keys)):
            idx = (self.current_index + i) % len(self.keys)
            if self.keys[idx].status == KeyStatus.ACTIVE:
                self.current_index = idx
                found = True
                break
        
        if found:
            next_key = self.keys[self.current_index]
            logger.info(f"Rotated to {next_key.name}")
        else:
            logger.error("All API keys exhausted or unavailable!")
    
    def get_status(self) -> dict:
        """Get status of all keys for debugging."""
        return {
            "current_key": self.keys[self.current_index].name if self.keys else None,
            "total_keys": len(self.keys),
            "keys": [
                {
                    "name": k.name,
                    "status": k.status.value,
                    "usage_count": k.usage_count,
                    "key_preview": f"...{k.key[-8:]}" if k.key else None
                }
                for k in self.keys
            ]
        }
    
    def reset_all(self):
        """Reset all keys to ACTIVE status (useful for new sessions)."""
        for key in self.keys:
            key.status = KeyStatus.ACTIVE
            key.last_error = None
        self.current_index = 0
        logger.info("All keys reset to ACTIVE")


# Global key manager instance
key_manager = KeyManager()


def get_sarvam_key() -> Optional[str]:
    """Convenience function to get current API key."""
    return key_manager.get_current_key_value()


def report_key_error(error_type: KeyStatus, error_message: str = ""):
    """Report an error for the current key."""
    key_manager.mark_error(error_type, error_message)


def report_key_success():
    """Report successful usage of current key."""
    key_manager.mark_success()