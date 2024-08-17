from datetime import timedelta
from django.urls import reverse
import pytest

from django.test import Client
from django.utils import timezone
from django.conf import settings

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='not_author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    news = News.objects.create(
        title='Title',
        text='News text',
        # Для будущей логики
        date=timezone.now() - timedelta(days=1)
    )
    return news


@pytest.fixture
def news_kwargs(news) -> dict:
    return {'pk': news.pk, }


@pytest.fixture
def news_detail_url(news_kwargs):
    return reverse('news:detail', kwargs=news_kwargs)


@pytest.mark.django_db
@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Comments text'
    )
    return comment


@pytest.fixture
def comment_data():
    return {'text': 'New comments text'}


@pytest.fixture
def comment_kwargs(comment):
    return {'pk': comment.pk, }


# Не работает как надо
# @pytest.mark.django_db
@pytest.fixture
def create_max_plus_news(db):
    News.objects.bulk_create(
        [
            News(
                title=f'News {index}',
                text='text',
                date=timezone.now() - timedelta(hours=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )


@pytest.fixture
def create_several_comments(news, author):
    for index in range(4):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Comment {index}'
        )
        comment.created = timezone.now() - timedelta(hours=index)
        comment.save()
