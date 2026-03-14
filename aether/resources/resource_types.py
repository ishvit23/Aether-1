"""Resource type definitions and configuration."""

from __future__ import annotations

# Mapping of resource type name to display properties
RESOURCE_DISPLAY: dict[str, dict[str, str]] = {
    "food": {"char": "F", "color": "green"},
    "material": {"char": "M", "color": "yellow"},
    "mana": {"char": "✦", "color": "blue"},
    "gold": {"char": "G", "color": "bright_yellow"},
}


def get_display_char(resource_name: str) -> str:
    """Get the display character for a resource type.

    Args:
        resource_name: Name of the resource.

    Returns:
        Single character for display.
    """
    return RESOURCE_DISPLAY.get(resource_name, {}).get("char", "?")


def get_display_color(resource_name: str) -> str:
    """Get the display color for a resource type.

    Args:
        resource_name: Name of the resource.

    Returns:
        Color name for rich rendering.
    """
    return RESOURCE_DISPLAY.get(resource_name, {}).get("color", "white")
