import pytest
import app.news_scraper as news_scraper


@pytest.fixture
def mock_no_api_key(monkeypatch):
    """Ensure NEWS_API_KEY is not set."""
    monkeypatch.delenv("NEWS_API_KEY", raising=False)


def test_news_fetching_without_api_key(mock_no_api_key):
    """Test if get_magnificent_seven_news returns an empty list when API key is missing."""
    news = news_scraper.get_magnificent_seven_news()
    assert isinstance(news, list)  # Ensure it returns a list
    assert len(news) == 0  # Should return an empty list if API key is missing