from django.urls import reverse
import pytest

from django.conf import settings

from news.forms import CommentForm


@pytest.mark.usefixtures('create_max_plus_news')
def test_count_and_order_news_on_homepage(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    count = object_list.count()
    assert count == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in object_list]
    sorted_date = sorted(all_dates, reverse=True)
    assert all_dates == sorted_date


@pytest.mark.usefixtures('create_several_comments')
def test_order_comments(client, news_detail_url):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    '_client, must_be',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    )
)
def test_form_exist(_client, must_be, news_detail_url):
    response = _client.get(news_detail_url)
    assert ('form' in response.context) == must_be
    if must_be:
        assert isinstance(response.context['form'], CommentForm)
