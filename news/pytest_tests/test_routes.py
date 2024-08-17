from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    '_client, name, kwargs, http_status',
    (
        (pytest.lazy_fixture('client'), 'users:login', None, HTTPStatus.OK),
        (pytest.lazy_fixture('client'), 'users:logout', None, HTTPStatus.OK),
        (pytest.lazy_fixture('client'), 'users:signup', None, HTTPStatus.OK),

        (pytest.lazy_fixture('client'), 'news:home', None, HTTPStatus.OK),
        (pytest.lazy_fixture('client'), 'news:detail',
            pytest.lazy_fixture('news_kwargs'), HTTPStatus.OK),

        (pytest.lazy_fixture('author_client'), 'news:edit',
            pytest.lazy_fixture('comment_kwargs'), HTTPStatus.OK),
        (pytest.lazy_fixture('author_client'), 'news:delete',
            pytest.lazy_fixture('comment_kwargs'), HTTPStatus.OK),

        (pytest.lazy_fixture('not_author_client'), 'news:edit',
            pytest.lazy_fixture('comment_kwargs'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('not_author_client'), 'news:delete',
            pytest.lazy_fixture('comment_kwargs'), HTTPStatus.NOT_FOUND),
    )
)
def test_pages_status_code(_client, name, kwargs, http_status):
    url = reverse(name, kwargs=kwargs)
    response = _client.get(url)
    assert response.status_code == http_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirects_for_anonymous(client, name, comment_kwargs):
    url = reverse(name, kwargs=comment_kwargs)
    expected_url = reverse('users:login') + '?next=' + url
    response = client.get(url)
    assertRedirects(response, expected_url)
