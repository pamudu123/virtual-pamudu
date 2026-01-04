"""
Utility functions for Virtual Pamudu Agent.
"""

import os
import sys
import yaml
import logging
import structlog

def setup_logging():
    """Configure structlog for the application."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() 
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True
    )

def load_shortcut_keys() -> tuple[str, ...]:
    """
    Load valid shortcut keys from the shortcuts.yaml file.
    
    Returns:
        Tuple of shortcut key strings from digital_brain/shortcuts.yaml
    """
    logger = structlog.get_logger()
    shortcuts_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "digital_brain", 
        "shortcuts.yaml"
    )
    try:
        with open(shortcuts_path, "r", encoding="utf-8") as f:
            shortcuts = yaml.safe_load(f)
            return tuple(shortcuts.keys()) if shortcuts else ()
    except Exception as e:
        logger.warning("failed_to_load_shortuts", error=str(e))
        return ("bio", "profile", "contact", "resume", "experience", "education", "skills", "awards", "projects")
