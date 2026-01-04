"""
Utility functions for Virtual Pamudu Agent.
"""

import os
import yaml


def load_shortcut_keys() -> tuple[str, ...]:
    """
    Load valid shortcut keys from the shortcuts.yaml file.
    
    Returns:
        Tuple of shortcut key strings from digital_brain/shortcuts.yaml
    """
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
        print(f"Warning: Could not load shortcuts.yaml: {e}")
        return ("bio", "profile", "contact", "resume", "experience", "education", "skills", "awards", "projects")
