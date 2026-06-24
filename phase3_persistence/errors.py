"""Persistence-layer exceptions."""


class PersistenceError(RuntimeError):
    """Raised when persisted state cannot be saved or restored."""
