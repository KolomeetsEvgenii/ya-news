from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, detail_url):
    form_data = {'text': 'Текст комментария'}

    comments_before = Comment.objects.count()
    client.post(detail_url, data=form_data)
    comments_after = Comment.objects.count()

    assert comments_after == comments_before


def test_user_can_create_comment(author_client, author, news, detail_url):
    form_data = {'text': 'Текст комментария'}

    existing_pks = set(Comment.objects.values_list('pk', flat=True))

    response = author_client.post(detail_url, data=form_data)

    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == len(existing_pks) + 1

    created_comment = Comment.objects.exclude(pk__in=existing_pks).get()
    assert created_comment.text == form_data['text']
    assert created_comment.news == news
    assert created_comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}

    comments_before = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_words_data)
    comments_after = Comment.objects.count()

    form = response.context['form']
    assert form.errors['text'] == [WARNING]
    assert comments_after == comments_before


def test_author_can_delete_comment(
        author_client,
        delete_url, detail_url,
        comment
):
    comments_before = Comment.objects.count()

    response = author_client.delete(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comments_before - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        delete_url, comment
):
    comments_before = Comment.objects.count()
    comment_state_before = {
        'pk': comment.pk,
        'text': comment.text,
        'author_id': comment.author_id,
        'news_id': comment.news_id,
        'created': comment.created,
    }

    response = not_author_client.delete(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before

    comment_state_after = Comment.objects.values(
        'pk', 'text', 'author_id', 'news_id', 'created'
    ).get(pk=comment.pk)
    assert comment_state_after == comment_state_before


def test_author_can_edit_comment(author_client, edit_url, detail_url, comment):
    form_data = {'text': 'Обновлённый комментарий'}
    comments_before = Comment.objects.count()

    response = author_client.post(edit_url, data=form_data)

    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comments_before

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        edit_url, comment
):
    form_data = {'text': 'Обновлённый комментарий'}
    comments_before = Comment.objects.count()
    comment_state_before = {
        'pk': comment.pk,
        'text': comment.text,
        'author_id': comment.author_id,
        'news_id': comment.news_id,
        'created': comment.created,
    }

    response = not_author_client.post(edit_url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before

    comment_state_after = Comment.objects.values(
        'pk', 'text', 'author_id', 'news_id', 'created'
    ).get(pk=comment.pk)
    assert comment_state_after == comment_state_before
