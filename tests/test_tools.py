import pytest
from unittest.mock import MagicMock, patch
from tools import github_tools

@pytest.fixture
def mock_github():
    with patch('tools.github_tools.Github') as mock:
        yield mock

def test_list_my_repos(mock_github):
    # Setup mock
    mock_instance = mock_github.return_value
    mock_user = mock_instance.get_user.return_value
    
    # Create mock repos
    repo1 = MagicMock()
    repo1.name = "repo1"
    repo1.description = "desc1"
    repo1.language = "Python"
    repo1.stargazers_count = 10
    repo1.updated_at = "2023-01-01"
    repo1.html_url = "http://github.com/user/repo1"
    
    mock_user.get_repos.return_value = [repo1]
    
    # Run function
    # We need to ensure _github_client is reset or mocked continuously because of the singleton pattern in the tool
    # But since we patch the class `Github`, the `_get_github` function will instantiate our mock.
    # However, `_github_client` global variable might persist.
    # Let's reset it before test.
    github_tools._github_client = None
    
    # Ensure environment variable is mocked if needed, or handle the raises
    with patch.dict(os.environ, {"GITHUB_TOKEN": "fake_token"}):
        results = github_tools.list_my_repos(limit=1)
    
    assert len(results) == 1
    assert results[0]['name'] == "repo1"
    assert results[0]['language'] == "Python"

import os
