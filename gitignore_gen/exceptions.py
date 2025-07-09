"""Custom exceptions for gitignore-gen."""


class GitignoreGenError(Exception):
    """Base exception for gitignore-gen errors."""
    pass


class DetectionError(GitignoreGenError):
    """Raised when technology detection fails."""
    pass


class TemplateError(GitignoreGenError):
    """Raised when template operations fail."""
    pass


class APIError(GitignoreGenError):
    """Raised when API calls fail."""
    pass


class GitError(GitignoreGenError):
    """Raised when Git operations fail."""
    pass


class ConfigurationError(GitignoreGenError):
    """Raised when configuration is invalid."""
    pass 