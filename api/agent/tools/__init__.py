"""Tools available to the Virtual Pamudu agent."""

from .contact import send_message_to_pamudu
from .github import get_repo_file, get_repo_readme, list_github_repos, search_github_repos
from .medium import list_medium_articles, read_medium_article, search_medium_articles
from .ui import (
    ask_visitor,
    show_contact_card,
    show_profile_section,
    show_quick_actions,
    show_role_fit,
    show_stats,
    suggest_followups,
)
from .youtube import get_video_transcript, list_youtube_videos, search_youtube_videos

__all__ = [
    "ask_visitor",
    "get_repo_file",
    "get_repo_readme",
    "get_video_transcript",
    "list_github_repos",
    "list_medium_articles",
    "list_youtube_videos",
    "read_medium_article",
    "search_github_repos",
    "search_medium_articles",
    "search_youtube_videos",
    "send_message_to_pamudu",
    "show_contact_card",
    "show_profile_section",
    "show_quick_actions",
    "show_role_fit",
    "show_stats",
    "suggest_followups",
]
