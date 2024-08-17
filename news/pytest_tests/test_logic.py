import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from news.forms import BAD_WORDS, WARNING

from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cant_create_comment(client, news_detail_url, comment_data):
    client.post(
        news_detail_url,
        data=comment_data)
    comment_count = Comment.objects.count()
    assert comment_count == 0


@pytest.mark.django_db
def test_auth_user_can_create_comment(
        author, author_client, news, news_detail_url, comment_data):
    response = author_client.post(news_detail_url, data=comment_data)
    comment_count = Comment.objects.count()
    assertRedirects(response, (news_detail_url + '#comments'))
    assert comment_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_bad_words_in_comment(author_client, news_detail_url):
    data = {'text': f'text before {BAD_WORDS[0]} after', }
    response = author_client.post(news_detail_url, data=data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING)
    comment_count = Comment.objects.count()
    assert comment_count == 0


@pytest.mark.usefixtures('comment')
@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment_kwargs, comment_data):
    author_client.post(
        reverse('news:edit', kwargs=comment_kwargs),
        data=comment_data)
    comment = Comment.objects.get()
    assert comment.text == comment_data['text']


@pytest.mark.usefixtures('comment')
@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment_kwargs):
    author_client.delete(reverse('news:delete', kwargs=comment_kwargs))
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_edit_comment(
        not_author_client, comment_kwargs, comment_data, comment):
    response = not_author_client.post(
        reverse('news:edit', kwargs=comment_kwargs),
        data=comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get()
    assert new_comment.text == comment.text


@pytest.mark.usefixtures('comment')
@pytest.mark.django_db
def test_user_cant_delete_comment(not_author_client, comment_kwargs):
    response = not_author_client.delete(
        reverse('news:delete', kwargs=comment_kwargs))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
