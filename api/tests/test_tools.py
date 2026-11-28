"""Unit tests for the agent's tools. Network calls are mocked."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import feedparser

from agent.tools import contact, github, medium, ui, youtube


def _repo(name: str, description: str):
    return SimpleNamespace(
        name=name,
        description=description,
        language="Python",
        stargazers_count=3,
        updated_at=datetime(2026, 1, 2),
        html_url=f"https://github.com/pamudu123/{name}",
    )


def test_list_github_repos_returns_card_fields():
    client = MagicMock()
    client.get_user.return_value.get_repos.return_value = [_repo("chess-eye", "Chessboard vision")]
    with patch.object(github, "_client", return_value=client):
        result = github.list_github_repos.invoke({"limit": 5})
    assert result["repos"] == [
        {
            "name": "chess-eye",
            "description": "Chessboard vision",
            "language": "Python",
            "stars": 3,
            "updated": "2026-01-02",
            "url": "https://github.com/pamudu123/chess-eye",
        }
    ]


def test_search_github_repos_ranks_matches():
    client = MagicMock()
    client.get_user.return_value.get_repos.return_value = [
        _repo("notes", "misc"),
        _repo("chess-eye", "Chessboard vision"),
    ]
    with patch.object(github, "_client", return_value=client):
        result = github.search_github_repos.invoke({"keywords": ["chess"]})
    assert [r["name"] for r in result["repos"]] == ["chess-eye"]


def test_github_errors_are_returned_not_raised():
    with patch.object(github, "_client", side_effect=RuntimeError("boom")):
        result = github.list_github_repos.invoke({})
    assert "error" in result


MEDIUM_FEED = """<?xml version="1.0"?><rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel><item><title>Agentic RAG in practice</title>
<link>https://medium.com/@pamudu1111/agentic-rag-1?source=rss</link>
<pubDate>Mon, 05 Jan 2026 10:00:00 GMT</pubDate><category>rag</category>
<content:encoded><![CDATA[<img src="https://img/x.png"/><p>Evaluating retrieval agents.</p>]]></content:encoded>
</item></channel></rss>"""


def test_medium_list_and_read_share_clean_urls():
    entries = feedparser.parse(MEDIUM_FEED).entries
    with patch.object(medium, "_entries", return_value=entries):
        listed = medium.list_medium_articles.invoke({})["articles"]
        read = medium.read_medium_article.invoke({"url": listed[0]["url"]})
    assert listed[0]["url"] == "https://medium.com/@pamudu1111/agentic-rag-1"
    assert listed[0]["image"] == "https://img/x.png"
    assert "Evaluating retrieval agents." in read["content"]


def test_medium_read_rejects_foreign_urls():
    entries = feedparser.parse(MEDIUM_FEED).entries
    with patch.object(medium, "_entries", return_value=entries):
        result = medium.read_medium_article.invoke({"url": "https://example.com/evil"})
    assert "error" in result


def test_youtube_list_builds_thumbnail():
    entry = {"title": "YOLOv9", "yt_videoid": "abc123", "link": "https://youtu.be/abc123", "published": "2024"}
    with patch.object(youtube, "_entries", return_value=[entry]):
        video = youtube.list_youtube_videos.invoke({})["videos"][0]
    assert video["thumbnail"] == "https://i.ytimg.com/vi/abc123/hqdefault.jpg"


def test_contact_card_reads_profile_links():
    card = ui.show_contact_card.invoke({})
    assert card["name"] == "Pamudu Ranasinghe"
    assert card["links"]["github"].startswith("https://github.com/")


def test_send_message_always_goes_to_pamudu(monkeypatch):
    monkeypatch.setenv("BREVO_API_KEY", "k")
    monkeypatch.setenv("CONTACT_RECIPIENT_EMAIL", "owner@example.com")
    with patch.object(contact.httpx, "post") as post:
        post.return_value.is_error = False
        result = contact.send_message_to_pamudu.invoke(
            {
                "sender_name": "Ada <b>",
                "sender_email": "ada@example.com",
                "subject": "Hello",
                "message": "Hi\n<script>x</script>",
            }
        )
    payload = post.call_args.kwargs["json"]
    assert result["sent"] is True
    assert payload["to"] == [{"email": "owner@example.com", "name": "Pamudu"}]
    assert payload["replyTo"]["email"] == "ada@example.com"
    assert "<script>" not in payload["htmlContent"]


def test_send_message_without_api_key_reports_error(monkeypatch):
    monkeypatch.delenv("BREVO_API_KEY", raising=False)
    result = contact.send_message_to_pamudu.invoke(
        {"sender_name": "A", "sender_email": "a@b.co", "subject": "s", "message": "m"}
    )
    assert "error" in result


def test_send_message_reports_a_rejection_without_leaking_details(monkeypatch):
    monkeypatch.setenv("BREVO_API_KEY", "k")
    with patch.object(contact.httpx, "post") as post:
        post.return_value.is_error = True
        post.return_value.status_code = 401
        post.return_value.text = '{"message":"Key not found","code":"unauthorized"}'
        result = contact.send_message_to_pamudu.invoke(
            {"sender_name": "A", "sender_email": "a@b.co", "subject": "s", "message": "m"}
        )
    assert result["sent"] is False
    assert "Nothing was sent" in result["error"]
    assert "Key not found" not in result["error"]


def test_send_message_needs_a_name_and_a_real_email(monkeypatch):
    monkeypatch.setenv("BREVO_API_KEY", "k")
    with patch.object(contact.httpx, "post") as post:
        for args in (
            {"sender_name": "", "sender_email": "a@b.co", "subject": "s", "message": "m"},
            {"sender_name": "A", "sender_email": "not-an-email", "subject": "s", "message": "m"},
            {"sender_name": "A", "sender_email": "a@b.co", "subject": "s", "message": "  "},
        ):
            assert contact.send_message_to_pamudu.invoke(args)["sent"] is False
    post.assert_not_called()


def test_quick_actions_use_fixed_prompts_and_profile_links():
    result = ui.show_quick_actions.invoke({"actions": ["message", "github", "message", "linkedin"]})
    actions = result["actions"]
    assert [a["id"] for a in actions] == ["message", "github", "linkedin"]
    assert actions[0]["kind"] == "prompt" and "message" in actions[0]["prompt"]
    assert actions[1] == {
        "id": "github",
        "kind": "link",
        "label": "View GitHub",
        "href": "https://github.com/pamudu123",
    }


def test_stats_and_role_fit_only_acknowledge():
    stats = ui.show_stats.invoke(
        {"heading": "Impact", "stats": [{"value": "10M+", "label": "daily interactions"}]}
    )
    assert "1 stat tile" in stats
    fit = ui.show_role_fit.invoke(
        {
            "role": "ML Engineer",
            "strong": [{"requirement": "Python", "evidence": "Used across his roles."}],
            "partial": [],
            "gaps": ["Kubernetes"],
            "summary": "Strong on ML, lighter on infrastructure.",
        }
    )
    assert "1 strong" in fit and "1 not covered" in fit
