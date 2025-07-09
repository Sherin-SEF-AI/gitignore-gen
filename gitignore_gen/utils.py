"""Utility functions for gitignore-gen."""

import logging
import os
from pathlib import Path
from typing import Optional

import toml
from rich.logging import RichHandler


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Setup logging configuration."""
    if quiet:
        logging.basicConfig(level=logging.ERROR)
        return

    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return Path.home() / ".gitignore-gen.toml"


def load_config() -> dict:
    """Load user configuration."""
    config_path = get_config_path()
    
    if not config_path.exists():
        return {}
    
    try:
        return toml.load(config_path)
    except Exception as e:
        logging.warning(f"Failed to load config: {e}")
        return {}


def save_config(config: dict) -> None:
    """Save user configuration."""
    config_path = get_config_path()
    
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            toml.dump(config, f)
    except Exception as e:
        logging.error(f"Failed to save config: {e}")


def get_cache_dir() -> Path:
    """Get the cache directory for gitignore-gen."""
    cache_dir = Path.home() / ".cache" / "gitignore-gen"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def sanitize_template_name(name: str) -> str:
    """Sanitize template name for API calls."""
    return name.lower().replace(" ", "-").replace("_", "-")


def is_git_repo(path: Path) -> bool:
    """Check if the given path is a Git repository."""
    return (path / ".git").exists() or (path / ".git").is_dir()


def get_git_root(path: Path) -> Optional[Path]:
    """Get the Git root directory."""
    current = path.resolve()
    
    while current != current.parent:
        if is_git_repo(current):
            return current
        current = current.parent
    
    return None


def backup_file(file_path: Path) -> Path:
    """Create a backup of the given file."""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
    
    if file_path.exists():
        import shutil
        shutil.copy2(file_path, backup_path)
    
    return backup_path


def merge_gitignore_content(existing: str, new: str) -> str:
    """Merge existing and new .gitignore content, removing duplicates."""
    existing_lines = set(line.strip() for line in existing.splitlines() if line.strip())
    new_lines = set(line.strip() for line in new.splitlines() if line.strip())
    
    # Combine and sort
    all_lines = sorted(existing_lines | new_lines)
    
    # Remove comments and empty lines for deduplication
    content_lines = [line for line in all_lines if not line.startswith("#") and line]
    
    # Add back comments
    result_lines = []
    for line in all_lines:
        if line.startswith("#"):
            result_lines.append(line)
        elif line in content_lines:
            result_lines.append(line)
            content_lines.remove(line)
    
    return "\n".join(result_lines)


def get_common_security_patterns() -> list[str]:
    """Get common security patterns to ignore."""
    return [
        "# Security patterns",
        "*.key",
        "*.pem",
        "*.p12",
        "*.pfx",
        "*.crt",
        "*.cer",
        "*.der",
        "*.p7b",
        "*.p7c",
        "*.p8",
        "*.p10",
        "*.p15",
        "*.p20",
        "*.p25",
        "*.p30",
        "*.p35",
        "*.p40",
        "*.p45",
        "*.p50",
        "*.p55",
        "*.p60",
        "*.p65",
        "*.p70",
        "*.p75",
        "*.p80",
        "*.p85",
        "*.p90",
        "*.p95",
        "*.p100",
        "*.env",
        "*.env.local",
        "*.env.development",
        "*.env.test",
        "*.env.production",
        "secrets.json",
        "secrets.yaml",
        "secrets.yml",
        "config.json",
        "config.yaml",
        "config.yml",
        "credentials.json",
        "service-account.json",
        "firebase-key.json",
        "google-credentials.json",
        "aws-credentials",
        ".aws/",
        ".ssh/",
        "id_rsa",
        "id_rsa.pub",
        "known_hosts",
        "authorized_keys",
        "*.log",
        "logs/",
        "*.tmp",
        "*.temp",
        "temp/",
        "tmp/",
        "cache/",
        ".cache/",
    ] 